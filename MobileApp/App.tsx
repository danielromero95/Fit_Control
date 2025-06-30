import 'react-native-gesture-handler'; // ¡Importante! Debe estar en la primera línea
import React from 'react';
import { NavigationContainer } from '@react-navigation/native';
import { createDrawerNavigator } from '@react-navigation/drawer';

// Importamos las pantallas que creaste en la carpeta 'src/screens'
import { HomeScreen } from './src/screens/HomeScreen';
import { ExercisesScreen } from './src/screens/ExercisesScreen';
import { PlansScreen } from './src/screens/PlansScreen';
import { ProfileScreen } from './src/screens/ProfileScreen';
import { ContactScreen } from './src/screens/ContactScreen';

// Creamos la instancia del navegador de menú lateral
const Drawer = createDrawerNavigator();

const App = () => {
  return (
    <NavigationContainer>
      <Drawer.Navigator
        initialRouteName="Inicio" // La pantalla que se verá al abrir la app
        screenOptions={{
          // Personalizamos un poco el estilo
          headerStyle: { backgroundColor: '#2c3e50' }, // Color de la barra superior
          headerTintColor: '#fff', // Color del título y del botón del menú
          drawerActiveBackgroundColor: '#3498db', // Color del elemento seleccionado en el menú
          drawerActiveTintColor: '#fff', // Color del texto del elemento seleccionado
        }}
      >
        {/* Aquí definimos cada una de las pantallas que aparecerán en el menú */}
        <Drawer.Screen name="Inicio" component={HomeScreen} />
        <Drawer.Screen name="Ejercicios" component={ExercisesScreen} />
        <Drawer.Screen name="Planes" component={PlansScreen} />
        <Drawer.Screen name="Perfil" component={ProfileScreen} />
        <Drawer.Screen name="Contacto" component={ContactScreen} />
      </Drawer.Navigator>
    </NavigationContainer>
  );
};

export default App;