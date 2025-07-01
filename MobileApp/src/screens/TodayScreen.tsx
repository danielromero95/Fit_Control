/**
 * Pantalla Principal "Hoy" - Fit_Control
 * 
 * Incluye:
 * - Calendario interactivo con entrenamientos marcados
 * - Entrenamientos del día seleccionado
 * - Estadísticas rápidas del usuario
 * - Acceso rápido a iniciar entrenamiento
 */

import React, { useState, useEffect, useCallback } from 'react';
import {
  View,
  ScrollView,
  StyleSheet,
  RefreshControl,
  Alert,
  Dimensions,
} from 'react-native';
import {
  Card,
  Title,
  Paragraph,
  Button,
  FAB,
  Avatar,
  ProgressBar,
  Chip,
  Surface,
  Divider,
  useTheme,
} from 'react-native-paper';
import { Calendar, LocaleConfig } from 'react-native-calendars';
import Icon from 'react-native-vector-icons/MaterialCommunityIcons';
import { useFocusEffect } from '@react-navigation/native';

import { useAuthStore } from '../store/authStore';
import { api, getErrorMessage } from '../services/apiClient';
import { Exercise, WorkoutPlan, UserPerformanceLog } from '../types/api';
import Toast from 'react-native-toast-message';

// Configuración de idioma para el calendario
LocaleConfig.locales['es'] = {
  monthNames: [
    'Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio',
    'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre'
  ],
  monthNamesShort: [
    'Ene', 'Feb', 'Mar', 'Abr', 'May', 'Jun',
    'Jul', 'Ago', 'Sep', 'Oct', 'Nov', 'Dic'
  ],
  dayNames: [
    'Domingo', 'Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado'
  ],
  dayNamesShort: ['Dom', 'Lun', 'Mar', 'Mié', 'Jue', 'Vie', 'Sáb'],
  today: "Hoy"
};
LocaleConfig.defaultLocale = 'es';

interface TodayWorkout {
  id: number;
  plan_name: string;
  day_name: string;
  exercises: Array<{
    exercise: Exercise;
    sets: number;
    reps: number;
    rest_seconds: number;
    completed?: boolean;
  }>;
}

interface CalendarMarking {
  [date: string]: {
    marked?: boolean;
    dotColor?: string;
    selected?: boolean;
    selectedColor?: string;
    customStyles?: any;
  };
}

interface UserStats {
  workouts_this_week: number;
  workouts_this_month: number;
  current_streak: number;
  total_workouts: number;
  avg_session_duration: number;
}

const { width } = Dimensions.get('window');

