import 'react-native-gesture-handler';
import React from 'react';
import { NavigationContainer, DefaultTheme } from '@react-navigation/native';
import { createDrawerNavigator } from '@react-navigation/drawer';
import { StatusBar } from 'react-native';
import Icon from 'react-native-vector-icons/Ionicons';

import { GestureHandlerRootView } from 'react-native-gesture-handler';
import { SafeAreaProvider } from 'react-native-safe-area-context';

// Importamos las pantallas actualizadas para análisis de técnica
import { HomeScreen } from './src/screens/HomeScreen';
import { RecordingScreen } from './src/screens/RecordingScreen';
import { AnalysisScreen } from './src/screens/AnalysisScreen';
import { HistoryScreen } from './src/screens/HistoryScreen';
import { SettingsScreen } from './src/screens/SettingsScreen';

const Drawer = createDrawerNavigator();

// Tema oscuro personalizado
const DarkTheme = {
  ...DefaultTheme,
  colors: {
    ...DefaultTheme.colors,
    primary: '#BB86FC',
    background: '#121212',
    card: '#1F1F1F',
    text: '#FFFFFF',
    border: '#333333',
    notification: '#CF6679',
  },
};

const App = () => {
  return (
    <GestureHandlerRootView style={{ flex: 1 }}>
      <SafeAreaProvider>
        <StatusBar barStyle="light-content" backgroundColor="#121212" />
        <NavigationContainer theme={DarkTheme}>
          <Drawer.Navigator
            initialRouteName="Inicio"
            screenOptions={{
              headerStyle: { 
                backgroundColor: '#1F1F1F',
                elevation: 0,
                shadowOpacity: 0,
                borderBottomWidth: 1,
                borderBottomColor: '#333333',
              },
              headerTintColor: '#FFFFFF',
              headerTitleStyle: {
                fontWeight: 'bold',
                fontSize: 18,
              },
              drawerStyle: {
                backgroundColor: '#1F1F1F',
                width: 280,
              },
              drawerActiveBackgroundColor: '#BB86FC20',
              drawerActiveTintColor: '#BB86FC',
              drawerInactiveTintColor: '#FFFFFF',
              drawerLabelStyle: {
                marginLeft: -16,
                fontSize: 16,
                fontWeight: '500',
              },
              drawerItemStyle: {
                marginHorizontal: 12,
                borderRadius: 8,
              },
            }}
          >
            <Drawer.Screen 
              name="Inicio" 
              component={HomeScreen}
              options={{
                drawerIcon: ({ color }) => (
                  <Icon name="home-outline" size={24} color={color} />
                ),
              }}
            />
            <Drawer.Screen 
              name="Grabación" 
              component={RecordingScreen}
              options={{
                drawerIcon: ({ color }) => (
                  <Icon name="videocam-outline" size={24} color={color} />
                ),
              }}
            />
            <Drawer.Screen 
              name="Análisis" 
              component={AnalysisScreen}
              options={{
                drawerIcon: ({ color }) => (
                  <Icon name="analytics-outline" size={24} color={color} />
                ),
              }}
            />
            <Drawer.Screen 
              name="Historial" 
              component={HistoryScreen}
              options={{
                drawerIcon: ({ color }) => (
                  <Icon name="time-outline" size={24} color={color} />
                ),
              }}
            />
            <Drawer.Screen 
              name="Configuración" 
              component={SettingsScreen}
              options={{
                drawerIcon: ({ color }) => (
                  <Icon name="settings-outline" size={24} color={color} />
                ),
              }}
            />
          </Drawer.Navigator>
        </NavigationContainer>
      </SafeAreaProvider>
    </GestureHandlerRootView>
  );
};

export default App;