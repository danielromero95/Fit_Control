/**
 * Pantalla de Perfil - Fit_Control
 * 
 * Incluye:
 * - Información del usuario y avatar
 * - Estadísticas y progreso detallado
 * - Logros y metas
 * - Configuración y ajustes
 * - Historial de entrenamientos
 */

import React, { useState, useEffect, useCallback } from 'react';
import {
  View,
  ScrollView,
  StyleSheet,
  RefreshControl,
  Dimensions,
  Alert,
  Image,
} from 'react-native';
import {
  Card,
  Title,
  Paragraph,
  Button,
  Avatar,
  Surface,
  Divider,
  List,
  IconButton,
  ProgressBar,
  Chip,
  useTheme,
  Badge,
  FAB,
} from 'react-native-paper';
import Icon from 'react-native-vector-icons/MaterialCommunityIcons';
import { LineChart, BarChart } from 'react-native-chart-kit';
import { useFocusEffect } from '@react-navigation/native';

import { useAuthStore } from '../store/authStore';
import { api, getErrorMessage } from '../services/apiClient';
import { UserStats, UserProfile, ProgressTrend, Achievement } from '../types/api';
import Toast from 'react-native-toast-message';

const { width } = Dimensions.get('window');

interface ProfileData {
  profile: UserProfile;
  stats: UserStats;
  achievements: Achievement[];
  recentWorkouts: any[];
}

