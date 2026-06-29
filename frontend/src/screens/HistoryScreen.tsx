import React, {useEffect} from 'react';
import {View, FlatList, StyleSheet, Alert} from 'react-native';
import {Text, Surface, IconButton, Button, ActivityIndicator} from 'react-native-paper';
import {NativeStackNavigationProp} from '@react-navigation/native-stack';
import {useAppDispatch, useAppSelector} from '../hooks/useAppDispatch';
import {fetchHistory, deleteConversation, deleteAllHistory, fetchConversation} from '../store/slices/chatSlice';
import {Conversation, RootStackParamList} from '../types';

type Props = {navigation: NativeStackNavigationProp<RootStackParamList, 'History'>};

export default function HistoryScreen({navigation}: Props) {
  const dispatch = useAppDispatch();
  const {conversations} = useAppSelector(s => s.chat);

  useEffect(() => {
    dispatch(fetchHistory());
  }, []);

  const handleOpen = async (id: number) => {
    await dispatch(fetchConversation(id));
    navigation.navigate('Chat', {conversationId: id});
  };

  const handleDelete = (id: number) => {
    Alert.alert('Delete Conversation', 'Are you sure?', [
      {text: 'Cancel'},
      {text: 'Delete', style: 'destructive', onPress: () => dispatch(deleteConversation(id))},
    ]);
  };

  const handleDeleteAll = () => {
    Alert.alert('Delete All History', 'This will delete all your conversations. Are you sure?', [
      {text: 'Cancel'},
      {text: 'Delete All', style: 'destructive', onPress: () => dispatch(deleteAllHistory())},
    ]);
  };

  const renderItem = ({item}: {item: Conversation}) => (
    <Surface style={styles.item} elevation={1} onTouchEnd={() => handleOpen(item.id)}>
      <View style={styles.itemContent}>
        <View style={styles.itemLeft}>
          <Text variant="bodyLarge" style={styles.itemTitle} numberOfLines={1}>{item.title}</Text>
          <Text variant="bodySmall" style={styles.itemMeta}>
            {item.message_count} messages · {new Date(item.created_at).toLocaleDateString()}
          </Text>
          {item.product_barcode && (
            <Text variant="bodySmall" style={styles.itemBarcode}>🛒 {item.product_barcode}</Text>
          )}
        </View>
        <IconButton icon="delete-outline" size={20} iconColor="#e63946" onPress={() => handleDelete(item.id)} />
      </View>
    </Surface>
  );

  return (
    <View style={styles.container}>
      {conversations.length > 0 && (
        <Button mode="outlined" onPress={handleDeleteAll} style={styles.deleteAllBtn} textColor="#e63946">
          Delete All History
        </Button>
      )}
      <FlatList
        data={conversations}
        keyExtractor={item => String(item.id)}
        renderItem={renderItem}
        contentContainerStyle={styles.list}
        ListEmptyComponent={
          <View style={styles.empty}>
            <Text style={styles.emptyIcon}>💬</Text>
            <Text variant="bodyLarge" style={styles.emptyText}>No conversations yet</Text>
            <Text variant="bodySmall" style={styles.emptySubtext}>Start chatting with the AI assistant</Text>
          </View>
        }
      />
    </View>
  );
}

const styles = StyleSheet.create({
  container: {flex: 1, backgroundColor: '#f5f5f5'},
  deleteAllBtn: {margin: 16, borderColor: '#e63946'},
  list: {padding: 16, paddingTop: 0, paddingBottom: 32},
  item: {borderRadius: 12, padding: 4, marginBottom: 10, backgroundColor: '#fff'},
  itemContent: {flexDirection: 'row', alignItems: 'center', padding: 12},
  itemLeft: {flex: 1},
  itemTitle: {fontWeight: '600'},
  itemMeta: {color: '#888', marginTop: 2},
  itemBarcode: {color: '#2d6a4f', marginTop: 2},
  empty: {alignItems: 'center', marginTop: 80},
  emptyIcon: {fontSize: 56, marginBottom: 12},
  emptyText: {fontWeight: '600'},
  emptySubtext: {color: '#888', marginTop: 4},
});
