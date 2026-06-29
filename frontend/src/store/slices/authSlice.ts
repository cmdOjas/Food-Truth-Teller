import {createSlice, createAsyncThunk, PayloadAction} from '@reduxjs/toolkit';
import AsyncStorage from '@react-native-async-storage/async-storage';
import {authApi} from '../../services/api';
import {AuthState, User} from '../../types';

const initialState: AuthState = {
  token: null,
  user: null,
  isLoading: false,
  error: null,
};

export const registerUser = createAsyncThunk(
  'auth/register',
  async ({email, password, name}: {email: string; password: string; name: string}, {rejectWithValue}) => {
    try {
      const res = await authApi.register(email, password, name);
      await AsyncStorage.setItem('jwt_token', res.data.token);
      return res.data;
    } catch (err: any) {
      return rejectWithValue(err.response?.data?.error ?? 'Registration failed');
    }
  },
);

export const loginUser = createAsyncThunk(
  'auth/login',
  async ({email, password}: {email: string; password: string}, {rejectWithValue}) => {
    try {
      const res = await authApi.login(email, password);
      await AsyncStorage.setItem('jwt_token', res.data.token);
      return res.data;
    } catch (err: any) {
      return rejectWithValue(err.response?.data?.error ?? 'Login failed');
    }
  },
);

export const loadStoredAuth = createAsyncThunk('auth/loadStored', async () => {
  const token = await AsyncStorage.getItem('jwt_token');
  if (!token) return null;
  const res = await authApi.me();
  return {token, user: res.data as User};
});

export const logout = createAsyncThunk('auth/logout', async () => {
  await AsyncStorage.removeItem('jwt_token');
});

const authSlice = createSlice({
  name: 'auth',
  initialState,
  reducers: {
    clearError: state => {
      state.error = null;
    },
  },
  extraReducers: builder => {
    builder
      .addCase(registerUser.pending, state => {
        state.isLoading = true;
        state.error = null;
      })
      .addCase(registerUser.fulfilled, (state, action) => {
        state.isLoading = false;
        state.token = action.payload.token;
        state.user = action.payload.user;
      })
      .addCase(registerUser.rejected, (state, action) => {
        state.isLoading = false;
        state.error = action.payload as string;
      })
      .addCase(loginUser.pending, state => {
        state.isLoading = true;
        state.error = null;
      })
      .addCase(loginUser.fulfilled, (state, action) => {
        state.isLoading = false;
        state.token = action.payload.token;
        state.user = action.payload.user;
      })
      .addCase(loginUser.rejected, (state, action) => {
        state.isLoading = false;
        state.error = action.payload as string;
      })
      .addCase(loadStoredAuth.fulfilled, (state, action) => {
        if (action.payload) {
          state.token = action.payload.token;
          state.user = action.payload.user;
        }
      })
      .addCase(logout.fulfilled, state => {
        state.token = null;
        state.user = null;
      });
  },
});

export const {clearError} = authSlice.actions;
export default authSlice.reducer;
