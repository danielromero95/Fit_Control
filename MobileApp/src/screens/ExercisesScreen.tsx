import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  TouchableOpacity,
  TextInput,
  FlatList,
  Dimensions,
  Image,
} from 'react-native';
import { Ionicons } from '@expo/vector-icons';

const { width } = Dimensions.get('window');

interface Exercise {
  id: string;
  name: string;
  muscleGroup: string;
  equipment: string;
  difficulty: 'Principiante' | 'Intermedio' | 'Avanzado';
  description: string;
  image?: string;
  sets?: number;
  reps?: string;
}

export const ExercisesScreen = ({ navigation }: any) => {
  const [exercises] = useState<Exercise[]>([
    {
      id: '1',
      name: 'Press de Banca',
      muscleGroup: 'Pecho',
      equipment: 'Barra',
      difficulty: 'Intermedio',
      description: 'Ejercicio fundamental para el desarrollo del pecho, hombros y tríceps.',
      sets: 4,
      reps: '8-12',
    },
    {
      id: '2',
      name: 'Sentadillas',
      muscleGroup: 'Piernas',
      equipment: 'Barra',
      difficulty: 'Principiante',
      description: 'Ejercicio compuesto excelente para piernas y glúteos.',
      sets: 3,
      reps: '12-15',
    },
    {
      id: '3',
      name: 'Peso Muerto',
      muscleGroup: 'Espalda',
      equipment: 'Barra',
      difficulty: 'Avanzado',
      description: 'Ejercicio completo que trabaja múltiples grupos musculares.',
      sets: 5,
      reps: '5-8',
    },
    {
      id: '4',
      name: 'Press Militar',
      muscleGroup: 'Hombros',
      equipment: 'Barra',
      difficulty: 'Intermedio',
      description: 'Desarrollo de fuerza y masa muscular en hombros.',
      sets: 4,
      reps: '8-10',
    },
    {
      id: '5',
      name: 'Dominadas',
      muscleGroup: 'Espalda',
      equipment: 'Peso Corporal',
      difficulty: 'Intermedio',
      description: 'Excelente ejercicio para desarrollar la espalda y bíceps.',
      sets: 3,
      reps: '6-12',
    },
    {
      id: '6',
      name: 'Flexiones',
      muscleGroup: 'Pecho',
      equipment: 'Peso Corporal',
      difficulty: 'Principiante',
      description: 'Ejercicio básico para el desarrollo del pecho y brazos.',
      sets: 3,
      reps: '10-20',
    },
  ]);

  const [searchQuery, setSearchQuery] = useState('');
  const [selectedFilter, setSelectedFilter] = useState('Todos');
  const [filteredExercises, setFilteredExercises] = useState<Exercise[]>(exercises);

  const muscleGroups = ['Todos', 'Pecho', 'Espalda', 'Piernas', 'Hombros', 'Brazos'];

  const difficultyColors = {
    'Principiante': '#27ae60',
    'Intermedio': '#f39c12',
    'Avanzado': '#e74c3c',
  };

  const equipmentIcons = {
    'Barra': 'barbell-outline',
    'Mancuernas': 'fitness-outline',
    'Peso Corporal': 'body-outline',
    'Máquina': 'hardware-chip-outline',
  };

  useEffect(() => {
    filterExercises();
  }, [searchQuery, selectedFilter]);

  const filterExercises = () => {
    let filtered = exercises;

    if (searchQuery) {
      filtered = filtered.filter(exercise =>
        exercise.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
        exercise.muscleGroup.toLowerCase().includes(searchQuery.toLowerCase())
      );
    }

    if (selectedFilter !== 'Todos') {
      filtered = filtered.filter(exercise => exercise.muscleGroup === selectedFilter);
    }

    setFilteredExercises(filtered);
  };

  const renderExerciseCard = ({ item }: { item: Exercise }) => (
    <TouchableOpacity
      style={styles.exerciseCard}
      onPress={() => navigation.navigate('ExerciseDetail', { exercise: item })}
      activeOpacity={0.7}
    >
      <View style={styles.exerciseHeader}>
        <View style={styles.exerciseInfo}>
          <Text style={styles.exerciseName}>{item.name}</Text>
          <View style={styles.exerciseMeta}>
            <View style={styles.metaItem}>
              <Ionicons name="fitness" size={14} color="#7f8c8d" />
              <Text style={styles.metaText}>{item.muscleGroup}</Text>
            </View>
            <View style={styles.metaItem}>
              <Ionicons 
                name={equipmentIcons[item.equipment as keyof typeof equipmentIcons] as any} 
                size={14} 
                color="#7f8c8d" 
              />
              <Text style={styles.metaText}>{item.equipment}</Text>
            </View>
          </View>
        </View>
        <View style={[styles.difficultyBadge, { backgroundColor: difficultyColors[item.difficulty] }]}>
          <Text style={styles.difficultyText}>{item.difficulty}</Text>
        </View>
      </View>

      <Text style={styles.exerciseDescription} numberOfLines={2}>
        {item.description}
      </Text>

      <View style={styles.exerciseFooter}>
        <View style={styles.setsReps}>
          <Text style={styles.setsRepsText}>
            {item.sets} series • {item.reps} reps
          </Text>
        </View>
        <TouchableOpacity style={styles.startButton}>
          <Text style={styles.startButtonText}>Iniciar</Text>
          <Ionicons name="play" size={14} color="white" />
        </TouchableOpacity>
      </View>
    </TouchableOpacity>
  );

  const renderFilterChip = (filter: string) => (
    <TouchableOpacity
      key={filter}
      style={[
        styles.filterChip,
        selectedFilter === filter && styles.activeFilterChip
      ]}
      onPress={() => setSelectedFilter(filter)}
    >
      <Text style={[
        styles.filterText,
        selectedFilter === filter && styles.activeFilterText
      ]}>
        {filter}
      </Text>
    </TouchableOpacity>
  );

  return (
    <View style={styles.container}>
      {/* Search Header */}
      <View style={styles.searchHeader}>
        <View style={styles.searchContainer}>
          <Ionicons name="search" size={20} color="#7f8c8d" style={styles.searchIcon} />
          <TextInput
            style={styles.searchInput}
            placeholder="Buscar ejercicios..."
            value={searchQuery}
            onChangeText={setSearchQuery}
            placeholderTextColor="#bdc3c7"
          />
          {searchQuery.length > 0 && (
            <TouchableOpacity
              onPress={() => setSearchQuery('')}
              style={styles.clearButton}
            >
              <Ionicons name="close" size={20} color="#7f8c8d" />
            </TouchableOpacity>
          )}
        </View>
      </View>

      {/* Filter Chips */}
      <ScrollView
        horizontal
        showsHorizontalScrollIndicator={false}
        style={styles.filtersContainer}
        contentContainerStyle={styles.filtersContent}
      >
        {muscleGroups.map(renderFilterChip)}
      </ScrollView>

      {/* Results Header */}
      <View style={styles.resultsHeader}>
        <Text style={styles.resultsText}>
          {filteredExercises.length} ejercicio{filteredExercises.length !== 1 ? 's' : ''} encontrado{filteredExercises.length !== 1 ? 's' : ''}
        </Text>
        <TouchableOpacity style={styles.sortButton}>
          <Ionicons name="swap-vertical" size={16} color="#7f8c8d" />
          <Text style={styles.sortText}>Ordenar</Text>
        </TouchableOpacity>
      </View>

      {/* Exercise List */}
      <FlatList
        data={filteredExercises}
        renderItem={renderExerciseCard}
        keyExtractor={(item) => item.id}
        contentContainerStyle={styles.exercisesList}
        showsVerticalScrollIndicator={false}
        ItemSeparatorComponent={() => <View style={styles.separator} />}
      />

      {/* Floating Action Button */}
      <TouchableOpacity style={styles.fab} activeOpacity={0.8}>
        <Ionicons name="add" size={24} color="white" />
      </TouchableOpacity>
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f8f9fa',
  },
  searchHeader: {
    backgroundColor: 'white',
    paddingHorizontal: 20,
    paddingVertical: 15,
    borderBottomWidth: 1,
    borderBottomColor: '#ecf0f1',
  },
  searchContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#f8f9fa',
    borderRadius: 12,
    paddingHorizontal: 15,
    height: 45,
  },
  searchIcon: {
    marginRight: 10,
  },
  searchInput: {
    flex: 1,
    fontSize: 16,
    color: '#2c3e50',
  },
  clearButton: {
    padding: 5,
  },
  filtersContainer: {
    backgroundColor: 'white',
    borderBottomWidth: 1,
    borderBottomColor: '#ecf0f1',
  },
  filtersContent: {
    paddingHorizontal: 20,
    paddingVertical: 10,
  },
  filterChip: {
    backgroundColor: '#ecf0f1',
    paddingHorizontal: 16,
    paddingVertical: 8,
    borderRadius: 20,
    marginRight: 10,
  },
  activeFilterChip: {
    backgroundColor: '#3498db',
  },
  filterText: {
    fontSize: 14,
    color: '#7f8c8d',
    fontWeight: '500',
  },
  activeFilterText: {
    color: 'white',
  },
  resultsHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingHorizontal: 20,
    paddingVertical: 15,
    backgroundColor: 'white',
    borderBottomWidth: 1,
    borderBottomColor: '#ecf0f1',
  },
  resultsText: {
    fontSize: 14,
    color: '#7f8c8d',
    fontWeight: '500',
  },
  sortButton: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  sortText: {
    fontSize: 14,
    color: '#7f8c8d',
    marginLeft: 5,
    fontWeight: '500',
  },
  exercisesList: {
    padding: 20,
  },
  exerciseCard: {
    backgroundColor: 'white',
    borderRadius: 12,
    padding: 16,
    elevation: 3,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 3,
  },
  exerciseHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'flex-start',
    marginBottom: 12,
  },
  exerciseInfo: {
    flex: 1,
  },
  exerciseName: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#2c3e50',
    marginBottom: 6,
  },
  exerciseMeta: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  metaItem: {
    flexDirection: 'row',
    alignItems: 'center',
    marginRight: 15,
  },
  metaText: {
    fontSize: 12,
    color: '#7f8c8d',
    marginLeft: 4,
  },
  difficultyBadge: {
    paddingHorizontal: 8,
    paddingVertical: 4,
    borderRadius: 12,
  },
  difficultyText: {
    fontSize: 10,
    color: 'white',
    fontWeight: 'bold',
  },
  exerciseDescription: {
    fontSize: 14,
    color: '#7f8c8d',
    lineHeight: 20,
    marginBottom: 12,
  },
  exerciseFooter: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
  },
  setsReps: {
    flex: 1,
  },
  setsRepsText: {
    fontSize: 12,
    color: '#3498db',
    fontWeight: '600',
  },
  startButton: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#27ae60',
    paddingHorizontal: 12,
    paddingVertical: 6,
    borderRadius: 15,
  },
  startButtonText: {
    color: 'white',
    fontSize: 12,
    fontWeight: 'bold',
    marginRight: 4,
  },
  separator: {
    height: 12,
  },
  fab: {
    position: 'absolute',
    bottom: 20,
    right: 20,
    width: 56,
    height: 56,
    borderRadius: 28,
    backgroundColor: '#3498db',
    justifyContent: 'center',
    alignItems: 'center',
    elevation: 6,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 3 },
    shadowOpacity: 0.3,
    shadowRadius: 4,
  },
});