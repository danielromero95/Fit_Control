import 'react-native-gesture-handler';
import React from 'react';
import { NavigationContainer } from '@react-navigation/native';
import { createDrawerNavigator } from '@react-navigation/drawer';
import { GestureHandlerRootView } from 'react-native-gesture-handler';

// 1. IMPORTAMOS el proveedor que nos falta
import { SafeAreaProvider } from 'react-native-safe-area-context';

// Importamos las pantallas
import { HomeScreen } from './src/screens/HomeScreen';
import { ExercisesScreen } from './src/screens/ExercisesScreen';
import { PlansScreen } from './src/screens/PlansScreen';
import { ProfileScreen } from './src/screens/ProfileScreen';
import { ContactScreen } from './src/screens/ContactScreen';

const Drawer = createDrawerNavigator();

const App = () => {
  return (
    <GestureHandlerRootView style={{ flex: 1 }}>
      {/* 2. ENVOLVEMOS el navegador con SafeAreaProvider */}
      <SafeAreaProvider>
        <NavigationContainer>
          <Drawer.Navigator
            initialRouteName="Inicio"
            screenOptions={{
              headerStyle: { backgroundColor: '#2c3e50' },
              headerTintColor: '#fff',
              drawerActiveBackgroundColor: '#3498db',
              drawerActiveTintColor: '#fff',
            }}
          >
            <Drawer.Screen name="Inicio" component={HomeScreen} />
            <Drawer.Screen name="Ejercicios" component={ExercisesScreen} />
            <Drawer.Screen name="Planes" component={PlansScreen} />
            <Drawer.Screen name="Perfil" component={ProfileScreen} />
            <Drawer.Screen name="Contacto" component={ContactScreen} />
          </Drawer.Navigator>
        </NavigationContainer>
      </SafeAreaProvider>
    </GestureHandlerRootView>
  );
};

export default App;