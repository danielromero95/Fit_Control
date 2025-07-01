/**
 * Pantalla de Planes de Entrenamiento - Fit_Control
 * 
 * Incluye:
 * - Lista de planes populares y recomendados
 * - Filtros por dificultad, duración y tipo
 * - Búsqueda de planes
 * - Mis planes seguidos
 * - Detalles y preview de planes
 */

import React, { useState, useEffect, useCallback } from 'react';
import {
  View,
  ScrollView,
  StyleSheet,
  RefreshControl,
  FlatList,
  Image,
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
} from 'react-native-paper';
import Icon from 'react-native-vector-icons/MaterialCommunityIcons';
import { useFocusEffect } from '@react-navigation/native';

import { useAuthStore } from '../store/authStore';
import { api, getErrorMessage } from '../services/apiClient';
import { WorkoutPlan, WorkoutPlanFilters, PaginatedResponse } from '../types/api';
import Toast from 'react-native-toast-message';

interface TabData {
  key: string;
  title: string;
  icon: string;
}

const TABS: TabData[] = [
  { key: 'recommended', title: 'Recomendados', icon: 'star' },
  { key: 'popular', title: 'Populares', icon: 'trending-up' },
  { key: 'following', title: 'Mis Planes', icon: 'heart' },
  { key: 'created', title: 'Creados', icon: 'plus-circle' },
];

const DIFFICULTY_FILTERS = [
  { key: 'all', label: 'Todos', value: undefined },
  { key: 'beginner', label: 'Principiante', value: 'beginner' },
  { key: 'intermediate', label: 'Intermedio', value: 'intermediate' },
  { key: 'advanced', label: 'Avanzado', value: 'advanced' },
];

const DURATION_FILTERS = [
  { key: 'all', label: 'Cualquiera', value: undefined },
  { key: 'short', label: '1-4 semanas', value: 4 },
  { key: 'medium', label: '5-8 semanas', value: 8 },
  { key: 'long', label: '9+ semanas', value: 12 },
];

