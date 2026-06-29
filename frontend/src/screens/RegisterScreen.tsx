import React, {useState, useEffect} from 'react';
import {View, StyleSheet, KeyboardAvoidingView, Platform, Alert, ScrollView} from 'react-native';
import {Text, TextInput, Button, Surface} from 'react-native-paper';
import {NativeStackNavigationProp} from '@react-navigation/native-stack';
import {useAppDispatch, useAppSelector} from '../hooks/useAppDispatch';
import {registerUser, clearError} from '../store/slices/authSlice';
import {RootStackParamList} from '../types';

type Props = {navigation: NativeStackNavigationProp<RootStackParamList, 'Register'>};

export default function RegisterScreen({navigation}: Props) {
  const dispatch = useAppDispatch();
  const {isLoading, error} = useAppSelector(s => s.auth);
  const [name, setName] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);

  useEffect(() => {
    if (error) {
      Alert.alert('Registration Failed', error);
      dispatch(clearError());
    }
  }, [error]);

  const handleRegister = () => {
    if (!name.trim() || !email.trim() || !password) {
      Alert.alert('Error', 'All fields are required.');
      return;
    }
    if (password !== confirmPassword) {
      Alert.alert('Error', 'Passwords do not match.');
      return;
    }
    if (password.length < 8) {
      Alert.alert('Error', 'Password must be at least 8 characters.');
      return;
    }
    dispatch(registerUser({email: email.trim().toLowerCase(), password, name: name.trim()}));
  };

  return (
    <KeyboardAvoidingView style={styles.container} behavior={Platform.OS === 'ios' ? 'padding' : undefined}>
      <ScrollView contentContainerStyle={styles.inner} keyboardShouldPersistTaps="handled">
        <Text variant="displaySmall" style={styles.title}>🥗 Food Truth Teller</Text>
        <Text variant="bodyLarge" style={styles.subtitle}>Create your account</Text>

        <Surface style={styles.card} elevation={2}>
          <Text variant="headlineSmall" style={styles.cardTitle}>Register</Text>

          <TextInput label="Full Name" value={name} onChangeText={setName} left={<TextInput.Icon icon="account" />} style={styles.input} />
          <TextInput label="Email" value={email} onChangeText={setEmail} keyboardType="email-address" autoCapitalize="none" left={<TextInput.Icon icon="email" />} style={styles.input} />
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
          <TextInput
            label="Confirm Password"
            value={confirmPassword}
            onChangeText={setConfirmPassword}
            secureTextEntry={!showPassword}
            autoCapitalize="none"
            left={<TextInput.Icon icon="lock-check" />}
            style={styles.input}
          />

          <Button mode="contained" onPress={handleRegister} loading={isLoading} disabled={isLoading} style={styles.button} contentStyle={styles.buttonContent}>
            Create Account
          </Button>

          <Button mode="text" onPress={() => navigation.navigate('Login')} style={styles.linkButton}>
            Already have an account? Sign In
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
