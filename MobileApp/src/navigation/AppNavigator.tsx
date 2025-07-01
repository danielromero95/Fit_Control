/**
 * Navegador principal de la aplicación Fit_Control
 * 
 * Implementa la navegación con Bottom Tab Navigator y Stack Navigator
 * según las especificaciones del proyecto.
 */

import React from 'react';
import { NavigationContainer } from '@react-navigation/native';
import { createBottomTabNavigator } from '@react-navigation/bottom-tabs';
import { createStackNavigator } from '@react-navigation/stack';
import { useTheme } from 'react-native-paper';
import Icon from 'react-native-vector-icons/MaterialCommunityIcons';

// Screens
import HomeScreen from '../screens/home/HomeScreen';
import PlansScreen from '../screens/plans/PlansScreen';
import PlanDetailScreen from '../screens/plans/PlanDetailScreen';
import ExercisesScreen from '../screens/exercises/ExercisesScreen';
import ExerciseDetailScreen from '../screens/exercises/ExerciseDetailScreen';
import ProfileScreen from '../screens/profile/ProfileScreen';
import WorkoutSessionScreen from '../screens/workout/WorkoutSessionScreen';
import LoginScreen from '../screens/auth/LoginScreen';
import RegisterScreen from '../screens/auth/RegisterScreen';

// Store
import { useAuthStore } from '../store/authStore';

const Tab = createBottomTabNavigator();
const Stack = createStackNavigator();

// Stack Navigators para cada pestaña
const HomeStack = () => {
  return (
    <Stack.Navigator screenOptions={{ headerShown: false }}>
      <Stack.Screen name="HomeMain" component={HomeScreen} />
      <Stack.Screen 
        name="WorkoutSession" 
        component={WorkoutSessionScreen}
        options={{ headerShown: true, title: 'Sesión de Entrenamiento' }}
      />
    </Stack.Navigator>
  );
};

const PlansStack = () => {
  return (
    <Stack.Navigator screenOptions={{ headerShown: false }}>
      <Stack.Screen name="PlansMain" component={PlansScreen} />
      <Stack.Screen 
        name="PlanDetail" 
        component={PlanDetailScreen}
        options={{ headerShown: true, title: 'Detalle del Plan' }}
      />
    </Stack.Navigator>
  );
};

const ExercisesStack = () => {
  return (
    <Stack.Navigator screenOptions={{ headerShown: false }}>
      <Stack.Screen name="ExercisesMain" component={ExercisesScreen} />
      <Stack.Screen 
        name="ExerciseDetail" 
        component={ExerciseDetailScreen}
        options={{ headerShown: true, title: 'Detalle del Ejercicio' }}
      />
    </Stack.Navigator>
  );
};

const ProfileStack = () => {
  return (
    <Stack.Navigator screenOptions={{ headerShown: false }}>
      <Stack.Screen name="ProfileMain" component={ProfileScreen} />
    </Stack.Navigator>
  );
};

// Main Tab Navigator
const TabNavigator = () => {
  const theme = useTheme();

  return (
    <Tab.Navigator
      screenOptions={({ route }) => ({
        tabBarIcon: ({ focused, color, size }) => {
          let iconName: string;

          switch (route.name) {
            case 'Hoy':
              iconName = focused ? 'home' : 'home-outline';
              break;
            case 'Planes':
              iconName = focused ? 'clipboard-text' : 'clipboard-text-outline';
              break;
            case 'Ejercicios':
              iconName = focused ? 'dumbbell' : 'dumbbell';
              break;
            case 'Perfil':
              iconName = focused ? 'account' : 'account-outline';
              break;
            default:
              iconName = 'circle';
          }

          return <Icon name={iconName} size={size} color={color} />;
        },
        tabBarActiveTintColor: theme.colors.primary,
        tabBarInactiveTintColor: theme.colors.onSurfaceVariant,
        tabBarStyle: {
          backgroundColor: theme.colors.surface,
          borderTopColor: theme.colors.outline,
          height: 60,
          paddingBottom: 8,
          paddingTop: 8,
        },
        tabBarLabelStyle: {
          fontSize: 12,
          fontWeight: '500',
        },
        headerShown: true,
        headerStyle: {
          backgroundColor: theme.colors.surface,
        },
        headerTitleStyle: {
          color: theme.colors.onSurface,
          fontSize: 18,
          fontWeight: '600',
        },
      })}
    >
      <Tab.Screen 
        name="Hoy" 
        component={HomeStack}
        options={{ title: 'Hoy' }}
      />
      <Tab.Screen 
        name="Planes" 
        component={PlansStack}
        options={{ title: 'Planes' }}
      />
      <Tab.Screen 
        name="Ejercicios" 
        component={ExercisesStack}
        options={{ title: 'Ejercicios' }}
      />
      <Tab.Screen 
        name="Perfil" 
        component={ProfileStack}
        options={{ title: 'Perfil' }}
      />
    </Tab.Navigator>
  );
};

// Auth Stack Navigator
const AuthStack = () => {
  return (
    <Stack.Navigator screenOptions={{ headerShown: false }}>
      <Stack.Screen name="Login" component={LoginScreen} />
      <Stack.Screen name="Register" component={RegisterScreen} />
    </Stack.Navigator>
  );
};

// Main App Navigator
const AppNavigator: React.FC = () => {
  const { isAuthenticated } = useAuthStore();

  return (
    <NavigationContainer>
      {isAuthenticated ? <TabNavigator /> : <AuthStack />}
    </NavigationContainer>
  );
};

export default AppNavigator;