export const PlansScreen: React.FC = () => {
  const theme = useTheme();
  const { user } = useAuthStore();
  
  const [activeTab, setActiveTab] = useState('recommended');
  const [searchQuery, setSearchQuery] = useState('');
  const [plans, setPlans] = useState<WorkoutPlan[]>([]);
  const [loading, setLoading] = useState(false);
  const [refreshing, setRefreshing] = useState(false);
  const [hasMore, setHasMore] = useState(true);
  const [page, setPage] = useState(1);
  
  // Filtros
  const [filters, setFilters] = useState<WorkoutPlanFilters>({});
  const [showFilters, setShowFilters] = useState(false);

  // Cargar planes según el tab activo
  const loadPlans = useCallback(async (reset = false) => {
    if (loading || (!hasMore && !reset)) return;
    
    try {
      setLoading(true);
      const currentPage = reset ? 1 : page;
      
      let endpoint = '/plans/';
      const params: any = {
        page: currentPage,
        ...filters,
        search: searchQuery || undefined,
      };
      
      switch (activeTab) {
        case 'recommended':
          endpoint = '/plans/recommended/';
          break;
        case 'popular':
          params.ordering = '-followers_count';
          break;
        case 'following':
          endpoint = `/plans/user/${user?.id}/following/`;
          break;
        case 'created':
          params.created_by = user?.id;
          break;
      }
      
      const response = await api.get<PaginatedResponse<WorkoutPlan>>(endpoint, params);
      
      if (reset) {
        setPlans(response.data.results);
        setPage(2);
      } else {
        setPlans(prev => [...prev, ...response.data.results]);
        setPage(prev => prev + 1);
      }
      
      setHasMore(!!response.data.next);
      
    } catch (error) {
      console.error('Error loading plans:', error);
      Toast.show({
        type: 'error',
        text1: 'Error',
        text2: getErrorMessage(error),
      });
    } finally {
      setLoading(false);
    }
  }, [activeTab, user, searchQuery, filters, loading, hasMore, page]);

  // Cargar datos al cambiar tab o filtros
  useEffect(() => {
    setPlans([]);
    setPage(1);
    setHasMore(true);
    loadPlans(true);
  }, [activeTab, searchQuery, filters]);

  // Cargar datos al enfocar la pantalla
  useFocusEffect(
    useCallback(() => {
      if (plans.length === 0) {
        loadPlans(true);
      }
    }, [])
  );

  // Manejar refresh
  const onRefresh = useCallback(async () => {
    setRefreshing(true);
    setPlans([]);
    setPage(1);
    setHasMore(true);
    await loadPlans(true);
    setRefreshing(false);
  }, [loadPlans]);

  // Seguir/dejar de seguir plan
  const toggleFollowPlan = async (planId: number, isFollowing: boolean) => {
    try {
      if (isFollowing) {
        await api.delete(`/plans/${planId}/unfollow/`);
        Toast.show({
          type: 'info',
          text1: 'Plan eliminado de tus seguidos',
        });
      } else {
        await api.post(`/plans/${planId}/follow/`);
        Toast.show({
          type: 'success',
          text1: 'Plan agregado a tus seguidos',
        });
      }
      
      // Actualizar estado local
      setPlans(prev => prev.map(plan => 
        plan.id === planId 
          ? { 
              ...plan, 
              is_following: !isFollowing,
              followers_count: plan.followers_count + (isFollowing ? -1 : 1)
            }
          : plan
      ));
      
    } catch (error) {
      console.error('Error toggling plan follow:', error);
      Toast.show({
        type: 'error',
        text1: 'Error',
        text2: getErrorMessage(error),
      });
    }
  };

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

  // Renderizar tab
  const renderTab = (tab: TabData) => {
    const isActive = activeTab === tab.key;
    return (
      <Surface
        key={tab.key}
        style={[
          styles.tab,
          isActive && { backgroundColor: theme.colors.primaryContainer }
        ]}
        elevation={isActive ? 2 : 0}
      >
        <Button
          mode="text"
          icon={tab.icon}
          onPress={() => setActiveTab(tab.key)}
          contentStyle={styles.tabContent}
          labelStyle={[
            styles.tabLabel,
            isActive && { color: theme.colors.onPrimaryContainer }
          ]}
          compact
        >
          {tab.title}
        </Button>
      </Surface>
    );
  };

  // Renderizar filtros
  const renderFilters = () => {
    if (!showFilters) return null;
    
    return (
      <Surface style={styles.filtersContainer} elevation={1}>
        <View style={styles.filterSection}>
          <Paragraph style={styles.filterTitle}>Dificultad</Paragraph>
          <View style={styles.filterChips}>
            {DIFFICULTY_FILTERS.map(filter => (
              <Chip
                key={filter.key}
                mode={filters.difficulty_level === filter.value ? 'flat' : 'outlined'}
                onPress={() => applyFilter('difficulty_level', filter.value)}
                style={styles.filterChip}
              >
                {filter.label}
              </Chip>
            ))}
          </View>
        </View>
        
        <View style={styles.filterSection}>
          <Paragraph style={styles.filterTitle}>Duración</Paragraph>
          <View style={styles.filterChips}>
            {DURATION_FILTERS.map(filter => (
              <Chip
                key={filter.key}
                mode={filters.duration_weeks === filter.value ? 'flat' : 'outlined'}
                onPress={() => applyFilter('duration_weeks', filter.value)}
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

  // Renderizar plan
  const renderPlan = ({ item: plan }: { item: WorkoutPlan }) => (
    <Card style={styles.planCard}>
      <View style={styles.planImageContainer}>
        {plan.image_url ? (
          <Image source={{ uri: plan.image_url }} style={styles.planImage} />
        ) : (
          <Surface style={styles.planImagePlaceholder} elevation={0}>
            <Icon name="dumbbell" size={40} color={theme.colors.outline} />
          </Surface>
        )}
        <View style={styles.planImageOverlay}>
          <Chip
            icon="star"
            mode="flat"
            style={[
              styles.difficultyChip,
              { backgroundColor: getDifficultyColor(plan.difficulty_level) }
            ]}
            textStyle={styles.difficultyText}
          >
            {getDifficultyLabel(plan.difficulty_level)}
          </Chip>
          <IconButton
            icon={plan.is_following ? "heart" : "heart-outline"}
            iconColor={plan.is_following ? theme.colors.error : theme.colors.onSurface}
            style={styles.favoriteButton}
            onPress={() => toggleFollowPlan(plan.id, plan.is_following || false)}
          />
        </View>
      </View>
      
      <Card.Content style={styles.planContent}>
        <View style={styles.planHeader}>
          <Title style={styles.planTitle} numberOfLines={2}>
            {plan.name}
          </Title>
          <View style={styles.planStats}>
            <Badge style={styles.planBadge}>
              {plan.followers_count} seguidores
            </Badge>
          </View>
        </View>
        
        <Paragraph style={styles.planDescription} numberOfLines={2}>
          {plan.description}
        </Paragraph>
        
        <View style={styles.planMetrics}>
          <View style={styles.metric}>
            <Icon name="calendar-week" size={16} color={theme.colors.primary} />
            <Paragraph style={styles.metricText}>
              {plan.duration_weeks} semanas
            </Paragraph>
          </View>
          <View style={styles.metric}>
            <Icon name="calendar" size={16} color={theme.colors.primary} />
            <Paragraph style={styles.metricText}>
              {plan.days_per_week} días/sem
            </Paragraph>
          </View>
          <View style={styles.metric}>
            <Icon name="timer" size={16} color={theme.colors.primary} />
            <Paragraph style={styles.metricText}>
              {plan.estimated_duration_minutes}min
            </Paragraph>
          </View>
        </View>
        
        <View style={styles.planTags}>
          {plan.tags.slice(0, 2).map((tag, index) => (
            <Chip key={index} mode="outlined" compact style={styles.tagChip}>
              {tag}
            </Chip>
          ))}
          {plan.tags.length > 2 && (
            <Paragraph style={styles.moreTags}>
              +{plan.tags.length - 2} más
            </Paragraph>
          )}
        </View>
        
        <View style={styles.planActions}>
          <Button
            mode="outlined"
            onPress={() => {
              // TODO: Navegar a detalles del plan
              Toast.show({
                type: 'info',
                text1: 'Abriendo detalles del plan...',
              });
            }}
            style={styles.actionButton}
          >
            Ver Detalles
          </Button>
          <Button
            mode="contained"
            onPress={() => toggleFollowPlan(plan.id, plan.is_following || false)}
            style={styles.actionButton}
          >
            {plan.is_following ? 'Siguiendo' : 'Seguir'}
          </Button>
        </View>
      </Card.Content>
    </Card>
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

  const filteredTabsCount = Object.keys(filters).filter(key => 
    filters[key as keyof WorkoutPlanFilters] !== undefined
  ).length;

  return (
    <View style={styles.container}>
      {/* Header con búsqueda */}
      <Surface style={styles.header} elevation={4}>
        <Searchbar
          placeholder="Buscar planes de entrenamiento..."
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
            filteredTabsCount > 0 && { backgroundColor: theme.colors.primary }
          ]}
        >
          {filteredTabsCount > 0 && (
            <Badge style={styles.filterBadge}>
              {filteredTabsCount}
            </Badge>
          )}
        </IconButton>
      </Surface>

      {/* Filtros */}
      {renderFilters()}

      {/* Tabs */}
      <ScrollView
        horizontal
        showsHorizontalScrollIndicator={false}
        style={styles.tabsContainer}
        contentContainerStyle={styles.tabsContent}
      >
        {TABS.map(renderTab)}
      </ScrollView>

      {/* Lista de planes */}
      <FlatList
        data={plans}
        renderItem={renderPlan}
        keyExtractor={(item) => item.id.toString()}
        contentContainerStyle={styles.listContainer}
        refreshControl={
          <RefreshControl refreshing={refreshing} onRefresh={onRefresh} />
        }
        onEndReached={() => loadPlans()}
        onEndReachedThreshold={0.1}
        ListFooterComponent={
          loading && hasMore ? (
            <View style={styles.loadingFooter}>
              <ActivityIndicator size="small" />
              <Paragraph style={styles.loadingText}>Cargando más planes...</Paragraph>
            </View>
          ) : null
        }
        ListEmptyComponent={
          !loading ? (
            <View style={styles.emptyState}>
              <Icon name="dumbbell" size={64} color={theme.colors.outline} />
              <Paragraph style={styles.emptyText}>
                {searchQuery ? 'No se encontraron planes' : 'No hay planes disponibles'}
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
    top: -4,
    right: -4,
    fontSize: 10,
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
  tabsContainer: {
    maxHeight: 60,
  },
  tabsContent: {
    paddingHorizontal: 16,
    paddingVertical: 8,
  },
  tab: {
    marginRight: 8,
    borderRadius: 20,
  },
  tabContent: {
    paddingHorizontal: 8,
  },
  tabLabel: {
    fontSize: 12,
  },
  listContainer: {
    padding: 16,
  },
  planCard: {
    marginBottom: 16,
    overflow: 'hidden',
  },
  planImageContainer: {
    position: 'relative',
    height: 160,
  },
  planImage: {
    width: '100%',
    height: '100%',
  },
  planImagePlaceholder: {
    width: '100%',
    height: '100%',
    justifyContent: 'center',
    alignItems: 'center',
    backgroundColor: '#f0f0f0',
  },
  planImageOverlay: {
    position: 'absolute',
    top: 0,
    left: 0,
    right: 0,
    bottom: 0,
    justifyContent: 'space-between',
    alignItems: 'flex-end',
    padding: 12,
    flexDirection: 'row',
  },
  difficultyChip: {
    alignSelf: 'flex-start',
  },
  difficultyText: {
    color: 'white',
    fontSize: 10,
    fontWeight: 'bold',
  },
  favoriteButton: {
    backgroundColor: 'rgba(255, 255, 255, 0.9)',
  },
  planContent: {
    padding: 16,
  },
  planHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'flex-start',
    marginBottom: 8,
  },
  planTitle: {
    flex: 1,
    fontSize: 18,
    fontWeight: 'bold',
  },
  planStats: {
    marginLeft: 8,
  },
  planBadge: {
    fontSize: 10,
  },
  planDescription: {
    marginBottom: 12,
    opacity: 0.8,
  },
  planMetrics: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    marginBottom: 12,
  },
  metric: {
    flexDirection: 'row',
    alignItems: 'center',
    flex: 1,
  },
  metricText: {
    fontSize: 12,
    marginLeft: 4,
  },
  planTags: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 16,
  },
  tagChip: {
    marginRight: 8,
    height: 24,
  },
  moreTags: {
    fontSize: 12,
    opacity: 0.6,
  },
  planActions: {
    flexDirection: 'row',
    gap: 8,
  },
  actionButton: {
    flex: 1,
  },
  loadingFooter: {
    flexDirection: 'row',
    justifyContent: 'center',
    alignItems: 'center',
    padding: 16,
  },
  loadingText: {
    marginLeft: 8,
  },
  emptyState: {
    alignItems: 'center',
    padding: 32,
  },
  emptyText: {
    textAlign: 'center',
    marginTop: 16,
    marginBottom: 24,
    opacity: 0.7,
  },
});

export default PlansScreen;