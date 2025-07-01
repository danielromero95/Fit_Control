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

interface AnalysisResult {
  id: string;
  exercise: string;
  date: string;
  accuracy: number;
  duration: number;
  keyPoints: KeyPoint[];
  feedback: string[];
  improvements: string[];
}

interface KeyPoint {
  name: string;
  accuracy: number;
  status: 'good' | 'warning' | 'error';
}

export const AnalysisScreen = ({ navigation }: any) => {
  const [selectedAnalysis, setSelectedAnalysis] = useState<AnalysisResult | null>(null);
  const [analyses, setAnalyses] = useState<AnalysisResult[]>([]);

  useEffect(() => {
    // Simular datos de análisis
    const mockAnalyses: AnalysisResult[] = [
      {
        id: '1',
        exercise: 'Sentadilla',
        date: '2024-01-15',
        accuracy: 92,
        duration: 45,
        keyPoints: [
          { name: 'Posición de rodillas', accuracy: 95, status: 'good' },
          { name: 'Profundidad', accuracy: 88, status: 'warning' },
          { name: 'Espalda recta', accuracy: 96, status: 'good' },
          { name: 'Posición de pies', accuracy: 90, status: 'good' },
        ],
        feedback: [
          'Excelente mantenimiento de la posición de la espalda',
          'Las rodillas se mantienen alineadas correctamente',
          'Buena estabilidad general durante el movimiento'
        ],
        improvements: [
          'Intentar profundizar un poco más en la sentadilla',
          'Mantener más tiempo la posición inferior'
        ]
      },
      {
        id: '2',
        exercise: 'Press Banca',
        date: '2024-01-14',
        accuracy: 85,
        duration: 80,
        keyPoints: [
          { name: 'Arco natural', accuracy: 82, status: 'warning' },
          { name: 'Trayectoria barra', accuracy: 88, status: 'good' },
          { name: 'Posición omóplatos', accuracy: 90, status: 'good' },
          { name: 'Timing', accuracy: 80, status: 'warning' },
        ],
        feedback: [
          'Buena trayectoria de la barra',
          'Posición de omóplatos correcta'
        ],
        improvements: [
          'Trabajar en mantener un arco más consistente',
          'Mejorar el timing de la fase excéntrica'
        ]
      }
    ];
    
    setAnalyses(mockAnalyses);
    if (mockAnalyses.length > 0) {
      setSelectedAnalysis(mockAnalyses[0]);
    }
  }, []);

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'good': return '#03DAC6';
      case 'warning': return '#FFA726';
      case 'error': return '#CF6679';
      default: return '#AAAAAA';
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'good': return 'checkmark-circle';
      case 'warning': return 'warning';
      case 'error': return 'close-circle';
      default: return 'help-circle';
    }
  };

  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    return date.toLocaleDateString('es-ES', {
      day: 'numeric',
      month: 'long',
      year: 'numeric'
    });
  };

  if (!selectedAnalysis) {
    return (
      <View style={styles.emptyContainer}>
        <Icon name="analytics" size={80} color="#BB86FC" />
        <Text style={styles.emptyTitle}>No hay análisis disponibles</Text>
        <Text style={styles.emptyText}>
          Graba un video en la sección de Grabación para obtener tu primer análisis de técnica
        </Text>
        <TouchableOpacity 
          style={styles.emptyButton}
          onPress={() => navigation.navigate('Grabación')}
        >
          <Text style={styles.emptyButtonText}>Grabar Video</Text>
        </TouchableOpacity>
      </View>
    );
  }

  return (
    <View style={styles.container}>
      <StatusBar barStyle="light-content" backgroundColor="#121212" />
      
      {/* Header */}
      <LinearGradient
        colors={['#1F1F1F', '#2C2C2C', '#1F1F1F']}
        style={styles.header}
      >
        <View style={styles.headerContent}>
          <View>
            <Text style={styles.exerciseTitle}>{selectedAnalysis.exercise}</Text>
            <Text style={styles.dateText}>{formatDate(selectedAnalysis.date)}</Text>
          </View>
          <View style={styles.accuracyBadge}>
            <Text style={styles.accuracyText}>{selectedAnalysis.accuracy}%</Text>
            <Text style={styles.accuracyLabel}>Precisión</Text>
          </View>
        </View>
      </LinearGradient>

      <ScrollView style={styles.content} showsVerticalScrollIndicator={false}>
        {/* Quick Stats */}
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>Resumen</Text>
          <View style={styles.statsRow}>
            <View style={styles.statItem}>
              <Icon name="time" size={24} color="#BB86FC" />
              <Text style={styles.statValue}>{selectedAnalysis.duration}s</Text>
              <Text style={styles.statLabel}>Duración</Text>
            </View>
            <View style={styles.statItem}>
              <Icon name="checkmark-circle" size={24} color="#03DAC6" />
              <Text style={styles.statValue}>
                {selectedAnalysis.keyPoints.filter(kp => kp.status === 'good').length}/
                {selectedAnalysis.keyPoints.length}
              </Text>
              <Text style={styles.statLabel}>Puntos Correctos</Text>
            </View>
            <View style={styles.statItem}>
              <Icon name="trending-up" size={24} color="#FFA726" />
              <Text style={styles.statValue}>
                {selectedAnalysis.improvements.length}
              </Text>
              <Text style={styles.statLabel}>Mejoras</Text>
            </View>
          </View>
        </View>

        {/* Key Points Analysis */}
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>Análisis de Puntos Clave</Text>
          <View style={styles.keyPointsContainer}>
            {selectedAnalysis.keyPoints.map((keyPoint, index) => (
              <View key={index} style={styles.keyPointCard}>
                <View style={styles.keyPointHeader}>
                  <Icon 
                    name={getStatusIcon(keyPoint.status)} 
                    size={20} 
                    color={getStatusColor(keyPoint.status)} 
                  />
                  <Text style={styles.keyPointName}>{keyPoint.name}</Text>
                  <Text style={styles.keyPointAccuracy}>{keyPoint.accuracy}%</Text>
                </View>
                <View style={styles.progressBar}>
                  <View 
                    style={[
                      styles.progressFill,
                      { 
                        width: `${keyPoint.accuracy}%`,
                        backgroundColor: getStatusColor(keyPoint.status)
                      }
                    ]} 
                  />
                </View>
              </View>
            ))}
          </View>
        </View>

        {/* Positive Feedback */}
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>Lo que haces bien</Text>
          <View style={styles.feedbackContainer}>
            {selectedAnalysis.feedback.map((item, index) => (
              <View key={index} style={styles.feedbackItem}>
                <Icon name="checkmark-circle" size={16} color="#03DAC6" />
                <Text style={styles.feedbackText}>{item}</Text>
              </View>
            ))}
          </View>
        </View>

        {/* Improvements */}
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>Oportunidades de mejora</Text>
          <View style={styles.improvementsContainer}>
            {selectedAnalysis.improvements.map((item, index) => (
              <View key={index} style={styles.improvementItem}>
                <Icon name="bulb" size={16} color="#FFA726" />
                <Text style={styles.improvementText}>{item}</Text>
              </View>
            ))}
          </View>
        </View>

        {/* Actions */}
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>Acciones</Text>
          <View style={styles.actionsContainer}>
            <TouchableOpacity 
              style={styles.actionButton}
              onPress={() => navigation.navigate('Grabación')}
            >
              <LinearGradient
                colors={['#BB86FC', '#9C64E8']}
                style={styles.actionGradient}
              >
                <Icon name="videocam" size={24} color="white" />
                <Text style={styles.actionButtonText}>Nueva Grabación</Text>
              </LinearGradient>
            </TouchableOpacity>
            
            <TouchableOpacity 
              style={styles.actionButton}
              onPress={() => navigation.navigate('Historial')}
            >
              <LinearGradient
                colors={['#03DAC6', '#00BCD4']}
                style={styles.actionGradient}
              >
                <Icon name="time" size={24} color="white" />
                <Text style={styles.actionButtonText}>Ver Historial</Text>
              </LinearGradient>
            </TouchableOpacity>
          </View>
        </View>

        {/* Analysis Selection */}
        {analyses.length > 1 && (
          <View style={styles.section}>
            <Text style={styles.sectionTitle}>Otros análisis</Text>
            <ScrollView horizontal showsHorizontalScrollIndicator={false}>
              {analyses.map((analysis) => (
                <TouchableOpacity
                  key={analysis.id}
                  style={[
                    styles.analysisChip,
                    selectedAnalysis.id === analysis.id && styles.analysisChipSelected
                  ]}
                  onPress={() => setSelectedAnalysis(analysis)}
                >
                  <Text style={[
                    styles.analysisChipText,
                    selectedAnalysis.id === analysis.id && styles.analysisChipTextSelected
                  ]}>
                    {analysis.exercise}
                  </Text>
                  <Text style={styles.analysisChipAccuracy}>{analysis.accuracy}%</Text>
                </TouchableOpacity>
              ))}
            </ScrollView>
          </View>
        )}
      </ScrollView>
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#121212',
  },
  emptyContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    backgroundColor: '#121212',
    padding: 20,
  },
  emptyTitle: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#FFFFFF',
    marginTop: 20,
    marginBottom: 10,
    textAlign: 'center',
  },
  emptyText: {
    fontSize: 16,
    color: '#AAAAAA',
    textAlign: 'center',
    marginBottom: 30,
    lineHeight: 24,
  },
  emptyButton: {
    backgroundColor: '#BB86FC',
    paddingHorizontal: 30,
    paddingVertical: 15,
    borderRadius: 25,
  },
  emptyButtonText: {
    color: 'white',
    fontSize: 16,
    fontWeight: 'bold',
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
  exerciseTitle: {
    fontSize: 24,
    fontWeight: 'bold',
    color: 'white',
  },
  dateText: {
    fontSize: 14,
    color: '#AAAAAA',
    marginTop: 4,
  },
  accuracyBadge: {
    backgroundColor: 'rgba(187, 134, 252, 0.2)',
    paddingHorizontal: 16,
    paddingVertical: 8,
    borderRadius: 12,
    alignItems: 'center',
  },
  accuracyText: {
    fontSize: 20,
    fontWeight: 'bold',
    color: '#BB86FC',
  },
  accuracyLabel: {
    fontSize: 12,
    color: '#AAAAAA',
    marginTop: 2,
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
  statsRow: {
    flexDirection: 'row',
    justifyContent: 'space-around',
    backgroundColor: '#1F1F1F',
    borderRadius: 12,
    paddingVertical: 20,
  },
  statItem: {
    alignItems: 'center',
  },
  statValue: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#FFFFFF',
    marginTop: 8,
  },
  statLabel: {
    fontSize: 12,
    color: '#AAAAAA',
    marginTop: 4,
  },
  keyPointsContainer: {
    backgroundColor: '#1F1F1F',
    borderRadius: 12,
    padding: 16,
  },
  keyPointCard: {
    marginBottom: 16,
  },
  keyPointHeader: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 8,
  },
  keyPointName: {
    flex: 1,
    fontSize: 16,
    color: '#FFFFFF',
    marginLeft: 8,
  },
  keyPointAccuracy: {
    fontSize: 14,
    fontWeight: 'bold',
    color: '#AAAAAA',
  },
  progressBar: {
    height: 6,
    backgroundColor: '#333333',
    borderRadius: 3,
    marginLeft: 28,
  },
  progressFill: {
    height: '100%',
    borderRadius: 3,
  },
  feedbackContainer: {
    backgroundColor: '#1F1F1F',
    borderRadius: 12,
    padding: 16,
  },
  feedbackItem: {
    flexDirection: 'row',
    alignItems: 'flex-start',
    marginBottom: 12,
  },
  feedbackText: {
    flex: 1,
    fontSize: 14,
    color: '#FFFFFF',
    marginLeft: 8,
    lineHeight: 20,
  },
  improvementsContainer: {
    backgroundColor: '#1F1F1F',
    borderRadius: 12,
    padding: 16,
  },
  improvementItem: {
    flexDirection: 'row',
    alignItems: 'flex-start',
    marginBottom: 12,
  },
  improvementText: {
    flex: 1,
    fontSize: 14,
    color: '#FFFFFF',
    marginLeft: 8,
    lineHeight: 20,
  },
  actionsContainer: {
    flexDirection: 'row',
    gap: 12,
  },
  actionButton: {
    flex: 1,
    borderRadius: 12,
    overflow: 'hidden',
  },
  actionGradient: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    paddingVertical: 16,
    paddingHorizontal: 20,
  },
  actionButtonText: {
    color: 'white',
    fontSize: 14,
    fontWeight: 'bold',
    marginLeft: 8,
  },
  analysisChip: {
    backgroundColor: '#1F1F1F',
    paddingHorizontal: 16,
    paddingVertical: 12,
    borderRadius: 20,
    marginRight: 12,
    alignItems: 'center',
    minWidth: 100,
  },
  analysisChipSelected: {
    backgroundColor: '#BB86FC',
  },
  analysisChipText: {
    color: '#AAAAAA',
    fontSize: 14,
    fontWeight: '500',
  },
  analysisChipTextSelected: {
    color: 'white',
  },
  analysisChipAccuracy: {
    color: '#FFFFFF',
    fontSize: 12,
    marginTop: 2,
  },
});