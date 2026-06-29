import React, {useState, useRef, useCallback, useEffect} from 'react';
import {
  View,
  FlatList,
  StyleSheet,
  KeyboardAvoidingView,
  Platform,
  Alert,
} from 'react-native';
import {Text, TextInput, IconButton, Surface, ActivityIndicator} from 'react-native-paper';
import {NativeStackNavigationProp} from '@react-navigation/native-stack';
import {RouteProp} from '@react-navigation/native';
import Markdown from 'react-native-markdown-display';
import {useAppDispatch, useAppSelector} from '../hooks/useAppDispatch';
import {
  addMessage,
  appendToLastMessage,
  setStreaming,
  setCurrentConversationId,
} from '../store/slices/chatSlice';
import {streamChat} from '../services/api';
import {RootStackParamList, ChatMessage} from '../types';

type Props = {
  navigation: NativeStackNavigationProp<RootStackParamList, 'Chat'>;
  route: RouteProp<RootStackParamList, 'Chat'>;
};

const QUICK_PROMPTS = [
  'Can I eat this?',
  'Is this safe for me?',
  'What ingredients are harmful?',
  'Suggest healthier alternatives',
  'Explain ingredients in simple terms',
];

export default function ChatScreen({navigation, route}: Props) {
  const dispatch = useAppDispatch();
  const {token} = useAppSelector(s => s.auth);
  const {messages, isStreaming, currentConversationId} = useAppSelector(s => s.chat);
  const {currentProduct} = useAppSelector(s => s.product);
  const [input, setInput] = useState('');
  const flatListRef = useRef<FlatList>(null);

  const barcode = route.params?.barcode ?? currentProduct?.barcode ?? null;

  const sendMessage = useCallback(
    async (text: string) => {
      if (!text.trim() || isStreaming || !token) return;
      const userText = text.trim();
      setInput('');

      const userMsg: ChatMessage = {
        id: Date.now(),
        conversation_id: currentConversationId ?? 0,
        role: 'user',
        content: userText,
        metadata: {},
        created_at: new Date().toISOString(),
      };
      dispatch(addMessage(userMsg));
      dispatch(setStreaming(true));

      try {
        let convId = currentConversationId;
        let firstChunk = true;

        for await (const chunk of streamChat(userText, convId, barcode, token)) {
          if (firstChunk) {
            firstChunk = false;
          }
          dispatch(appendToLastMessage(chunk));
        }
      } catch (err: any) {
        Alert.alert('Error', 'Failed to get a response. Please try again.');
        dispatch(appendToLastMessage('\n\n⚠️ Failed to get response.'));
      } finally {
        dispatch(setStreaming(false));
        setTimeout(() => flatListRef.current?.scrollToEnd({animated: true}), 100);
      }
    },
    [dispatch, isStreaming, token, currentConversationId, barcode],
  );

  const renderMessage = ({item}: {item: ChatMessage}) => {
    const isUser = item.role === 'user';
    return (
      <View style={[styles.messageRow, isUser ? styles.userRow : styles.assistantRow]}>
        {!isUser && (
          <View style={styles.avatar}>
            <Text style={styles.avatarText}>🤖</Text>
          </View>
        )}
        <Surface
          style={[styles.bubble, isUser ? styles.userBubble : styles.assistantBubble]}
          elevation={1}>
          {isUser ? (
            <Text style={styles.userText}>{item.content}</Text>
          ) : (
            <Markdown style={markdownStyles}>{item.content}</Markdown>
          )}
        </Surface>
      </View>
    );
  };

  return (
    <KeyboardAvoidingView
      style={styles.container}
      behavior={Platform.OS === 'ios' ? 'padding' : 'height'}
      keyboardVerticalOffset={Platform.OS === 'ios' ? 90 : 0}>

      {/* Product context banner */}
      {currentProduct && (
        <Surface style={styles.productBanner} elevation={1}>
          <Text variant="bodySmall" style={styles.bannerText}>
            🛒 {currentProduct.name} · {currentProduct.brand ?? ''}
          </Text>
        </Surface>
      )}

      {/* Quick prompts */}
      {messages.length === 0 && (
        <View style={styles.quickPrompts}>
          <Text variant="bodySmall" style={styles.quickLabel}>Quick questions:</Text>
          <View style={styles.promptChips}>
            {QUICK_PROMPTS.map(p => (
              <Surface key={p} style={styles.promptChip} elevation={1} onTouchEnd={() => sendMessage(p)}>
                <Text variant="bodySmall">{p}</Text>
              </Surface>
            ))}
          </View>
        </View>
      )}

      <FlatList
        ref={flatListRef}
        data={messages}
        keyExtractor={item => String(item.id)}
        renderItem={renderMessage}
        contentContainerStyle={styles.messageList}
        onContentSizeChange={() => flatListRef.current?.scrollToEnd({animated: true})}
      />

      {isStreaming && (
        <View style={styles.typingIndicator}>
          <ActivityIndicator size="small" />
          <Text variant="bodySmall" style={{marginLeft: 8}}>AI is typing...</Text>
        </View>
      )}

      <Surface style={styles.inputBar} elevation={4}>
        <TextInput
          value={input}
          onChangeText={setInput}
          placeholder="Ask about this product..."
          multiline
          maxLength={500}
          style={styles.textInput}
          right={
            <TextInput.Icon
              icon="send"
              disabled={isStreaming || !input.trim()}
              onPress={() => sendMessage(input)}
            />
          }
          onSubmitEditing={() => sendMessage(input)}
        />
      </Surface>
    </KeyboardAvoidingView>
  );
}

const styles = StyleSheet.create({
  container: {flex: 1, backgroundColor: '#f0f0f0'},
  productBanner: {padding: 10, backgroundColor: '#d8f3dc', borderRadius: 0},
  bannerText: {color: '#2d6a4f', fontWeight: '600'},
  quickPrompts: {padding: 12},
  quickLabel: {color: '#888', marginBottom: 8},
  promptChips: {flexDirection: 'row', flexWrap: 'wrap', gap: 8},
  promptChip: {
    paddingHorizontal: 12,
    paddingVertical: 8,
    borderRadius: 20,
    backgroundColor: '#fff',
  },
  messageList: {padding: 12, paddingBottom: 4},
  messageRow: {flexDirection: 'row', marginVertical: 6, alignItems: 'flex-end'},
  userRow: {justifyContent: 'flex-end'},
  assistantRow: {justifyContent: 'flex-start'},
  avatar: {width: 32, height: 32, borderRadius: 16, backgroundColor: '#e8f5e9', justifyContent: 'center', alignItems: 'center', marginRight: 8},
  avatarText: {fontSize: 16},
  bubble: {maxWidth: '78%', borderRadius: 16, padding: 12},
  userBubble: {backgroundColor: '#2d6a4f', borderBottomRightRadius: 4},
  assistantBubble: {backgroundColor: '#fff', borderBottomLeftRadius: 4},
  userText: {color: '#fff'},
  typingIndicator: {flexDirection: 'row', alignItems: 'center', padding: 12},
  inputBar: {padding: 8, backgroundColor: '#fff'},
  textInput: {backgroundColor: '#fff', maxHeight: 120},
});

const markdownStyles = {
  body: {color: '#333', fontSize: 14, lineHeight: 22},
  strong: {fontWeight: '700' as const},
  em: {fontStyle: 'italic' as const},
  bullet_list: {marginVertical: 4},
  code_inline: {backgroundColor: '#f3f4f6', borderRadius: 4, paddingHorizontal: 4},
};
