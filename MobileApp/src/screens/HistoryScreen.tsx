import React, { useState } from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  TouchableOpacity,
  StatusBar,
} from 'react-native';
import Icon from 'react-native-vector-icons/Ionicons';

export const HistoryScreen = ({ navigation }: any) => {
  const [historyData] = useState([
    {
      id: '1',
      exercise: 'Sentadilla',
      date: '2024-01-15',
      accuracy: 92,
      duration: 45,
      status: 'completed'
    },
    {
      id: '2',
      exercise: 'Press Banca',
      date: '2024-01-14',
      accuracy: 85,
      duration: 80,
      status: 'completed'
    },
    {
      id: '3',
      exercise: 'Peso Muerto',
      date: '2024-01-13',
      accuracy: 78,
      duration: 65,
      status: 'needs_review'
    },
  ]);

  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    return date.toLocaleDateString('es-ES', {
      day: 'numeric',
      month: 'short',
      year: 'numeric'
    });
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'completed': return '#03DAC6';
      case 'needs_review': return '#FFA726';
      default: return '#AAAAAA';
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'completed': return 'checkmark-circle';
      case 'needs_review': return 'warning';
      default: return 'help-circle';
    }
  };

  return (
    <View style={styles.container}>
      <StatusBar barStyle="light-content" backgroundColor="#121212" />
      
      <ScrollView style={styles.content} showsVerticalScrollIndicator={false}>
        <View style={styles.header}>
          <Text style={styles.title}>Historial de Análisis</Text>
          <Text style={styles.subtitle}>{historyData.length} análisis realizados</Text>
        </View>

        {historyData.map((item) => (
          <TouchableOpacity
            key={item.id}
            style={styles.historyCard}
            onPress={() => navigation.navigate('Análisis')}
          >
            <View style={styles.cardHeader}>
              <View style={styles.exerciseInfo}>
                <Text style={styles.exerciseName}>{item.exercise}</Text>
                <Text style={styles.exerciseDate}>{formatDate(item.date)}</Text>
              </View>
              <View style={styles.statusContainer}>
                <Icon
                  name={getStatusIcon(item.status)}
                  size={20}
                  color={getStatusColor(item.status)}
                />
              </View>
            </View>
            
            <View style={styles.cardStats}>
              <View style={styles.statItem}>
                <Icon name="speedometer" size={16} color="#BB86FC" />
                <Text style={styles.statText}>{item.accuracy}% precisión</Text>
              </View>
              <View style={styles.statItem}>
                <Icon name="time" size={16} color="#BB86FC" />
                <Text style={styles.statText}>{item.duration}s duración</Text>
              </View>
            </View>
          </TouchableOpacity>
        ))}

        <TouchableOpacity
          style={styles.newRecordingButton}
          onPress={() => navigation.navigate('Grabación')}
        >
          <Icon name="add-circle" size={24} color="white" />
          <Text style={styles.newRecordingText}>Nueva Grabación</Text>
        </TouchableOpacity>
      </ScrollView>
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#121212',
  },
  content: {
    flex: 1,
    paddingHorizontal: 20,
  },
  header: {
    paddingVertical: 20,
  },
  title: {
    fontSize: 28,
    fontWeight: 'bold',
    color: '#FFFFFF',
    marginBottom: 4,
  },
  subtitle: {
    fontSize: 16,
    color: '#AAAAAA',
  },
  historyCard: {
    backgroundColor: '#1F1F1F',
    borderRadius: 12,
    padding: 16,
    marginBottom: 12,
    borderLeftWidth: 4,
    borderLeftColor: '#BB86FC',
  },
  cardHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 12,
  },
  exerciseInfo: {
    flex: 1,
  },
  exerciseName: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#FFFFFF',
    marginBottom: 4,
  },
  exerciseDate: {
    fontSize: 14,
    color: '#AAAAAA',
  },
  statusContainer: {
    padding: 4,
  },
  cardStats: {
    flexDirection: 'row',
    gap: 16,
  },
  statItem: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 4,
  },
  statText: {
    fontSize: 14,
    color: '#AAAAAA',
  },
  newRecordingButton: {
    backgroundColor: '#BB86FC',
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    paddingVertical: 16,
    borderRadius: 12,
    marginTop: 20,
    marginBottom: 40,
  },
  newRecordingText: {
    color: 'white',
    fontSize: 16,
    fontWeight: 'bold',
    marginLeft: 8,
  },
});