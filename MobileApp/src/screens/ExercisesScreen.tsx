/**
 * Pantalla de Ejercicios - Fit_Control
 * 
 * Incluye:
 * - Biblioteca completa de ejercicios
 * - Filtros por grupo muscular y equipo
 * - Búsqueda y favoritos
 * - Vista previa con análisis de video
 */

import React, { useState, useEffect, useCallback } from 'react';
import {
  View,
  ScrollView,
  StyleSheet,
  RefreshControl,
  FlatList,
  Image,
  Dimensions,
} from 'react-native';
import {
  Card,
  Title,
  Paragraph,
  Button,
  Searchbar,
  Chip,
  Avatar,
  Surface,
  Badge,
  IconButton,
  useTheme,
  ActivityIndicator,
  Modal,
  Portal,
} from 'react-native-paper';
import Icon from 'react-native-vector-icons/MaterialCommunityIcons';
import { useFocusEffect } from '@react-navigation/native';

import { useAuthStore } from '../store/authStore';
import { api, getErrorMessage } from '../services/apiClient';
import { Exercise, ExerciseFilters, PaginatedResponse } from '../types/api';
import Toast from 'react-native-toast-message';

const MUSCLE_GROUPS = [
  { key: 'all', label: 'Todos', value: undefined },
  { key: 'chest', label: 'Pecho', value: 'chest' },
  { key: 'back', label: 'Espalda', value: 'back' },
  { key: 'shoulders', label: 'Hombros', value: 'shoulders' },
  { key: 'arms', label: 'Brazos', value: 'arms' },
  { key: 'legs', label: 'Piernas', value: 'legs' },
  { key: 'abs', label: 'Abdomen', value: 'abs' },
  { key: 'cardio', label: 'Cardio', value: 'cardio' },
];

const EQUIPMENT_FILTERS = [
  { key: 'all', label: 'Todo', value: undefined },
  { key: 'bodyweight', label: 'Peso corporal', value: 'bodyweight' },
  { key: 'dumbbells', label: 'Mancuernas', value: 'dumbbells' },
  { key: 'barbell', label: 'Barra', value: 'barbell' },
  { key: 'machine', label: 'Máquina', value: 'machine' },
  { key: 'resistance_band', label: 'Banda elástica', value: 'resistance_band' },
];

const { width } = Dimensions.get('window');
const CARD_WIDTH = (width - 48) / 2;

