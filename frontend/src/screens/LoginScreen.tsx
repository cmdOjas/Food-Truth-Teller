import React, {useState, useEffect} from 'react';
import {
  View,
  StyleSheet,
  KeyboardAvoidingView,
  Platform,
  Alert,
  ScrollView,
} from 'react-native';
import {Text, TextInput, Button, Surface} from 'react-native-paper';
import {NativeStackNavigationProp} from '@react-navigation/native-stack';
import {useAppDispatch, useAppSelector} from '../hooks/useAppDispatch';
import {loginUser, clearError} from '../store/slices/authSlice';
import {RootStackParamList} from '../types';

type Props = {
  navigation: NativeStackNavigationProp<RootStackParamList, 'Login'>;
};

export default function LoginScreen({navigation}: Props) {
  const dispatch = useAppDispatch();
  const {isLoading, error} = useAppSelector(s => s.auth);

  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);

  useEffect(() => {
    if (error) {
      Alert.alert('Login Failed', error);
      dispatch(clearError());
    }
  }, [error]);

  const handleLogin = async () => {
    if (!email.trim() || !password) {
      Alert.alert('Error', 'Please enter your email and password.');
      return;
    }
    dispatch(loginUser({email: email.trim().toLowerCase(), password}));
  };

  return (
    <KeyboardAvoidingView style={styles.container} behavior={Platform.OS === 'ios' ? 'padding' : undefined}>
      <ScrollView contentContainerStyle={styles.inner} keyboardShouldPersistTaps="handled">
        <Text variant="displaySmall" style={styles.title}>🥗 Food Truth Teller</Text>
        <Text variant="bodyLarge" style={styles.subtitle}>Your AI nutrition assistant</Text>

        <Surface style={styles.card} elevation={2}>
          <Text variant="headlineSmall" style={styles.cardTitle}>Sign In</Text>

          <TextInput
            label="Email"
            value={email}
            onChangeText={setEmail}
            keyboardType="email-address"
            autoCapitalize="none"
            autoComplete="email"
            left={<TextInput.Icon icon="email" />}
            style={styles.input}
          />

          <TextInput
            label="Password"
            value={password}
            onChangeText={setPassword}
            secureTextEntry={!showPassword}
            autoCapitalize="none"
            left={<TextInput.Icon icon="lock" />}
            right={<TextInput.Icon icon={showPassword ? 'eye-off' : 'eye'} onPress={() => setShowPassword(v => !v)} />}
            style={styles.input}
          />

          <Button
            mode="contained"
            onPress={handleLogin}
            loading={isLoading}
            disabled={isLoading}
            style={styles.button}
            contentStyle={styles.buttonContent}>
            Sign In
          </Button>

          <Button
            mode="text"
            onPress={() => navigation.navigate('Register')}
            style={styles.linkButton}>
            Don't have an account? Register
          </Button>
        </Surface>
      </ScrollView>
    </KeyboardAvoidingView>
  );
}

const styles = StyleSheet.create({
  container: {flex: 1, backgroundColor: '#f5f5f5'},
  inner: {flexGrow: 1, justifyContent: 'center', padding: 24},
  title: {textAlign: 'center', fontWeight: 'bold', color: '#2d6a4f', marginBottom: 4},
  subtitle: {textAlign: 'center', color: '#666', marginBottom: 32},
  card: {borderRadius: 16, padding: 24, backgroundColor: '#fff'},
  cardTitle: {fontWeight: '700', marginBottom: 20},
  input: {marginBottom: 12},
  button: {marginTop: 8, borderRadius: 8},
  buttonContent: {paddingVertical: 6},
  linkButton: {marginTop: 8},
});
