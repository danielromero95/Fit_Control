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
import { LinearGradient } from 'react-native-linear-gradient';
import Icon from 'react-native-vector-icons/Ionicons';

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
      title: 'Videos Analizados',
      value: '24',
      icon: 'videocam',
      color: '#BB86FC',
      trend: '+5 esta semana'
    },
    {
      title: 'Sesiones Grabadas',
      value: '32',
      icon: 'recording',
      color: '#03DAC6',
      trend: '+8 vs anterior'
    },
    {
      title: 'Tiempo Total',
      value: '12.5h',
      icon: 'time',
      color: '#CF6679',
      trend: 'Esta semana'
    },
    {
      title: 'Precisión Media',
      value: '87%',
      icon: 'analytics',
      color: '#FFA726',
      trend: '+3% mejora'
    }
  ]);

  const quickActions = [
    { title: 'Nueva Grabación', icon: 'videocam', screen: 'Grabación', color: '#BB86FC' },
    { title: 'Ver Análisis', icon: 'analytics', screen: 'Análisis', color: '#03DAC6' },
    { title: 'Historial', icon: 'time', screen: 'Historial', color: '#CF6679' },
    { title: 'Configuración', icon: 'settings', screen: 'Configuración', color: '#FFA726' },
  ];

  const recentAnalyses = [
    {
      id: 1,
      title: 'Análisis de Sentadilla',
      timestamp: 'Hace 2 horas',
      accuracy: '92%',
      duration: '45 seg',
      status: 'completed'
    },
    {
      id: 2,
      title: 'Técnica de Press Banca',
      timestamp: 'Ayer',
      accuracy: '85%',
      duration: '1:20 min',
      status: 'completed'
    },
    {
      id: 3,
      title: 'Deadlift Form Check',
      timestamp: 'Hace 2 días',
      accuracy: '78%',
      duration: '2:15 min',
      status: 'needs_review'
    }
  ];

  return (
    <View style={styles.container}>
      <StatusBar barStyle="light-content" backgroundColor="#121212" />
      
      <LinearGradient
        colors={['#1F1F1F', '#2C2C2C', '#1F1F1F']}
        style={styles.header}
      >
        <View style={styles.headerContent}>
          <View>
            <Text style={styles.greeting}>¡Hola Atleta!</Text>
            <Text style={styles.username}>Analiza tu técnica deportiva</Text>
          </View>
          <TouchableOpacity style={styles.profileButton}>
            <Icon name="person-circle" size={40} color="#BB86FC" />
          </TouchableOpacity>
        </View>
      </LinearGradient>

      <ScrollView style={styles.content} showsVerticalScrollIndicator={false}>
        {/* Stats Section */}
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>Resumen de Análisis</Text>
          <View style={styles.statsGrid}>
            {stats.map((stat, index) => (
              <View key={index} style={[styles.statCard, { borderLeftColor: stat.color }]}>
                <View style={styles.statHeader}>
                  <Icon name={stat.icon as any} size={24} color={stat.color} />
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
                  colors={[action.color, `${action.color}99`]}
                  style={styles.actionGradient}
                >
                  <Icon name={action.icon as any} size={28} color="white" />
                  <Text style={styles.actionTitle}>{action.title}</Text>
                </LinearGradient>
              </TouchableOpacity>
            ))}
          </View>
        </View>

        {/* Recent Analyses */}
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>Análisis Recientes</Text>
          <View style={styles.analysesContainer}>
            {recentAnalyses.map((analysis) => (
              <TouchableOpacity
                key={analysis.id}
                style={styles.analysisCard}
                onPress={() => navigation.navigate('Análisis')}
              >
                <View style={styles.analysisContent}>
                  <View style={styles.analysisHeader}>
                    <Icon 
                      name={analysis.status === 'completed' ? 'checkmark-circle' : 'warning'} 
                      size={20} 
                      color={analysis.status === 'completed' ? '#03DAC6' : '#FFA726'} 
                    />
                    <Text style={styles.analysisTitle}>{analysis.title}</Text>
                  </View>
                  <Text style={styles.analysisTime}>{analysis.timestamp}</Text>
                  <View style={styles.analysisStats}>
                    <View style={styles.analysisStat}>
                      <Icon name="speedometer" size={16} color="#BB86FC" />
                      <Text style={styles.analysisStatText}>{analysis.accuracy}</Text>
                    </View>
                    <View style={styles.analysisStat}>
                      <Icon name="time" size={16} color="#BB86FC" />
                      <Text style={styles.analysisStatText}>{analysis.duration}</Text>
                    </View>
                  </View>
                </View>
                <Icon name="chevron-forward" size={20} color="#666" />
              </TouchableOpacity>
            ))}
          </View>
        </View>

        {/* Today's Recommendation */}
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>Recomendación de Hoy</Text>
          <TouchableOpacity 
            style={styles.recommendationCard}
            onPress={() => navigation.navigate('Grabación')}
          >
            <LinearGradient
              colors={['#667eea', '#764ba2']}
              style={styles.recommendationGradient}
            >
              <View style={styles.recommendationContent}>
                <Icon name="bulb" size={32} color="white" style={styles.recommendationIcon} />
                <View style={styles.recommendationText}>
                  <Text style={styles.recommendationTitle}>Analiza tu técnica de sentadilla</Text>
                  <Text style={styles.recommendationDetails}>
                    Graba una serie de sentadillas para obtener feedback instantáneo sobre tu forma
                  </Text>
                </View>
              </View>
              <Icon name="arrow-forward" size={24} color="white" />
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
    backgroundColor: '#121212',
  },
  header: {
    paddingTop: 20,
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
    color: '#AAAAAA',
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
    color: '#FFFFFF',
    marginBottom: 15,
  },
  statsGrid: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    justifyContent: 'space-between',
  },
  statCard: {
    backgroundColor: '#1F1F1F',
    borderRadius: 12,
    padding: 16,
    width: (width - 50) / 2,
    marginBottom: 12,
    borderLeftWidth: 4,
    elevation: 3,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.3,
    shadowRadius: 3,
  },
  statHeader: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 8,
  },
  statTitle: {
    fontSize: 14,
    color: '#AAAAAA',
    marginLeft: 8,
    fontWeight: '500',
  },
  statValue: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#FFFFFF',
    marginBottom: 4,
  },
  statTrend: {
    fontSize: 12,
    color: '#03DAC6',
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
  analysesContainer: {
    backgroundColor: '#1F1F1F',
    borderRadius: 12,
    padding: 4,
  },
  analysisCard: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingVertical: 16,
    paddingHorizontal: 16,
    borderBottomWidth: 1,
    borderBottomColor: '#333333',
  },
  analysisContent: {
    flex: 1,
  },
  analysisHeader: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 4,
  },
  analysisTitle: {
    fontSize: 16,
    fontWeight: '600',
    color: '#FFFFFF',
    marginLeft: 8,
  },
  analysisTime: {
    fontSize: 12,
    color: '#AAAAAA',
    marginBottom: 8,
  },
  analysisStats: {
    flexDirection: 'row',
    gap: 16,
  },
  analysisStat: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 4,
  },
  analysisStatText: {
    fontSize: 12,
    color: '#AAAAAA',
  },
  recommendationCard: {
    borderRadius: 12,
    overflow: 'hidden',
    elevation: 3,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.3,
    shadowRadius: 3,
  },
  recommendationGradient: {
    flexDirection: 'row',
    alignItems: 'center',
    padding: 20,
  },
  recommendationContent: {
    flex: 1,
    flexDirection: 'row',
    alignItems: 'center',
  },
  recommendationIcon: {
    marginRight: 16,
  },
  recommendationText: {
    flex: 1,
  },
  recommendationTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    color: 'white',
    marginBottom: 4,
  },
  recommendationDetails: {
    fontSize: 14,
    color: 'rgba(255, 255, 255, 0.8)',
  },
});