export const ProfileScreen: React.FC = () => {
  const theme = useTheme();
  const { user, logout } = useAuthStore();
  
  const [profileData, setProfileData] = useState<ProfileData | null>(null);
  const [loading, setLoading] = useState(false);
  const [refreshing, setRefreshing] = useState(false);
  const [activeTab, setActiveTab] = useState<'stats' | 'progress' | 'achievements'>('stats');

  // Cargar datos del perfil
  const loadProfileData = useCallback(async () => {
    if (!user) return;
    
    try {
      setLoading(true);
      
      const [profileResponse, statsResponse, achievementsResponse, workoutsResponse] = 
        await Promise.all([
          api.get(`/users/${user.id}/profile/`),
          api.get(`/users/${user.id}/stats/`),
          api.get(`/users/${user.id}/achievements/`),
          api.get(`/users/${user.id}/recent-workouts/`)
        ]);
      
      setProfileData({
        profile: profileResponse.data,
        stats: statsResponse.data,
        achievements: achievementsResponse.data,
        recentWorkouts: workoutsResponse.data
      });
      
    } catch (error) {
      console.error('Error loading profile data:', error);
      Toast.show({
        type: 'error',
        text1: 'Error',
        text2: getErrorMessage(error),
      });
    } finally {
      setLoading(false);
    }
  }, [user]);

  // Cargar datos al enfocar la pantalla
  useFocusEffect(
    useCallback(() => {
      loadProfileData();
    }, [loadProfileData])
  );

  // Manejar refresh
  const onRefresh = useCallback(async () => {
    setRefreshing(true);
    await loadProfileData();
    setRefreshing(false);
  }, [loadProfileData]);

  // Cerrar sesión
  const handleLogout = () => {
    Alert.alert(
      'Cerrar Sesión',
      '¿Estás seguro de que quieres cerrar sesión?',
      [
        { text: 'Cancelar', style: 'cancel' },
        {
          text: 'Cerrar Sesión',
          style: 'destructive',
          onPress: () => {
            logout();
            Toast.show({
              type: 'success',
              text1: 'Sesión cerrada',
              text2: 'Hasta la próxima!',
            });
          }
        }
      ]
    );
  };

  // Renderizar header del perfil
  const renderProfileHeader = () => (
    <Card style={styles.headerCard}>
      <Card.Content>
        <View style={styles.profileHeader}>
          <View style={styles.avatarSection}>
            <Avatar.Text
              size={80}
              label={user?.first_name?.[0] || 'U'}
              style={{ backgroundColor: theme.colors.primary }}
            />
            <IconButton
              icon="camera"
              mode="contained"
              size={20}
              style={styles.cameraButton}
              onPress={() => {
                // TODO: Implementar cambio de foto
                Toast.show({
                  type: 'info',
                  text1: 'Próximamente',
                  text2: 'Función de foto de perfil',
                });
              }}
            />
          </View>
          
          <View style={styles.userInfo}>
            <Title style={styles.userName}>
              {user?.first_name} {user?.last_name}
            </Title>
            <Paragraph style={styles.userEmail}>{user?.email}</Paragraph>
            
            {profileData?.profile && (
              <View style={styles.userMetrics}>
                <Chip icon="weight" mode="outlined" compact style={styles.metricChip}>
                  {profileData.profile.weight || '--'} kg
                </Chip>
                <Chip icon="human-male-height" mode="outlined" compact style={styles.metricChip}>
                  {profileData.profile.height || '--'} cm
                </Chip>
                <Chip icon="target" mode="outlined" compact style={styles.metricChip}>
                  {profileData.profile.fitness_level || 'Principiante'}
                </Chip>
              </View>
            )}
          </View>
        </View>
        
        <View style={styles.profileActions}>
          <Button
            mode="outlined"
            icon="pencil"
            onPress={() => {
              // TODO: Navegar a editar perfil
              Toast.show({
                type: 'info',
                text1: 'Editar perfil próximamente',
              });
            }}
            style={styles.actionButton}
          >
            Editar
          </Button>
          <Button
            mode="contained"
            icon="cog"
            onPress={() => {
              // TODO: Navegar a configuración
              Toast.show({
                type: 'info',
                text1: 'Configuración próximamente',
              });
            }}
            style={styles.actionButton}
          >
            Configuración
          </Button>
        </View>
      </Card.Content>
    </Card>
  );

  // Renderizar tabs de navegación
  const renderTabs = () => (
    <Surface style={styles.tabsContainer} elevation={2}>
      <View style={styles.tabs}>
        {[
          { key: 'stats', label: 'Estadísticas', icon: 'chart-line' },
          { key: 'progress', label: 'Progreso', icon: 'trending-up' },
          { key: 'achievements', label: 'Logros', icon: 'trophy' },
        ].map((tab) => (
          <Surface
            key={tab.key}
            style={[
              styles.tab,
              activeTab === tab.key && { backgroundColor: theme.colors.primaryContainer }
            ]}
            elevation={activeTab === tab.key ? 2 : 0}
          >
            <Button
              mode="text"
              icon={tab.icon}
              onPress={() => setActiveTab(tab.key as any)}
              contentStyle={styles.tabContent}
              labelStyle={[
                styles.tabLabel,
                activeTab === tab.key && { color: theme.colors.onPrimaryContainer }
              ]}
              compact
            >
              {tab.label}
            </Button>
          </Surface>
        ))}
      </View>
    </Surface>
  );

  // Renderizar estadísticas
  const renderStats = () => {
    if (!profileData?.stats) return null;

    const stats = profileData.stats;
    
    return (
      <View style={styles.tabContent}>
        {/* Estadísticas principales */}
        <Card style={styles.card}>
          <Card.Content>
            <Title>Resumen General</Title>
            <View style={styles.statsGrid}>
              <View style={styles.statItem}>
                <Icon name="fire" size={24} color={theme.colors.primary} />
                <Paragraph style={styles.statValue}>{stats.current_streak}</Paragraph>
                <Paragraph style={styles.statLabel}>Días seguidos</Paragraph>
              </View>
              <View style={styles.statItem}>
                <Icon name="dumbbell" size={24} color={theme.colors.primary} />
                <Paragraph style={styles.statValue}>{stats.total_workouts}</Paragraph>
                <Paragraph style={styles.statLabel}>Entrenamientos</Paragraph>
              </View>
              <View style={styles.statItem}>
                <Icon name="timer" size={24} color={theme.colors.primary} />
                <Paragraph style={styles.statValue}>{stats.avg_session_duration}</Paragraph>
                <Paragraph style={styles.statLabel}>Min promedio</Paragraph>
              </View>
              <View style={styles.statItem}>
                <Icon name="weight-lifter" size={24} color={theme.colors.primary} />
                <Paragraph style={styles.statValue}>{Math.round(stats.total_weight_lifted)}</Paragraph>
                <Paragraph style={styles.statLabel}>Kg levantados</Paragraph>
              </View>
            </View>
          </Card.Content>
        </Card>

        {/* Actividad semanal */}
        <Card style={styles.card}>
          <Card.Content>
            <Title>Actividad Semanal</Title>
            <View style={styles.weeklyActivity}>
              {['L', 'M', 'X', 'J', 'V', 'S', 'D'].map((day, index) => (
                <View key={day} style={styles.dayActivity}>
                  <Surface
                    style={[
                      styles.dayCircle,
                      index < stats.workouts_this_week && { backgroundColor: theme.colors.primary }
                    ]}
                    elevation={index < stats.workouts_this_week ? 2 : 0}
                  >
                    <Paragraph style={[
                      styles.dayText,
                      index < stats.workouts_this_week && { color: theme.colors.onPrimary }
                    ]}>
                      {day}
                    </Paragraph>
                  </Surface>
                </View>
              ))}
            </View>
            <Paragraph style={styles.weeklyStats}>
              {stats.workouts_this_week} de 7 días completados esta semana
            </Paragraph>
          </Card.Content>
        </Card>

        {/* Ejercicios favoritos */}
        {stats.favorite_exercises && stats.favorite_exercises.length > 0 && (
          <Card style={styles.card}>
            <Card.Content>
              <Title>Ejercicios Favoritos</Title>
              {stats.favorite_exercises.slice(0, 3).map((exercise, index) => (
                <List.Item
                  key={exercise.id}
                  title={exercise.name}
                  description={`${exercise.muscle_groups.join(', ')}`}
                  left={() => (
                    <Avatar.Icon
                      size={40}
                      icon="dumbbell"
                      style={{ backgroundColor: theme.colors.primaryContainer }}
                    />
                  )}
                  right={() => (
                    <Badge style={styles.exerciseBadge}>#{index + 1}</Badge>
                  )}
                />
              ))}
            </Card.Content>
          </Card>
        )}
      </View>
    );
  };

  // Renderizar progreso
  const renderProgress = () => {
    if (!profileData?.stats) return null;

    // Datos de ejemplo para gráficos
    const progressData = {
      labels: ['Ene', 'Feb', 'Mar', 'Abr', 'May', 'Jun'],
      datasets: [{
        data: [10, 15, 12, 18, 16, 20],
        strokeWidth: 2,
      }]
    };

    const weightData = {
      labels: ['Ene', 'Feb', 'Mar', 'Abr', 'May', 'Jun'],
      datasets: [{
        data: [65, 67, 66, 68, 67, 69],
      }]
    };

    return (
      <View style={styles.tabContent}>
        {/* Gráfico de entrenamientos */}
        <Card style={styles.card}>
          <Card.Content>
            <Title>Entrenamientos por Mes</Title>
            <LineChart
              data={progressData}
              width={width - 64}
              height={200}
              chartConfig={{
                backgroundColor: theme.colors.surface,
                backgroundGradientFrom: theme.colors.surface,
                backgroundGradientTo: theme.colors.surface,
                decimalPlaces: 0,
                color: (opacity = 1) => `rgba(${theme.colors.primary}, ${opacity})`,
                labelColor: () => theme.colors.onSurface,
                style: { borderRadius: 16 },
                propsForDots: {
                  r: '6',
                  strokeWidth: '2',
                  stroke: theme.colors.primary
                }
              }}
              style={styles.chart}
            />
          </Card.Content>
        </Card>

        {/* Gráfico de peso */}
        <Card style={styles.card}>
          <Card.Content>
            <Title>Evolución del Peso</Title>
            <BarChart
              data={weightData}
              width={width - 64}
              height={200}
              chartConfig={{
                backgroundColor: theme.colors.surface,
                backgroundGradientFrom: theme.colors.surface,
                backgroundGradientTo: theme.colors.surface,
                decimalPlaces: 1,
                color: (opacity = 1) => `rgba(${theme.colors.secondary}, ${opacity})`,
                labelColor: () => theme.colors.onSurface,
                style: { borderRadius: 16 }
              }}
              style={styles.chart}
            />
          </Card.Content>
        </Card>

        {/* Metas de progreso */}
        <Card style={styles.card}>
          <Card.Content>
            <Title>Metas de Progreso</Title>
            
            <View style={styles.goalItem}>
              <View style={styles.goalInfo}>
                <Paragraph style={styles.goalTitle}>Entrenamientos Semanales</Paragraph>
                <Paragraph style={styles.goalProgress}>
                  {profileData.stats.workouts_this_week} / 5
                </Paragraph>
              </View>
              <ProgressBar
                progress={profileData.stats.workouts_this_week / 5}
                color={theme.colors.primary}
                style={styles.goalBar}
              />
            </View>

            <View style={styles.goalItem}>
              <View style={styles.goalInfo}>
                <Paragraph style={styles.goalTitle}>Racha Mensual</Paragraph>
                <Paragraph style={styles.goalProgress}>
                  {profileData.stats.current_streak} / 30 días
                </Paragraph>
              </View>
              <ProgressBar
                progress={profileData.stats.current_streak / 30}
                color={theme.colors.secondary}
                style={styles.goalBar}
              />
            </View>
          </Card.Content>
        </Card>
      </View>
    );
  };

  // Renderizar logros
  const renderAchievements = () => {
    if (!profileData?.achievements) return null;

    const earnedAchievements = profileData.achievements.filter(a => a.is_earned);
    const pendingAchievements = profileData.achievements.filter(a => !a.is_earned);

    return (
      <View style={styles.tabContent}>
        {/* Logros obtenidos */}
        <Card style={styles.card}>
          <Card.Content>
            <Title>Logros Obtenidos ({earnedAchievements.length})</Title>
            {earnedAchievements.length === 0 ? (
              <Paragraph style={styles.emptyText}>
                ¡Aún no tienes logros! Sigue entrenando para desbloquearlos.
              </Paragraph>
            ) : (
              earnedAchievements.map((achievement) => (
                <List.Item
                  key={achievement.id}
                  title={achievement.name}
                  description={achievement.description}
                  left={() => (
                    <Avatar.Icon
                      size={40}
                      icon={achievement.icon}
                      style={{ backgroundColor: achievement.badge_color }}
                    />
                  )}
                  right={() => (
                    <View style={styles.achievementPoints}>
                      <Icon name="star" size={16} color={theme.colors.primary} />
                      <Paragraph style={styles.pointsText}>{achievement.points}</Paragraph>
                    </View>
                  )}
                />
              ))
            )}
          </Card.Content>
        </Card>

        {/* Próximos logros */}
        <Card style={styles.card}>
          <Card.Content>
            <Title>Próximos Logros</Title>
            {pendingAchievements.slice(0, 5).map((achievement) => (
              <List.Item
                key={achievement.id}
                title={achievement.name}
                description={achievement.description}
                left={() => (
                  <Avatar.Icon
                    size={40}
                    icon={achievement.icon}
                    style={{ 
                      backgroundColor: theme.colors.outline,
                      opacity: 0.5 
                    }}
                  />
                )}
                right={() => (
                  <View style={styles.achievementPoints}>
                    <Icon name="star-outline" size={16} color={theme.colors.outline} />
                    <Paragraph style={[styles.pointsText, { color: theme.colors.outline }]}>
                      {achievement.points}
                    </Paragraph>
                  </View>
                )}
                style={{ opacity: 0.6 }}
              />
            ))}
          </Card.Content>
        </Card>
      </View>
    );
  };

  return (
    <View style={styles.container}>
      <ScrollView
        style={styles.scrollView}
        refreshControl={
          <RefreshControl refreshing={refreshing} onRefresh={onRefresh} />
        }
      >
        {/* Header del perfil */}
        {renderProfileHeader()}

        {/* Tabs de navegación */}
        {renderTabs()}

        {/* Contenido de tabs */}
        {activeTab === 'stats' && renderStats()}
        {activeTab === 'progress' && renderProgress()}
        {activeTab === 'achievements' && renderAchievements()}

        {/* Opciones adicionales */}
        <Card style={styles.card}>
          <Card.Content>
            <Title>Opciones</Title>
            <List.Item
              title="Historial de Entrenamientos"
              description="Ver todos tus entrenamientos pasados"
              left={() => <Icon name="history" size={24} color={theme.colors.onSurface} />}
              right={() => <Icon name="chevron-right" size={24} color={theme.colors.onSurface} />}
              onPress={() => {
                // TODO: Navegar a historial
                Toast.show({
                  type: 'info',
                  text1: 'Historial próximamente',
                });
              }}
            />
            <Divider />
            <List.Item
              title="Compartir Progreso"
              description="Comparte tus logros con amigos"
              left={() => <Icon name="share" size={24} color={theme.colors.onSurface} />}
              right={() => <Icon name="chevron-right" size={24} color={theme.colors.onSurface} />}
              onPress={() => {
                // TODO: Implementar compartir
                Toast.show({
                  type: 'info',
                  text1: 'Compartir próximamente',
                });
              }}
            />
            <Divider />
            <List.Item
              title="Ayuda y Soporte"
              description="¿Necesitas ayuda? Contáctanos"
              left={() => <Icon name="help-circle" size={24} color={theme.colors.onSurface} />}
              right={() => <Icon name="chevron-right" size={24} color={theme.colors.onSurface} />}
              onPress={() => {
                // TODO: Abrir soporte
                Toast.show({
                  type: 'info',
                  text1: 'Soporte próximamente',
                });
              }}
            />
            <Divider />
            <List.Item
              title="Cerrar Sesión"
              description="Salir de tu cuenta"
              left={() => <Icon name="logout" size={24} color={theme.colors.error} />}
              right={() => <Icon name="chevron-right" size={24} color={theme.colors.error} />}
              onPress={handleLogout}
              titleStyle={{ color: theme.colors.error }}
            />
          </Card.Content>
        </Card>

        {/* Espacio para el FAB */}
        <View style={styles.fabSpace} />
      </ScrollView>

      {/* FAB para acceso rápido a configuración */}
      <FAB
        icon="account-edit"
        style={[
          styles.fab,
          { backgroundColor: theme.colors.secondary }
        ]}
        onPress={() => {
          // TODO: Abrir configuración rápida
          Alert.alert(
            'Configuración Rápida',
            'Selecciona una opción',
            [
              { text: 'Editar Perfil', onPress: () => {} },
              { text: 'Cambiar Foto', onPress: () => {} },
              { text: 'Configuración', onPress: () => {} },
              { text: 'Cancelar', style: 'cancel' }
            ]
          );
        }}
      />
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f5f5f5',
  },
  scrollView: {
    flex: 1,
  },
  headerCard: {
    margin: 16,
    marginBottom: 8,
  },
  profileHeader: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 16,
  },
  avatarSection: {
    position: 'relative',
    marginRight: 16,
  },
  cameraButton: {
    position: 'absolute',
    bottom: -5,
    right: -5,
    backgroundColor: 'white',
  },
  userInfo: {
    flex: 1,
  },
  userName: {
    fontSize: 24,
    fontWeight: 'bold',
    marginBottom: 4,
  },
  userEmail: {
    fontSize: 14,
    opacity: 0.7,
    marginBottom: 12,
  },
  userMetrics: {
    flexDirection: 'row',
    flexWrap: 'wrap',
  },
  metricChip: {
    marginRight: 8,
    marginBottom: 4,
  },
  profileActions: {
    flexDirection: 'row',
    gap: 12,
  },
  actionButton: {
    flex: 1,
  },
  tabsContainer: {
    marginHorizontal: 16,
    marginBottom: 8,
    borderRadius: 12,
    overflow: 'hidden',
  },
  tabs: {
    flexDirection: 'row',
  },
  tab: {
    flex: 1,
    borderRadius: 0,
  },
  tabContent: {
    paddingHorizontal: 0,
    paddingVertical: 8,
  },
  tabLabel: {
    fontSize: 12,
  },
  card: {
    margin: 16,
    marginTop: 8,
  },
  statsGrid: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    justifyContent: 'space-between',
    marginTop: 16,
  },
  statItem: {
    width: (width - 64) / 2,
    alignItems: 'center',
    marginBottom: 16,
  },
  statValue: {
    fontSize: 24,
    fontWeight: 'bold',
    marginTop: 8,
    marginBottom: 4,
  },
  statLabel: {
    fontSize: 12,
    textAlign: 'center',
    opacity: 0.7,
  },
  weeklyActivity: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    marginTop: 16,
    marginBottom: 12,
  },
  dayActivity: {
    alignItems: 'center',
  },
  dayCircle: {
    width: 40,
    height: 40,
    borderRadius: 20,
    justifyContent: 'center',
    alignItems: 'center',
    backgroundColor: '#f0f0f0',
  },
  dayText: {
    fontSize: 12,
    fontWeight: 'bold',
  },
  weeklyStats: {
    textAlign: 'center',
    fontSize: 12,
    opacity: 0.7,
  },
  exerciseBadge: {
    alignSelf: 'center',
  },
  chart: {
    marginTop: 16,
    borderRadius: 16,
  },
  goalItem: {
    marginBottom: 16,
  },
  goalInfo: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 8,
  },
  goalTitle: {
    fontSize: 14,
    fontWeight: '600',
  },
  goalProgress: {
    fontSize: 14,
    fontWeight: 'bold',
  },
  goalBar: {
    height: 8,
    borderRadius: 4,
  },
  emptyText: {
    textAlign: 'center',
    opacity: 0.7,
    marginVertical: 16,
  },
  achievementPoints: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  pointsText: {
    marginLeft: 4,
    fontSize: 12,
    fontWeight: 'bold',
  },
  fab: {
    position: 'absolute',
    margin: 16,
    right: 0,
    bottom: 0,
  },
  fabSpace: {
    height: 100,
  },
});

export default ProfileScreen;