export const ExercisesScreen: React.FC = () => {
  const theme = useTheme();
  const { user } = useAuthStore();
  
  const [searchQuery, setSearchQuery] = useState('');
  const [exercises, setExercises] = useState<Exercise[]>([]);
  const [loading, setLoading] = useState(false);
  const [refreshing, setRefreshing] = useState(false);
  const [hasMore, setHasMore] = useState(true);
  const [page, setPage] = useState(1);
  
  // Filtros
  const [filters, setFilters] = useState<ExerciseFilters>({});
  const [showFilters, setShowFilters] = useState(false);
  
  // Modal de detalles
  const [selectedExercise, setSelectedExercise] = useState<Exercise | null>(null);
  const [showExerciseModal, setShowExerciseModal] = useState(false);

  // Cargar ejercicios
  const loadExercises = useCallback(async (reset = false) => {
    if (loading || (!hasMore && !reset)) return;
    
    try {
      setLoading(true);
      const currentPage = reset ? 1 : page;
      
      const params = {
        page: currentPage,
        ...filters,
        search: searchQuery || undefined,
      };
      
      const response = await api.get<PaginatedResponse<Exercise>>('/exercises/', params);
      
      if (reset) {
        setExercises(response.data.results);
        setPage(2);
      } else {
        setExercises(prev => [...prev, ...response.data.results]);
        setPage(prev => prev + 1);
      }
      
      setHasMore(!!response.data.next);
      
    } catch (error) {
      console.error('Error loading exercises:', error);
      Toast.show({
        type: 'error',
        text1: 'Error',
        text2: getErrorMessage(error),
      });
    } finally {
      setLoading(false);
    }
  }, [searchQuery, filters, loading, hasMore, page]);

  // Cargar datos al cambiar filtros
  useEffect(() => {
    setExercises([]);
    setPage(1);
    setHasMore(true);
    loadExercises(true);
  }, [searchQuery, filters]);

  // Cargar datos al enfocar la pantalla
  useFocusEffect(
    useCallback(() => {
      if (exercises.length === 0) {
        loadExercises(true);
      }
    }, [])
  );

  // Manejar refresh
  const onRefresh = useCallback(async () => {
    setRefreshing(true);
    setExercises([]);
    setPage(1);
    setHasMore(true);
    await loadExercises(true);
    setRefreshing(false);
  }, [loadExercises]);

  // Aplicar filtro
  const applyFilter = (key: string, value: any) => {
    setFilters(prev => ({
      ...prev,
      [key]: value,
    }));
  };

  // Limpiar filtros
  const clearFilters = () => {
    setFilters({});
    setShowFilters(false);
  };

  // Abrir detalles del ejercicio
  const openExerciseDetails = (exercise: Exercise) => {
    setSelectedExercise(exercise);
    setShowExerciseModal(true);
  };

  // Iniciar análisis de video
  const startVideoAnalysis = (exercise: Exercise) => {
    setShowExerciseModal(false);
    // TODO: Navegar a pantalla de análisis de video
    Toast.show({
      type: 'info',
      text1: 'Iniciando análisis de video...',
      text2: `Para ${exercise.name}`,
    });
  };

  // Renderizar filtros
  const renderFilters = () => {
    if (!showFilters) return null;
    
    return (
      <Surface style={styles.filtersContainer} elevation={1}>
        <View style={styles.filterSection}>
          <Paragraph style={styles.filterTitle}>Grupo Muscular</Paragraph>
          <View style={styles.filterChips}>
            {MUSCLE_GROUPS.map(filter => (
              <Chip
                key={filter.key}
                mode={filters.muscle_groups?.includes(filter.value || '') ? 'flat' : 'outlined'}
                onPress={() => {
                  if (filter.value) {
                    const current = filters.muscle_groups || [];
                    const updated = current.includes(filter.value)
                      ? current.filter(g => g !== filter.value)
                      : [...current, filter.value];
                    applyFilter('muscle_groups', updated.length > 0 ? updated : undefined);
                  } else {
                    applyFilter('muscle_groups', undefined);
                  }
                }}
                style={styles.filterChip}
              >
                {filter.label}
              </Chip>
            ))}
          </View>
        </View>
        
        <View style={styles.filterSection}>
          <Paragraph style={styles.filterTitle}>Equipo</Paragraph>
          <View style={styles.filterChips}>
            {EQUIPMENT_FILTERS.map(filter => (
              <Chip
                key={filter.key}
                mode={filters.equipment_needed?.includes(filter.value || '') ? 'flat' : 'outlined'}
                onPress={() => {
                  if (filter.value) {
                    const current = filters.equipment_needed || [];
                    const updated = current.includes(filter.value)
                      ? current.filter(e => e !== filter.value)
                      : [...current, filter.value];
                    applyFilter('equipment_needed', updated.length > 0 ? updated : undefined);
                  } else {
                    applyFilter('equipment_needed', undefined);
                  }
                }}
                style={styles.filterChip}
              >
                {filter.label}
              </Chip>
            ))}
          </View>
        </View>
        
        <View style={styles.filterActions}>
          <Button mode="outlined" onPress={clearFilters} compact>
            Limpiar
          </Button>
          <Button 
            mode="contained" 
            onPress={() => setShowFilters(false)}
            compact
          >
            Aplicar
          </Button>
        </View>
      </Surface>
    );
  };

  // Renderizar ejercicio
  const renderExercise = ({ item: exercise }: { item: Exercise }) => (
    <Card style={styles.exerciseCard} onPress={() => openExerciseDetails(exercise)}>
      <View style={styles.exerciseImageContainer}>
        {exercise.image_url ? (
          <Image source={{ uri: exercise.image_url }} style={styles.exerciseImage} />
        ) : (
          <Surface style={styles.exerciseImagePlaceholder} elevation={0}>
            <Icon name="dumbbell" size={32} color={theme.colors.outline} />
          </Surface>
        )}
        <View style={styles.exerciseImageOverlay}>
          <Chip
            mode="flat"
            style={[
              styles.difficultyChip,
              { backgroundColor: getDifficultyColor(exercise.difficulty_level) }
            ]}
            textStyle={styles.difficultyText}
          >
            {getDifficultyLabel(exercise.difficulty_level)}
          </Chip>
        </View>
      </View>
      
      <Card.Content style={styles.exerciseContent}>
        <Title style={styles.exerciseTitle} numberOfLines={2}>
          {exercise.name}
        </Title>
        
        <View style={styles.exerciseMuscles}>
          {exercise.muscle_groups.slice(0, 2).map((muscle, index) => (
            <Chip key={index} mode="outlined" compact style={styles.muscleChip}>
              {muscle}
            </Chip>
          ))}
          {exercise.muscle_groups.length > 2 && (
            <Paragraph style={styles.moreMuscles}>
              +{exercise.muscle_groups.length - 2}
            </Paragraph>
          )}
        </View>
        
        <View style={styles.exerciseEquipment}>
          <Icon name="weight-lifter" size={14} color={theme.colors.outline} />
          <Paragraph style={styles.equipmentText}>
            {exercise.equipment_needed[0] || 'Peso corporal'}
          </Paragraph>
        </View>
      </Card.Content>
    </Card>
  );

  // Renderizar modal de detalles
  const renderExerciseModal = () => (
    <Portal>
      <Modal
        visible={showExerciseModal}
        onDismiss={() => setShowExerciseModal(false)}
        contentContainerStyle={styles.modalContainer}
      >
        {selectedExercise && (
          <Surface style={styles.modalContent} elevation={5}>
            <ScrollView>
              {/* Header del modal */}
              <View style={styles.modalHeader}>
                <Title style={styles.modalTitle}>{selectedExercise.name}</Title>
                <IconButton
                  icon="close"
                  onPress={() => setShowExerciseModal(false)}
                />
              </View>
              
              {/* Imagen del ejercicio */}
              {selectedExercise.image_url && (
                <Image 
                  source={{ uri: selectedExercise.image_url }} 
                  style={styles.modalImage} 
                />
              )}
              
              {/* Información básica */}
              <View style={styles.modalSection}>
                <Paragraph style={styles.sectionTitle}>Información</Paragraph>
                <View style={styles.infoGrid}>
                  <View style={styles.infoItem}>
                    <Icon name="target" size={20} color={theme.colors.primary} />
                    <Paragraph style={styles.infoText}>
                      {getDifficultyLabel(selectedExercise.difficulty_level)}
                    </Paragraph>
                  </View>
                  <View style={styles.infoItem}>
                    <Icon name="weight-lifter" size={20} color={theme.colors.primary} />
                    <Paragraph style={styles.infoText}>
                      {selectedExercise.equipment_needed.join(', ') || 'Peso corporal'}
                    </Paragraph>
                  </View>
                </View>
              </View>
              
              {/* Grupos musculares */}
              <View style={styles.modalSection}>
                <Paragraph style={styles.sectionTitle}>Grupos Musculares</Paragraph>
                <View style={styles.muscleGroupsGrid}>
                  {selectedExercise.muscle_groups.map((muscle, index) => (
                    <Chip key={index} mode="flat" style={styles.muscleGroupChip}>
                      {muscle}
                    </Chip>
                  ))}
                </View>
              </View>
              
              {/* Descripción */}
              <View style={styles.modalSection}>
                <Paragraph style={styles.sectionTitle}>Descripción</Paragraph>
                <Paragraph style={styles.description}>
                  {selectedExercise.description}
                </Paragraph>
              </View>
              
              {/* Instrucciones */}
              {selectedExercise.instructions.length > 0 && (
                <View style={styles.modalSection}>
                  <Paragraph style={styles.sectionTitle}>Instrucciones</Paragraph>
                  {selectedExercise.instructions.map((instruction, index) => (
                    <View key={index} style={styles.instructionItem}>
                      <Badge style={styles.stepNumber}>{index + 1}</Badge>
                      <Paragraph style={styles.instructionText}>
                        {instruction}
                      </Paragraph>
                    </View>
                  ))}
                </View>
              )}
              
              {/* Tips */}
              {selectedExercise.tips.length > 0 && (
                <View style={styles.modalSection}>
                  <Paragraph style={styles.sectionTitle}>Tips</Paragraph>
                  {selectedExercise.tips.map((tip, index) => (
                    <View key={index} style={styles.tipItem}>
                      <Icon name="lightbulb-outline" size={16} color={theme.colors.primary} />
                      <Paragraph style={styles.tipText}>{tip}</Paragraph>
                    </View>
                  ))}
                </View>
              )}
              
              {/* Acciones */}
              <View style={styles.modalActions}>
                <Button
                  mode="outlined"
                  onPress={() => setShowExerciseModal(false)}
                  style={styles.modalButton}
                >
                  Cerrar
                </Button>
                <Button
                  mode="contained"
                  icon="video"
                  onPress={() => startVideoAnalysis(selectedExercise)}
                  style={styles.modalButton}
                >
                  Analizar Video
                </Button>
              </View>
            </ScrollView>
          </Surface>
        )}
      </Modal>
    </Portal>
  );

  // Helper functions
  const getDifficultyColor = (difficulty: string) => {
    switch (difficulty) {
      case 'beginner': return '#4CAF50';
      case 'intermediate': return '#FF9800';
      case 'advanced': return '#F44336';
      default: return theme.colors.outline;
    }
  };

  const getDifficultyLabel = (difficulty: string) => {
    switch (difficulty) {
      case 'beginner': return 'Principiante';
      case 'intermediate': return 'Intermedio';
      case 'advanced': return 'Avanzado';
      default: return difficulty;
    }
  };

  const activeFiltersCount = [
    filters.muscle_groups?.length || 0,
    filters.equipment_needed?.length || 0,
    filters.difficulty_level ? 1 : 0,
  ].reduce((sum, count) => sum + count, 0);

  return (
    <View style={styles.container}>
      {/* Header con búsqueda */}
      <Surface style={styles.header} elevation={4}>
        <Searchbar
          placeholder="Buscar ejercicios..."
          onChangeText={setSearchQuery}
          value={searchQuery}
          style={styles.searchBar}
        />
        <IconButton
          icon="tune"
          mode="contained"
          onPress={() => setShowFilters(!showFilters)}
          style={[
            styles.filterButton,
            activeFiltersCount > 0 && { backgroundColor: theme.colors.primary }
          ]}
        />
        {activeFiltersCount > 0 && (
          <Badge style={styles.filterBadge}>
            {activeFiltersCount}
          </Badge>
        )}
      </Surface>

      {/* Filtros */}
      {renderFilters()}

      {/* Lista de ejercicios */}
      <FlatList
        data={exercises}
        renderItem={renderExercise}
        keyExtractor={(item) => item.id.toString()}
        numColumns={2}
        contentContainerStyle={styles.listContainer}
        columnWrapperStyle={styles.row}
        refreshControl={
          <RefreshControl refreshing={refreshing} onRefresh={onRefresh} />
        }
        onEndReached={() => loadExercises()}
        onEndReachedThreshold={0.1}
        ListFooterComponent={
          loading && hasMore ? (
            <View style={styles.loadingFooter}>
              <ActivityIndicator size="small" />
              <Paragraph style={styles.loadingText}>Cargando más ejercicios...</Paragraph>
            </View>
          ) : null
        }
        ListEmptyComponent={
          !loading ? (
            <View style={styles.emptyState}>
              <Icon name="dumbbell" size={64} color={theme.colors.outline} />
              <Paragraph style={styles.emptyText}>
                {searchQuery ? 'No se encontraron ejercicios' : 'No hay ejercicios disponibles'}
              </Paragraph>
              {searchQuery && (
                <Button mode="outlined" onPress={() => setSearchQuery('')}>
                  Limpiar búsqueda
                </Button>
              )}
            </View>
          ) : null
        }
      />

      {/* Modal de detalles */}
      {renderExerciseModal()}
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f5f5f5',
  },
  header: {
    flexDirection: 'row',
    alignItems: 'center',
    padding: 16,
    paddingTop: 8,
    position: 'relative',
  },
  searchBar: {
    flex: 1,
    marginRight: 8,
  },
  filterButton: {
    position: 'relative',
  },
  filterBadge: {
    position: 'absolute',
    top: 4,
    right: 4,
    fontSize: 10,
    zIndex: 1,
  },
  filtersContainer: {
    margin: 16,
    marginTop: 0,
    padding: 16,
    borderRadius: 12,
  },
  filterSection: {
    marginBottom: 16,
  },
  filterTitle: {
    fontSize: 14,
    fontWeight: '600',
    marginBottom: 8,
  },
  filterChips: {
    flexDirection: 'row',
    flexWrap: 'wrap',
  },
  filterChip: {
    marginRight: 8,
    marginBottom: 8,
  },
  filterActions: {
    flexDirection: 'row',
    justifyContent: 'flex-end',
    gap: 8,
  },
  listContainer: {
    padding: 16,
  },
  row: {
    justifyContent: 'space-between',
  },
  exerciseCard: {
    width: CARD_WIDTH,
    marginBottom: 16,
    overflow: 'hidden',
  },
  exerciseImageContainer: {
    position: 'relative',
    height: 120,
  },
  exerciseImage: {
    width: '100%',
    height: '100%',
  },
  exerciseImagePlaceholder: {
    width: '100%',
    height: '100%',
    justifyContent: 'center',
    alignItems: 'center',
    backgroundColor: '#f0f0f0',
  },
  exerciseImageOverlay: {
    position: 'absolute',
    top: 8,
    right: 8,
  },
  difficultyChip: {
    height: 24,
  },
  difficultyText: {
    color: 'white',
    fontSize: 10,
    fontWeight: 'bold',
  },
  exerciseContent: {
    padding: 12,
  },
  exerciseTitle: {
    fontSize: 14,
    fontWeight: 'bold',
    marginBottom: 8,
  },
  exerciseMuscles: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 8,
  },
  muscleChip: {
    marginRight: 4,
    height: 20,
  },
  moreMuscles: {
    fontSize: 10,
    opacity: 0.6,
    marginLeft: 4,
  },
  exerciseEquipment: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  equipmentText: {
    fontSize: 12,
    marginLeft: 4,
    opacity: 0.7,
  },
  modalContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    padding: 16,
  },
  modalContent: {
    width: '100%',
    maxHeight: '90%',
    borderRadius: 16,
    overflow: 'hidden',
  },
  modalHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    padding: 16,
    paddingBottom: 8,
  },
  modalTitle: {
    flex: 1,
    fontSize: 20,
    fontWeight: 'bold',
  },
  modalImage: {
    width: '100%',
    height: 200,
  },
  modalSection: {
    padding: 16,
    paddingTop: 8,
  },
  sectionTitle: {
    fontSize: 16,
    fontWeight: 'bold',
    marginBottom: 12,
  },
  infoGrid: {
    flexDirection: 'row',
    flexWrap: 'wrap',
  },
  infoItem: {
    flexDirection: 'row',
    alignItems: 'center',
    width: '50%',
    marginBottom: 8,
  },
  infoText: {
    marginLeft: 8,
    fontSize: 14,
  },
  muscleGroupsGrid: {
    flexDirection: 'row',
    flexWrap: 'wrap',
  },
  muscleGroupChip: {
    marginRight: 8,
    marginBottom: 8,
  },
  description: {
    lineHeight: 20,
  },
  instructionItem: {
    flexDirection: 'row',
    alignItems: 'flex-start',
    marginBottom: 12,
  },
  stepNumber: {
    marginRight: 12,
    marginTop: 2,
  },
  instructionText: {
    flex: 1,
    lineHeight: 20,
  },
  tipItem: {
    flexDirection: 'row',
    alignItems: 'flex-start',
    marginBottom: 8,
  },
  tipText: {
    flex: 1,
    marginLeft: 8,
    fontSize: 14,
  },
  modalActions: {
    flexDirection: 'row',
    padding: 16,
    gap: 12,
  },
  modalButton: {
    flex: 1,
  },
  loadingFooter: {
    flexDirection: 'row',
    justifyContent: 'center',
    alignItems: 'center',
    padding: 16,
    gridColumn: '1 / -1',
  },
  loadingText: {
    marginLeft: 8,
  },
  emptyState: {
    alignItems: 'center',
    padding: 32,
    gridColumn: '1 / -1',
  },
  emptyText: {
    textAlign: 'center',
    marginTop: 16,
    marginBottom: 24,
    opacity: 0.7,
  },
});

export default ExercisesScreen;