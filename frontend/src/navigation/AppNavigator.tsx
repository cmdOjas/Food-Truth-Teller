import React, {useEffect} from 'react';
import {NavigationContainer} from '@react-navigation/native';
import {createNativeStackNavigator} from '@react-navigation/native-stack';
import {createBottomTabNavigator} from '@react-navigation/bottom-tabs';
import {ActivityIndicator, View} from 'react-native';
import {IconButton} from 'react-native-paper';
import {useAppDispatch, useAppSelector} from '../hooks/useAppDispatch';
import {loadStoredAuth, logout} from '../store/slices/authSlice';
import {RootStackParamList} from '../types';

import LoginScreen from '../screens/LoginScreen';
import RegisterScreen from '../screens/RegisterScreen';
import HomeScreen from '../screens/HomeScreen';
import ScannerScreen from '../screens/ScannerScreen';
import ChatScreen from '../screens/ChatScreen';
import ProductDetailScreen from '../screens/ProductDetailScreen';
import ProfileScreen from '../screens/ProfileScreen';
import HistoryScreen from '../screens/HistoryScreen';

const Stack = createNativeStackNavigator<RootStackParamList>();
const Tab = createBottomTabNavigator();

function MainTabs() {
  const dispatch = useAppDispatch();
  return (
    <Tab.Navigator
      screenOptions={{
        tabBarActiveTintColor: '#2d6a4f',
        tabBarInactiveTintColor: '#888',
        headerRight: () => (
          <IconButton icon="logout" size={22} onPress={() => dispatch(logout())} />
        ),
      }}>
      <Tab.Screen
        name="Home"
        component={HomeScreen}
        options={{
          tabBarIcon: ({color}) => <IconButton icon="home" iconColor={color} size={24} />,
          title: 'Food Truth Teller',
        }}
      />
      <Tab.Screen
        name="ScannerTab"
        component={ScannerScreen}
        options={{
          tabBarIcon: ({color}) => <IconButton icon="barcode-scan" iconColor={color} size={24} />,
          title: 'Scan',
        }}
      />
      <Tab.Screen
        name="ChatTab"
        component={ChatScreen}
        options={{
          tabBarIcon: ({color}) => <IconButton icon="chat" iconColor={color} size={24} />,
          title: 'AI Chat',
        }}
        initialParams={{}}
      />
      <Tab.Screen
        name="ProfileTab"
        component={ProfileScreen}
        options={{
          tabBarIcon: ({color}) => <IconButton icon="account" iconColor={color} size={24} />,
          title: 'Profile',
        }}
      />
    </Tab.Navigator>
  );
}

export default function AppNavigator() {
  const dispatch = useAppDispatch();
  const {token, isLoading} = useAppSelector(s => s.auth);

  useEffect(() => {
    dispatch(loadStoredAuth());
  }, []);

  if (isLoading) {
    return (
      <View style={{flex: 1, justifyContent: 'center', alignItems: 'center'}}>
        <ActivityIndicator size="large" color="#2d6a4f" />
      </View>
    );
  }

  return (
    <NavigationContainer>
      <Stack.Navigator screenOptions={{headerShown: false}}>
        {token ? (
          <>
            <Stack.Screen name="Main" component={MainTabs} />
            <Stack.Screen name="ProductDetail" component={ProductDetailScreen} options={{headerShown: true, title: 'Product Analysis'}} />
            <Stack.Screen name="Chat" component={ChatScreen} options={{headerShown: true, title: 'AI Assistant'}} />
            <Stack.Screen name="History" component={HistoryScreen} options={{headerShown: true, title: 'Chat History'}} />
            <Stack.Screen name="Profile" component={ProfileScreen} options={{headerShown: true, title: 'Health Profile'}} />
            <Stack.Screen name="Scanner" component={ScannerScreen} options={{headerShown: true, title: 'Scan Barcode'}} />
          </>
        ) : (
          <>
            <Stack.Screen name="Login" component={LoginScreen} />
            <Stack.Screen name="Register" component={RegisterScreen} />
          </>
        )}
      </Stack.Navigator>
    </NavigationContainer>
  );
}
