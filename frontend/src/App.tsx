import React from 'react';
import {Provider as ReduxProvider} from 'react-redux';
import {PaperProvider, MD3LightTheme} from 'react-native-paper';
import {GestureHandlerRootView} from 'react-native-gesture-handler';
import {store} from './store';
import AppNavigator from './navigation/AppNavigator';

const theme = {
  ...MD3LightTheme,
  colors: {
    ...MD3LightTheme.colors,
    primary: '#2d6a4f',
    secondary: '#52b788',
    background: '#f5f5f5',
  },
};

export default function App() {
  return (
    <GestureHandlerRootView style={{flex: 1}}>
      <ReduxProvider store={store}>
        <PaperProvider theme={theme}>
          <AppNavigator />
        </PaperProvider>
      </ReduxProvider>
    </GestureHandlerRootView>
  );
}
