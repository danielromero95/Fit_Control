import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  TouchableOpacity,
  Dimensions,
  StatusBar,
} from 'react-native';
import { LinearGradient } from 'expo-linear-gradient';
import { Ionicons } from '@expo/vector-icons';

const { width } = Dimensions.get('window');

interface StatCard {
  title: string;
  value: string;
  icon: string;
  color: string;
  trend?: string;
}

export const HomeScreen = ({ navigation }: any) => {
  const [stats, setStats] = useState<StatCard[]>([
    {
      title: 'Entrenamientos',
      value: '12',
      icon: 'fitness',
      color: '#4ECDC4',
      trend: '+2 esta semana'
    },
    {
      title: 'Repeticiones',
      value: '450',
      icon: 'trending-up',
      color: '#45B7D1',
      trend: '+15% vs anterior'
    },
    {
      title: 'Tiempo Total',
      value: '8.5h',
      icon: 'time',
      color: '#96CEB4',
      trend: 'Esta semana'
    },
    {
      title: 'Peso Levantado',
      value: '2.4t',
      icon: 'barbell',
      color: '#FFEAA7',
      trend: '+200kg esta semana'
    }
  ]);

  const quickActions = [
    { title: 'Nuevo Entrenamiento', icon: 'add-circle', screen: 'Ejercicios', color: '#FF6B6B' },
    { title: 'Ver Planes', icon: 'calendar', screen: 'Planes', color: '#4ECDC4' },
    { title: 'Progreso', icon: 'analytics', screen: 'Perfil', color: '#45B7D1' },
    { title: 'Configuración', icon: 'settings', screen: 'Contacto', color: '#96CEB4' },
  ];

  return (
    <View style={styles.container}>
      <StatusBar barStyle="light-content" backgroundColor="#1a1a2e" />
      
      <LinearGradient
        colors={['#1a1a2e', '#16213e', '#0f1624']}
        style={styles.header}
      >
        <View style={styles.headerContent}>
          <View>
            <Text style={styles.greeting}>¡Hola!</Text>
            <Text style={styles.username}>Bienvenido de vuelta</Text>
          </View>
          <TouchableOpacity style={styles.profileButton}>
            <Ionicons name="person-circle" size={40} color="#4ECDC4" />
          </TouchableOpacity>
        </View>
      </LinearGradient>

      <ScrollView style={styles.content} showsVerticalScrollIndicator={false}>
        {/* Stats Section */}
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>Resumen de Actividad</Text>
          <View style={styles.statsGrid}>
            {stats.map((stat, index) => (
              <View key={index} style={[styles.statCard, { borderLeftColor: stat.color }]}>
                <View style={styles.statHeader}>
                  <Ionicons name={stat.icon as any} size={24} color={stat.color} />
                  <Text style={styles.statTitle}>{stat.title}</Text>
                </View>
                <Text style={styles.statValue}>{stat.value}</Text>
                {stat.trend && <Text style={styles.statTrend}>{stat.trend}</Text>}
              </View>
            ))}
          </View>
        </View>

        {/* Quick Actions */}
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>Acciones Rápidas</Text>
          <View style={styles.actionsGrid}>
            {quickActions.map((action, index) => (
              <TouchableOpacity
                key={index}
                style={styles.actionCard}
                onPress={() => navigation.navigate(action.screen)}
                activeOpacity={0.7}
              >
                <LinearGradient
                  colors={[action.color, `${action.color}CC`]}
                  style={styles.actionGradient}
                >
                  <Ionicons name={action.icon as any} size={28} color="white" />
                  <Text style={styles.actionTitle}>{action.title}</Text>
                </LinearGradient>
              </TouchableOpacity>
            ))}
          </View>
        </View>

        {/* Recent Activity */}
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>Actividad Reciente</Text>
          <View style={styles.activityCard}>
            <View style={styles.activityItem}>
              <View style={styles.activityIcon}>
                <Ionicons name="checkmark-circle" size={20} color="#4ECDC4" />
              </View>
              <View style={styles.activityContent}>
                <Text style={styles.activityTitle}>Entrenamiento de Pecho completado</Text>
                <Text style={styles.activityTime}>Hace 2 horas • 45 min</Text>
              </View>
            </View>
            
            <View style={styles.activityItem}>
              <View style={styles.activityIcon}>
                <Ionicons name="trophy" size={20} color="#FFEAA7" />
              </View>
              <View style={styles.activityContent}>
                <Text style={styles.activityTitle}>¡Nuevo récord personal!</Text>
                <Text style={styles.activityTime}>Ayer • Press de banca: 80kg</Text>
              </View>
            </View>

            <View style={styles.activityItem}>
              <View style={styles.activityIcon}>
                <Ionicons name="calendar" size={20} color="#45B7D1" />
              </View>
              <View style={styles.activityContent}>
                <Text style={styles.activityTitle}>Plan de entrenamiento actualizado</Text>
                <Text style={styles.activityTime}>Hace 3 días</Text>
              </View>
            </View>
          </View>
        </View>

        {/* Today's Workout Preview */}
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>Entrenamiento de Hoy</Text>
          <TouchableOpacity 
            style={styles.todayWorkoutCard}
            onPress={() => navigation.navigate('Ejercicios')}
          >
            <LinearGradient
              colors={['#667eea', '#764ba2']}
              style={styles.todayWorkoutGradient}
            >
              <View style={styles.todayWorkoutContent}>
                <Text style={styles.todayWorkoutTitle}>Entrenamiento de Piernas</Text>
                <Text style={styles.todayWorkoutDetails}>5 ejercicios • 45-60 min</Text>
                <View style={styles.todayWorkoutProgress}>
                  <Text style={styles.progressText}>Progreso: 0/5</Text>
                  <View style={styles.progressBar}>
                    <View style={[styles.progressFill, { width: '0%' }]} />
                  </View>
                </View>
              </View>
              <Ionicons name="chevron-forward" size={24} color="white" />
            </LinearGradient>
          </TouchableOpacity>
        </View>
      </ScrollView>
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f8f9fa',
  },
  header: {
    paddingTop: 50,
    paddingBottom: 20,
    paddingHorizontal: 20,
  },
  headerContent: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
  },
  greeting: {
    fontSize: 16,
    color: '#a0a0a0',
  },
  username: {
    fontSize: 24,
    fontWeight: 'bold',
    color: 'white',
    marginTop: 4,
  },
  profileButton: {
    padding: 4,
  },
  content: {
    flex: 1,
    paddingHorizontal: 20,
  },
  section: {
    marginVertical: 15,
  },
  sectionTitle: {
    fontSize: 20,
    fontWeight: 'bold',
    color: '#2c3e50',
    marginBottom: 15,
  },
  statsGrid: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    justifyContent: 'space-between',
  },
  statCard: {
    backgroundColor: 'white',
    borderRadius: 12,
    padding: 16,
    width: (width - 50) / 2,
    marginBottom: 12,
    borderLeftWidth: 4,
    elevation: 3,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 3,
  },
  statHeader: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 8,
  },
  statTitle: {
    fontSize: 14,
    color: '#7f8c8d',
    marginLeft: 8,
    fontWeight: '500',
  },
  statValue: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#2c3e50',
    marginBottom: 4,
  },
  statTrend: {
    fontSize: 12,
    color: '#27ae60',
    fontWeight: '500',
  },
  actionsGrid: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    justifyContent: 'space-between',
  },
  actionCard: {
    width: (width - 50) / 2,
    height: 100,
    marginBottom: 12,
    borderRadius: 12,
    overflow: 'hidden',
  },
  actionGradient: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    paddingHorizontal: 16,
  },
  actionTitle: {
    color: 'white',
    fontSize: 14,
    fontWeight: 'bold',
    marginTop: 8,
    textAlign: 'center',
  },
  activityCard: {
    backgroundColor: 'white',
    borderRadius: 12,
    padding: 16,
    elevation: 3,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 3,
  },
  activityItem: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingVertical: 12,
    borderBottomWidth: 1,
    borderBottomColor: '#ecf0f1',
  },
  activityIcon: {
    width: 36,
    height: 36,
    borderRadius: 18,
    backgroundColor: '#f8f9fa',
    justifyContent: 'center',
    alignItems: 'center',
    marginRight: 12,
  },
  activityContent: {
    flex: 1,
  },
  activityTitle: {
    fontSize: 14,
    fontWeight: '600',
    color: '#2c3e50',
    marginBottom: 2,
  },
  activityTime: {
    fontSize: 12,
    color: '#7f8c8d',
  },
  todayWorkoutCard: {
    borderRadius: 12,
    overflow: 'hidden',
    elevation: 3,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 3,
  },
  todayWorkoutGradient: {
    flexDirection: 'row',
    alignItems: 'center',
    padding: 20,
  },
  todayWorkoutContent: {
    flex: 1,
  },
  todayWorkoutTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    color: 'white',
    marginBottom: 4,
  },
  todayWorkoutDetails: {
    fontSize: 14,
    color: 'rgba(255, 255, 255, 0.8)',
    marginBottom: 12,
  },
  todayWorkoutProgress: {
    marginTop: 8,
  },
  progressText: {
    fontSize: 12,
    color: 'rgba(255, 255, 255, 0.9)',
    marginBottom: 6,
  },
  progressBar: {
    height: 4,
    backgroundColor: 'rgba(255, 255, 255, 0.3)',
    borderRadius: 2,
  },
  progressFill: {
    height: '100%',
    backgroundColor: 'white',
    borderRadius: 2,
  },
});