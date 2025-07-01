import React, { useState, useRef, useEffect } from 'react';
import {
  View,
  Text,
  StyleSheet,
  TouchableOpacity,
  Dimensions,
  StatusBar,
  Alert,
  Modal,
} from 'react-native';
import { Camera, useCameraDevices } from 'react-native-vision-camera';
import { LinearGradient } from 'react-native-linear-gradient';
import Icon from 'react-native-vector-icons/Ionicons';

const { width, height } = Dimensions.get('window');

export const RecordingScreen = ({ navigation }: any) => {
  const [isRecording, setIsRecording] = useState(false);
  const [hasPermission, setHasPermission] = useState(false);
  const [exerciseType, setExerciseType] = useState<string>('squat');
  const [showExerciseModal, setShowExerciseModal] = useState(false);
  const [recordingTime, setRecordingTime] = useState(0);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  
  const camera = useRef<Camera>(null);
  const devices = useCameraDevices();
  const device = devices.back;

  const exercises = [
    { id: 'squat', name: 'Sentadilla', icon: 'fitness', description: 'Análisis de técnica de sentadilla' },
    { id: 'deadlift', name: 'Peso Muerto', icon: 'barbell', description: 'Análisis de técnica de deadlift' },
    { id: 'bench', name: 'Press Banca', icon: 'analytics', description: 'Análisis de técnica de press banca' },
    { id: 'overhead', name: 'Press Militar', icon: 'trending-up', description: 'Análisis de press por encima de la cabeza' },
  ];

  useEffect(() => {
    checkCameraPermission();
  }, []);

  useEffect(() => {
    let interval: NodeJS.Timeout;
    if (isRecording) {
      interval = setInterval(() => {
        setRecordingTime(prev => prev + 1);
      }, 1000);
    } else {
      setRecordingTime(0);
    }
    return () => clearInterval(interval);
  }, [isRecording]);

  const checkCameraPermission = async () => {
    try {
      const cameraPermission = await Camera.getCameraPermissionStatus();
      const microphonePermission = await Camera.getMicrophonePermissionStatus();
      
      if (cameraPermission === 'authorized' && microphonePermission === 'authorized') {
        setHasPermission(true);
      } else {
        const newCameraPermission = await Camera.requestCameraPermission();
        const newMicrophonePermission = await Camera.requestMicrophonePermission();
        setHasPermission(newCameraPermission === 'authorized' && newMicrophonePermission === 'authorized');
      }
    } catch (error) {
      console.error('Error checking permissions:', error);
      setHasPermission(false);
    }
  };

  const startRecording = async () => {
    if (!camera.current || !hasPermission) return;
    
    try {
      setIsRecording(true);
      await camera.current.startRecording({
        flash: 'off',
        onRecordingFinished: (video) => {
          console.log('Recording finished:', video);
          setIsRecording(false);
          processRecording(video);
        },
        onRecordingError: (error) => {
          console.error('Recording error:', error);
          setIsRecording(false);
          Alert.alert('Error', 'Error al grabar el video');
        },
      });
    } catch (error) {
      console.error('Start recording error:', error);
      setIsRecording(false);
    }
  };

  const stopRecording = async () => {
    if (!camera.current || !isRecording) return;
    
    try {
      await camera.current.stopRecording();
    } catch (error) {
      console.error('Stop recording error:', error);
    }
  };

  const processRecording = async (video: any) => {
    setIsAnalyzing(true);
    
    // Simular procesamiento de análisis
    setTimeout(() => {
      setIsAnalyzing(false);
      Alert.alert(
        'Análisis Completado',
        'Tu video ha sido analizado. Ve a la sección de Análisis para ver los resultados.',
        [
          { text: 'Ver Análisis', onPress: () => navigation.navigate('Análisis') },
          { text: 'OK' }
        ]
      );
    }, 3000);
  };

  const formatTime = (seconds: number) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
  };

  const selectedExercise = exercises.find(ex => ex.id === exerciseType);

  if (!hasPermission) {
    return (
      <View style={styles.permissionContainer}>
        <Icon name="camera" size={80} color="#BB86FC" />
        <Text style={styles.permissionTitle}>Permisos de Cámara Necesarios</Text>
        <Text style={styles.permissionText}>
          Para analizar tu técnica deportiva, necesitamos acceso a tu cámara y micrófono.
        </Text>
        <TouchableOpacity style={styles.permissionButton} onPress={checkCameraPermission}>
          <Text style={styles.permissionButtonText}>Permitir Acceso</Text>
        </TouchableOpacity>
      </View>
    );
  }

  if (!device) {
    return (
      <View style={styles.errorContainer}>
        <Text style={styles.errorText}>Cámara no disponible</Text>
      </View>
    );
  }

  return (
    <View style={styles.container}>
      <StatusBar barStyle="light-content" backgroundColor="#121212" />
      
      {/* Camera View */}
      <View style={styles.cameraContainer}>
        <Camera
          ref={camera}
          style={styles.camera}
          device={device}
          isActive={true}
          video={true}
          audio={true}
        />
        
        {/* Overlay */}
        <View style={styles.overlay}>
          {/* Top Controls */}
          <View style={styles.topControls}>
            <TouchableOpacity 
              style={styles.backButton}
              onPress={() => navigation.goBack()}
            >
              <Icon name="arrow-back" size={24} color="white" />
            </TouchableOpacity>
            
            <View style={styles.exerciseInfo}>
              <Text style={styles.exerciseTitle}>{selectedExercise?.name}</Text>
              <Text style={styles.exerciseDescription}>{selectedExercise?.description}</Text>
            </View>
            
            <TouchableOpacity 
              style={styles.exerciseButton}
              onPress={() => setShowExerciseModal(true)}
            >
              <Icon name="list" size={24} color="white" />
            </TouchableOpacity>
          </View>

          {/* Recording Timer */}
          {isRecording && (
            <View style={styles.recordingTimer}>
              <View style={styles.recordingDot} />
              <Text style={styles.timerText}>{formatTime(recordingTime)}</Text>
            </View>
          )}

          {/* Guidelines */}
          <View style={styles.guidelines}>
            <View style={styles.guideline} />
            <View style={[styles.guideline, styles.guidelineVertical]} />
          </View>

          {/* Bottom Controls */}
          <View style={styles.bottomControls}>
            <TouchableOpacity 
              style={styles.controlButton}
              onPress={() => navigation.navigate('Historial')}
            >
              <Icon name="folder" size={24} color="white" />
              <Text style={styles.controlLabel}>Historial</Text>
            </TouchableOpacity>
            
            <TouchableOpacity
              style={[styles.recordButton, isRecording && styles.recordButtonActive]}
              onPress={isRecording ? stopRecording : startRecording}
              disabled={isAnalyzing}
            >
              {isAnalyzing ? (
                <Icon name="hourglass" size={32} color="white" />
              ) : (
                <View style={[styles.recordButtonInner, isRecording && styles.recordButtonInnerActive]} />
              )}
            </TouchableOpacity>
            
            <TouchableOpacity 
              style={styles.controlButton}
              onPress={() => navigation.navigate('Configuración')}
            >
              <Icon name="settings" size={24} color="white" />
              <Text style={styles.controlLabel}>Config</Text>
            </TouchableOpacity>
          </View>
        </View>
      </View>

      {/* Exercise Selection Modal */}
      <Modal
        visible={showExerciseModal}
        transparent={true}
        animationType="slide"
        onRequestClose={() => setShowExerciseModal(false)}
      >
        <View style={styles.modalOverlay}>
          <View style={styles.modalContent}>
            <View style={styles.modalHeader}>
              <Text style={styles.modalTitle}>Seleccionar Ejercicio</Text>
              <TouchableOpacity onPress={() => setShowExerciseModal(false)}>
                <Icon name="close" size={24} color="#FFFFFF" />
              </TouchableOpacity>
            </View>
            
            {exercises.map((exercise) => (
              <TouchableOpacity
                key={exercise.id}
                style={[
                  styles.exerciseOption,
                  exerciseType === exercise.id && styles.exerciseOptionSelected
                ]}
                onPress={() => {
                  setExerciseType(exercise.id);
                  setShowExerciseModal(false);
                }}
              >
                <Icon name={exercise.icon as any} size={24} color="#BB86FC" />
                <View style={styles.exerciseOptionText}>
                  <Text style={styles.exerciseOptionTitle}>{exercise.name}</Text>
                  <Text style={styles.exerciseOptionDesc}>{exercise.description}</Text>
                </View>
                {exerciseType === exercise.id && (
                  <Icon name="checkmark-circle" size={24} color="#03DAC6" />
                )}
              </TouchableOpacity>
            ))}
          </View>
        </View>
      </Modal>

      {/* Analysis Loading */}
      {isAnalyzing && (
        <View style={styles.analyzingOverlay}>
          <View style={styles.analyzingContent}>
            <Icon name="analytics" size={48} color="#BB86FC" />
            <Text style={styles.analyzingTitle}>Analizando Técnica...</Text>
            <Text style={styles.analyzingText}>
              Procesando video con MediaPipe para detectar puntos clave y evaluar tu forma
            </Text>
          </View>
        </View>
      )}
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#121212',
  },
  permissionContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    backgroundColor: '#121212',
    padding: 20,
  },
  permissionTitle: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#FFFFFF',
    marginTop: 20,
    marginBottom: 10,
    textAlign: 'center',
  },
  permissionText: {
    fontSize: 16,
    color: '#AAAAAA',
    textAlign: 'center',
    marginBottom: 30,
    lineHeight: 24,
  },
  permissionButton: {
    backgroundColor: '#BB86FC',
    paddingHorizontal: 30,
    paddingVertical: 15,
    borderRadius: 25,
  },
  permissionButtonText: {
    color: 'white',
    fontSize: 16,
    fontWeight: 'bold',
  },
  errorContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    backgroundColor: '#121212',
  },
  errorText: {
    color: '#FFFFFF',
    fontSize: 18,
  },
  cameraContainer: {
    flex: 1,
  },
  camera: {
    flex: 1,
  },
  overlay: {
    position: 'absolute',
    top: 0,
    left: 0,
    right: 0,
    bottom: 0,
  },
  topControls: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    paddingTop: 50,
    paddingHorizontal: 20,
    paddingBottom: 20,
  },
  backButton: {
    width: 44,
    height: 44,
    borderRadius: 22,
    backgroundColor: 'rgba(0, 0, 0, 0.5)',
    justifyContent: 'center',
    alignItems: 'center',
  },
  exerciseInfo: {
    flex: 1,
    alignItems: 'center',
    marginHorizontal: 15,
  },
  exerciseTitle: {
    color: 'white',
    fontSize: 18,
    fontWeight: 'bold',
  },
  exerciseDescription: {
    color: 'rgba(255, 255, 255, 0.8)',
    fontSize: 14,
    marginTop: 2,
  },
  exerciseButton: {
    width: 44,
    height: 44,
    borderRadius: 22,
    backgroundColor: 'rgba(0, 0, 0, 0.5)',
    justifyContent: 'center',
    alignItems: 'center',
  },
  recordingTimer: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    backgroundColor: 'rgba(207, 102, 121, 0.9)',
    paddingHorizontal: 15,
    paddingVertical: 8,
    borderRadius: 20,
    position: 'absolute',
    top: 120,
    alignSelf: 'center',
  },
  recordingDot: {
    width: 8,
    height: 8,
    borderRadius: 4,
    backgroundColor: 'white',
    marginRight: 8,
  },
  timerText: {
    color: 'white',
    fontSize: 16,
    fontWeight: 'bold',
  },
  guidelines: {
    position: 'absolute',
    top: '50%',
    left: '50%',
    width: 200,
    height: 200,
    marginLeft: -100,
    marginTop: -100,
  },
  guideline: {
    position: 'absolute',
    backgroundColor: 'rgba(187, 134, 252, 0.3)',
  },
  guidelineVertical: {
    width: 1,
    height: '100%',
    left: '50%',
  },
  bottomControls: {
    position: 'absolute',
    bottom: 50,
    left: 0,
    right: 0,
    flexDirection: 'row',
    justifyContent: 'space-around',
    alignItems: 'center',
    paddingHorizontal: 30,
  },
  controlButton: {
    alignItems: 'center',
    opacity: 0.8,
  },
  controlLabel: {
    color: 'white',
    fontSize: 12,
    marginTop: 5,
  },
  recordButton: {
    width: 80,
    height: 80,
    borderRadius: 40,
    backgroundColor: 'rgba(255, 255, 255, 0.3)',
    justifyContent: 'center',
    alignItems: 'center',
    borderWidth: 4,
    borderColor: 'white',
  },
  recordButtonActive: {
    borderColor: '#CF6679',
  },
  recordButtonInner: {
    width: 60,
    height: 60,
    borderRadius: 30,
    backgroundColor: '#CF6679',
  },
  recordButtonInnerActive: {
    borderRadius: 8,
    width: 40,
    height: 40,
  },
  modalOverlay: {
    flex: 1,
    backgroundColor: 'rgba(0, 0, 0, 0.8)',
    justifyContent: 'flex-end',
  },
  modalContent: {
    backgroundColor: '#1F1F1F',
    borderTopLeftRadius: 20,
    borderTopRightRadius: 20,
    paddingBottom: 30,
  },
  modalHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    padding: 20,
    borderBottomWidth: 1,
    borderBottomColor: '#333333',
  },
  modalTitle: {
    color: '#FFFFFF',
    fontSize: 20,
    fontWeight: 'bold',
  },
  exerciseOption: {
    flexDirection: 'row',
    alignItems: 'center',
    padding: 20,
    borderBottomWidth: 1,
    borderBottomColor: '#333333',
  },
  exerciseOptionSelected: {
    backgroundColor: 'rgba(187, 134, 252, 0.1)',
  },
  exerciseOptionText: {
    flex: 1,
    marginLeft: 15,
  },
  exerciseOptionTitle: {
    color: '#FFFFFF',
    fontSize: 16,
    fontWeight: '600',
  },
  exerciseOptionDesc: {
    color: '#AAAAAA',
    fontSize: 14,
    marginTop: 2,
  },
  analyzingOverlay: {
    position: 'absolute',
    top: 0,
    left: 0,
    right: 0,
    bottom: 0,
    backgroundColor: 'rgba(18, 18, 18, 0.9)',
    justifyContent: 'center',
    alignItems: 'center',
  },
  analyzingContent: {
    alignItems: 'center',
    padding: 30,
  },
  analyzingTitle: {
    color: '#FFFFFF',
    fontSize: 24,
    fontWeight: 'bold',
    marginTop: 20,
    marginBottom: 10,
  },
  analyzingText: {
    color: '#AAAAAA',
    fontSize: 16,
    textAlign: 'center',
    lineHeight: 24,
  },
});