export const TodayScreen: React.FC = () => {
  const theme = useTheme();
  const { user } = useAuthStore();
  
  const [selectedDate, setSelectedDate] = useState(
    new Date().toISOString().split('T')[0]
  );
  const [todayWorkouts, setTodayWorkouts] = useState<TodayWorkout[]>([]);
  const [userStats, setUserStats] = useState<UserStats | null>(null);
  const [calendarMarkings, setCalendarMarkings] = useState<CalendarMarking>({});
  const [loading, setLoading] = useState(false);
  const [refreshing, setRefreshing] = useState(false);

  // Cargar datos de la pantalla
  const loadTodayData = useCallback(async () => {
    if (!user) return;
    
    try {
      setLoading(true);
      
      // Cargar entrenamientos del día
      const workoutsResponse = await api.get(`/plans/user/${user.id}/workouts/`, {
        date: selectedDate
      });
      setTodayWorkouts(workoutsResponse.data);
      
      // Cargar estadísticas del usuario
      const statsResponse = await api.get(`/users/${user.id}/stats/`);
      setUserStats(statsResponse.data);
      
      // Cargar marcadores del calendario (entrenamientos programados)
      const calendarResponse = await api.get(`/plans/user/${user.id}/calendar/`);
      const markings: CalendarMarking = {};
      
      // Marcar entrenamientos programados
      calendarResponse.data.scheduled_days.forEach((date: string) => {
        markings[date] = {
          marked: true,
          dotColor: theme.colors.primary,
        };
      });
      
      // Marcar entrenamientos completados
      calendarResponse.data.completed_days.forEach((date: string) => {
        markings[date] = {
          ...markings[date],
          dotColor: theme.colors.onSurface,
          customStyles: {
            container: {
              backgroundColor: theme.colors.primaryContainer,
              borderRadius: 16,
            },
            text: {
              color: theme.colors.onPrimaryContainer,
              fontWeight: 'bold',
            }
          }
        };
      });
      
      // Marcar día seleccionado
      markings[selectedDate] = {
        ...markings[selectedDate],
        selected: true,
        selectedColor: theme.colors.primary,
      };
      
      setCalendarMarkings(markings);
      
    } catch (error) {
      console.error('Error loading today data:', error);
      Toast.show({
        type: 'error',
        text1: 'Error',
        text2: getErrorMessage(error),
      });
    } finally {
      setLoading(false);
    }
  }, [user, selectedDate, theme]);

  // Cargar datos al enfocar la pantalla
  useFocusEffect(
    useCallback(() => {
      loadTodayData();
    }, [loadTodayData])
  );

  // Manejar refresh
  const onRefresh = useCallback(async () => {
    setRefreshing(true);
    await loadTodayData();
    setRefreshing(false);
  }, [loadTodayData]);

  // Manejar selección de fecha
  const onDateSelect = (day: any) => {
    setSelectedDate(day.dateString);
  };

  // Iniciar entrenamiento
  const startWorkout = (workoutId: number) => {
    Alert.alert(
      'Iniciar Entrenamiento',
      '¿Estás listo para comenzar tu entrenamiento?',
      [
        { text: 'Cancelar', style: 'cancel' },
        {
          text: 'Iniciar',
          onPress: () => {
            // TODO: Navegar a pantalla de entrenamiento activo
            Toast.show({
              type: 'success',
              text1: '¡Entrenamiento iniciado!',
              text2: 'Ve a grabar tus ejercicios',
            });
          }
        }
      ]
    );
  };

  // Renderizar estadística
  const renderStat = (icon: string, label: string, value: string | number) => (
    <Surface style={styles.statCard} elevation={1}>
      <Icon name={icon} size={24} color={theme.colors.primary} />
      <Paragraph style={styles.statValue}>{value}</Paragraph>
      <Paragraph style={styles.statLabel}>{label}</Paragraph>
    </Surface>
  );

  // Renderizar ejercicio
  const renderExercise = (exercise: any, index: number) => (
    <View key={index} style={styles.exerciseItem}>
      <Avatar.Icon
        size={40}
        icon="dumbbell"
        style={{ backgroundColor: theme.colors.primaryContainer }}
      />
      <View style={styles.exerciseInfo}>
        <Paragraph style={styles.exerciseName}>
          {exercise.exercise.name}
        </Paragraph>
        <Paragraph style={styles.exerciseDetails}>
          {exercise.sets} series × {exercise.reps} reps
        </Paragraph>
        <Paragraph style={styles.exerciseRest}>
          Descanso: {Math.floor(exercise.rest_seconds / 60)}:{exercise.rest_seconds % 60}
        </Paragraph>
      </View>
      <Chip
        mode={exercise.completed ? 'flat' : 'outlined'}
        icon={exercise.completed ? 'check' : 'clock-outline'}
        style={[
          styles.exerciseStatus,
          exercise.completed && { backgroundColor: theme.colors.primaryContainer }
        ]}
      >
        {exercise.completed ? 'Completado' : 'Pendiente'}
      </Chip>
    </View>
  );

  return (
    <View style={styles.container}>
      <ScrollView
        style={styles.scrollView}
        refreshControl={
          <RefreshControl refreshing={refreshing} onRefresh={onRefresh} />
        }
      >
        {/* Header con saludo */}
        <Card style={styles.headerCard}>
          <Card.Content>
            <View style={styles.headerContent}>
              <View>
                <Title>¡Hola, {user?.first_name || 'Usuario'}!</Title>
                <Paragraph>
                  {new Date(selectedDate).toLocaleDateString('es-ES', {
                    weekday: 'long',
                    year: 'numeric',
                    month: 'long',
                    day: 'numeric'
                  })}
                </Paragraph>
              </View>
              <Avatar.Icon size={60} icon="account" />
            </View>
          </Card.Content>
        </Card>

        {/* Estadísticas rápidas */}
        {userStats && (
          <Card style={styles.card}>
            <Card.Content>
              <Title>Tus Estadísticas</Title>
              <View style={styles.statsGrid}>
                {renderStat('fire', 'Racha', `${userStats.current_streak} días`)}
                {renderStat('calendar-week', 'Esta semana', userStats.workouts_this_week)}
                {renderStat('calendar-month', 'Este mes', userStats.workouts_this_month)}
                {renderStat('timer', 'Tiempo promedio', `${userStats.avg_session_duration}min`)}
              </View>
            </Card.Content>
          </Card>
        )}

        {/* Calendario interactivo */}
        <Card style={styles.card}>
          <Card.Content>
            <Title>Calendario de Entrenamientos</Title>
            <Calendar
              current={selectedDate}
              onDayPress={onDateSelect}
              markedDates={calendarMarkings}
              theme={{
                backgroundColor: theme.colors.surface,
                calendarBackground: theme.colors.surface,
                textSectionTitleColor: theme.colors.onSurface,
                selectedDayBackgroundColor: theme.colors.primary,
                selectedDayTextColor: theme.colors.onPrimary,
                todayTextColor: theme.colors.primary,
                dayTextColor: theme.colors.onSurface,
                textDisabledColor: theme.colors.outline,
                dotColor: theme.colors.primary,
                selectedDotColor: theme.colors.onPrimary,
                arrowColor: theme.colors.primary,
                monthTextColor: theme.colors.onSurface,
                indicatorColor: theme.colors.primary,
                textDayFontWeight: '600',
                textMonthFontWeight: 'bold',
                textDayHeaderFontWeight: '600',
                textDayFontSize: 16,
                textMonthFontSize: 18,
                textDayHeaderFontSize: 14
              }}
              markingType="custom"
              enableSwipeMonths={true}
            />
          </Card.Content>
        </Card>

        {/* Entrenamientos del día */}
        <Card style={styles.card}>
          <Card.Content>
            <View style={styles.sectionHeader}>
              <Title>Entrenamientos de Hoy</Title>
              {todayWorkouts.length > 0 && (
                <Chip icon="information-outline">
                  {todayWorkouts.length} programado{todayWorkouts.length !== 1 ? 's' : ''}
                </Chip>
              )}
            </View>

            {todayWorkouts.length === 0 ? (
              <Surface style={styles.emptyState} elevation={0}>
                <Icon
                  name="calendar-blank"
                  size={64}
                  color={theme.colors.outline}
                />
                <Paragraph style={styles.emptyText}>
                  No tienes entrenamientos programados para este día
                </Paragraph>
                <Button
                  mode="outlined"
                  icon="plus"
                  onPress={() => {
                    // TODO: Navegar a selección de plan
                  }}
                  style={styles.emptyButton}
                >
                  Explorar Planes
                </Button>
              </Surface>
            ) : (
              todayWorkouts.map((workout, index) => (
                <Surface key={workout.id} style={styles.workoutCard} elevation={1}>
                  <View style={styles.workoutHeader}>
                    <View>
                      <Title style={styles.workoutTitle}>
                        {workout.plan_name}
                      </Title>
                      <Paragraph style={styles.workoutSubtitle}>
                        {workout.day_name} • {workout.exercises.length} ejercicios
                      </Paragraph>
                    </View>
                    <Button
                      mode="contained"
                      icon="play"
                      onPress={() => startWorkout(workout.id)}
                      compact
                    >
                      Iniciar
                    </Button>
                  </View>

                  <Divider style={styles.divider} />

                  {workout.exercises.slice(0, 3).map((exercise, exerciseIndex) =>
                    renderExercise(exercise, exerciseIndex)
                  )}

                  {workout.exercises.length > 3 && (
                    <Paragraph style={styles.moreExercises}>
                      +{workout.exercises.length - 3} ejercicios más
                    </Paragraph>
                  )}

                  {/* Progreso del entrenamiento */}
                  <View style={styles.progressSection}>
                    <Paragraph style={styles.progressLabel}>
                      Progreso: {workout.exercises.filter(e => e.completed).length} / {workout.exercises.length}
                    </Paragraph>
                    <ProgressBar
                      progress={workout.exercises.filter(e => e.completed).length / workout.exercises.length}
                      color={theme.colors.primary}
                      style={styles.progressBar}
                    />
                  </View>
                </Surface>
              ))
            )}
          </Card.Content>
        </Card>

        {/* Espacio para el FAB */}
        <View style={styles.fabSpace} />
      </ScrollView>

      {/* FAB para acceso rápido */}
      <FAB
        icon="plus"
        style={[
          styles.fab,
          { backgroundColor: theme.colors.primary }
        ]}
        onPress={() => {
          // TODO: Abrir menú de acciones rápidas
          Alert.alert(
            'Acciones Rápidas',
            'Selecciona una acción',
            [
              { text: 'Nuevo Entrenamiento Libre', onPress: () => {} },
              { text: 'Grabar Ejercicio', onPress: () => {} },
              { text: 'Ver Progreso', onPress: () => {} },
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
  headerContent: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
  },
  card: {
    margin: 16,
    marginTop: 8,
  },
  sectionHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 16,
  },
  statsGrid: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    justifyContent: 'space-between',
    marginTop: 16,
  },
  statCard: {
    width: (width - 64) / 2,
    padding: 16,
    borderRadius: 12,
    alignItems: 'center',
    marginBottom: 8,
  },
  statValue: {
    fontSize: 20,
    fontWeight: 'bold',
    marginTop: 8,
    marginBottom: 4,
  },
  statLabel: {
    fontSize: 12,
    textAlign: 'center',
  },
  workoutCard: {
    padding: 16,
    borderRadius: 12,
    marginBottom: 12,
  },
  workoutHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'flex-start',
    marginBottom: 12,
  },
  workoutTitle: {
    fontSize: 18,
    marginBottom: 4,
  },
  workoutSubtitle: {
    fontSize: 14,
    opacity: 0.7,
  },
  divider: {
    marginBottom: 12,
  },
  exerciseItem: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 12,
  },
  exerciseInfo: {
    flex: 1,
    marginLeft: 12,
  },
  exerciseName: {
    fontSize: 14,
    fontWeight: '600',
    marginBottom: 2,
  },
  exerciseDetails: {
    fontSize: 12,
    opacity: 0.8,
  },
  exerciseRest: {
    fontSize: 12,
    opacity: 0.6,
  },
  exerciseStatus: {
    marginLeft: 8,
  },
  moreExercises: {
    fontSize: 12,
    opacity: 0.7,
    textAlign: 'center',
    marginTop: 8,
    marginBottom: 12,
  },
  progressSection: {
    marginTop: 8,
  },
  progressLabel: {
    fontSize: 12,
    marginBottom: 8,
  },
  progressBar: {
    height: 6,
    borderRadius: 3,
  },
  emptyState: {
    alignItems: 'center',
    padding: 32,
    borderRadius: 12,
  },
  emptyText: {
    textAlign: 'center',
    marginTop: 16,
    marginBottom: 24,
    opacity: 0.7,
  },
  emptyButton: {
    marginTop: 8,
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

export default TodayScreen;