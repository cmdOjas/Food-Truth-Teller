import {createSlice, createAsyncThunk, PayloadAction} from '@reduxjs/toolkit';
import {chatApi} from '../../services/api';
import {ChatState, ChatMessage, Conversation} from '../../types';

const initialState: ChatState = {
  conversations: [],
  currentConversationId: null,
  messages: [],
  isStreaming: false,
  error: null,
};

export const fetchHistory = createAsyncThunk('chat/fetchHistory', async (_, {rejectWithValue}) => {
  try {
    const res = await chatApi.getHistory();
    return res.data as Conversation[];
  } catch (err: any) {
    return rejectWithValue(err.response?.data?.error ?? 'Failed to load history');
  }
});

export const fetchConversation = createAsyncThunk(
  'chat/fetchConversation',
  async (id: number, {rejectWithValue}) => {
    try {
      const res = await chatApi.getConversation(id);
      return res.data as {conversation: Conversation; messages: ChatMessage[]};
    } catch (err: any) {
      return rejectWithValue(err.response?.data?.error ?? 'Failed to load conversation');
    }
  },
);

export const deleteConversation = createAsyncThunk(
  'chat/deleteConversation',
  async (id: number, {rejectWithValue}) => {
    try {
      await chatApi.deleteConversation(id);
      return id;
    } catch (err: any) {
      return rejectWithValue(err.response?.data?.error ?? 'Delete failed');
    }
  },
);

export const deleteAllHistory = createAsyncThunk('chat/deleteAllHistory', async (_, {rejectWithValue}) => {
  try {
    await chatApi.deleteAllHistory();
  } catch (err: any) {
    return rejectWithValue(err.response?.data?.error ?? 'Delete failed');
  }
});

const chatSlice = createSlice({
  name: 'chat',
  initialState,
  reducers: {
    startNewConversation: state => {
      state.currentConversationId = null;
      state.messages = [];
    },
    addMessage: (state, action: PayloadAction<ChatMessage>) => {
      state.messages.push(action.payload);
    },
    appendToLastMessage: (state, action: PayloadAction<string>) => {
      const last = state.messages[state.messages.length - 1];
      if (last && last.role === 'assistant') {
        last.content += action.payload;
      } else {
        state.messages.push({
          id: Date.now(),
          conversation_id: state.currentConversationId ?? 0,
          role: 'assistant',
          content: action.payload,
          metadata: {},
          created_at: new Date().toISOString(),
        });
      }
    },
    setStreaming: (state, action: PayloadAction<boolean>) => {
      state.isStreaming = action.payload;
    },
    setCurrentConversationId: (state, action: PayloadAction<number>) => {
      state.currentConversationId = action.payload;
    },
    clearError: state => {
      state.error = null;
    },
  },
  extraReducers: builder => {
    builder
      .addCase(fetchHistory.fulfilled, (state, action) => {
        state.conversations = action.payload;
      })
      .addCase(fetchConversation.fulfilled, (state, action) => {
        state.messages = action.payload.messages;
        state.currentConversationId = action.payload.conversation.id;
      })
      .addCase(deleteConversation.fulfilled, (state, action) => {
        state.conversations = state.conversations.filter(c => c.id !== action.payload);
        if (state.currentConversationId === action.payload) {
          state.currentConversationId = null;
          state.messages = [];
        }
      })
      .addCase(deleteAllHistory.fulfilled, state => {
        state.conversations = [];
        state.currentConversationId = null;
        state.messages = [];
      });
  },
});

export const {
  startNewConversation,
  addMessage,
  appendToLastMessage,
  setStreaming,
  setCurrentConversationId,
  clearError,
} = chatSlice.actions;

export default chatSlice.reducer;
