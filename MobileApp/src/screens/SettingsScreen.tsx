import React, { useState } from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  TouchableOpacity,
  Switch,
  StatusBar,
} from 'react-native';
import Icon from 'react-native-vector-icons/Ionicons';

export const SettingsScreen = ({ navigation }: any) => {
  const [notifications, setNotifications] = useState(true);
  const [autoSave, setAutoSave] = useState(true);
  const [highQuality, setHighQuality] = useState(false);

  const settingsOptions = [
    {
      id: 'notifications',
      title: 'Notificaciones',
      description: 'Recibir notificaciones de análisis completados',
      type: 'switch',
      value: notifications,
      onToggle: setNotifications,
      icon: 'notifications'
    },
    {
      id: 'autoSave',
      title: 'Guardado Automático',
      description: 'Guardar automáticamente los videos analizados',
      type: 'switch',
      value: autoSave,
      onToggle: setAutoSave,
      icon: 'save'
    },
    {
      id: 'highQuality',
      title: 'Alta Calidad',
      description: 'Grabación en alta resolución (consume más batería)',
      type: 'switch',
      value: highQuality,
      onToggle: setHighQuality,
      icon: 'videocam'
    },
  ];

  const infoOptions = [
    {
      id: 'about',
      title: 'Acerca de',
      description: 'Información sobre la aplicación',
      icon: 'information-circle',
      onPress: () => console.log('About pressed')
    },
    {
      id: 'help',
      title: 'Ayuda',
      description: 'Guías y soporte técnico',
      icon: 'help-circle',
      onPress: () => console.log('Help pressed')
    },
    {
      id: 'privacy',
      title: 'Privacidad',
      description: 'Política de privacidad y datos',
      icon: 'shield-checkmark',
      onPress: () => console.log('Privacy pressed')
    },
  ];

  return (
    <View style={styles.container}>
      <StatusBar barStyle="light-content" backgroundColor="#121212" />
      
      <ScrollView style={styles.content} showsVerticalScrollIndicator={false}>
        <View style={styles.header}>
          <Text style={styles.title}>Configuración</Text>
          <Text style={styles.subtitle}>Personaliza tu experiencia de análisis</Text>
        </View>

        {/* App Settings */}
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>Configuración de la App</Text>
          {settingsOptions.map((option) => (
            <View key={option.id} style={styles.settingItem}>
              <View style={styles.settingIcon}>
                <Icon name={option.icon as any} size={24} color="#BB86FC" />
              </View>
              <View style={styles.settingContent}>
                <Text style={styles.settingTitle}>{option.title}</Text>
                <Text style={styles.settingDescription}>{option.description}</Text>
              </View>
              <Switch
                value={option.value}
                onValueChange={option.onToggle}
                trackColor={{ false: '#333333', true: '#BB86FC' }}
                thumbColor={option.value ? '#FFFFFF' : '#AAAAAA'}
              />
            </View>
          ))}
        </View>

        {/* Camera Settings */}
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>Configuración de Cámara</Text>
          
          <TouchableOpacity style={styles.settingItem}>
            <View style={styles.settingIcon}>
              <Icon name="camera" size={24} color="#BB86FC" />
            </View>
            <View style={styles.settingContent}>
              <Text style={styles.settingTitle}>Resolución de Video</Text>
              <Text style={styles.settingDescription}>1080p (Recomendado para análisis)</Text>
            </View>
            <Icon name="chevron-forward" size={20} color="#666" />
          </TouchableOpacity>

          <TouchableOpacity style={styles.settingItem}>
            <View style={styles.settingIcon}>
              <Icon name="speedometer" size={24} color="#BB86FC" />
            </View>
            <View style={styles.settingContent}>
              <Text style={styles.settingTitle}>FPS de Grabación</Text>
              <Text style={styles.settingDescription}>30 FPS</Text>
            </View>
            <Icon name="chevron-forward" size={20} color="#666" />
          </TouchableOpacity>
        </View>

        {/* Analysis Settings */}
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>Configuración de Análisis</Text>
          
          <TouchableOpacity style={styles.settingItem}>
            <View style={styles.settingIcon}>
              <Icon name="analytics" size={24} color="#BB86FC" />
            </View>
            <View style={styles.settingContent}>
              <Text style={styles.settingTitle}>Precisión de MediaPipe</Text>
              <Text style={styles.settingDescription}>Alta precisión (más lento pero más exacto)</Text>
            </View>
            <Icon name="chevron-forward" size={20} color="#666" />
          </TouchableOpacity>

          <TouchableOpacity style={styles.settingItem}>
            <View style={styles.settingIcon}>
              <Icon name="time" size={24} color="#BB86FC" />
            </View>
            <View style={styles.settingContent}>
              <Text style={styles.settingTitle}>Tiempo de Retención</Text>
              <Text style={styles.settingDescription}>Mantener análisis por 30 días</Text>
            </View>
            <Icon name="chevron-forward" size={20} color="#666" />
          </TouchableOpacity>
        </View>

        {/* Information */}
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>Información</Text>
          {infoOptions.map((option) => (
            <TouchableOpacity 
              key={option.id} 
              style={styles.settingItem}
              onPress={option.onPress}
            >
              <View style={styles.settingIcon}>
                <Icon name={option.icon as any} size={24} color="#BB86FC" />
              </View>
              <View style={styles.settingContent}>
                <Text style={styles.settingTitle}>{option.title}</Text>
                <Text style={styles.settingDescription}>{option.description}</Text>
              </View>
              <Icon name="chevron-forward" size={20} color="#666" />
            </TouchableOpacity>
          ))}
        </View>

        {/* App Version */}
        <View style={styles.versionContainer}>
          <Text style={styles.versionText}>TechniqueAnalyzer v1.0.0</Text>
          <Text style={styles.versionSubtext}>Análisis de técnica deportiva con IA</Text>
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
  section: {
    marginBottom: 24,
  },
  sectionTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#BB86FC',
    marginBottom: 12,
  },
  settingItem: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#1F1F1F',
    borderRadius: 12,
    padding: 16,
    marginBottom: 8,
  },
  settingIcon: {
    width: 40,
    height: 40,
    borderRadius: 20,
    backgroundColor: 'rgba(187, 134, 252, 0.1)',
    justifyContent: 'center',
    alignItems: 'center',
    marginRight: 12,
  },
  settingContent: {
    flex: 1,
  },
  settingTitle: {
    fontSize: 16,
    fontWeight: '600',
    color: '#FFFFFF',
    marginBottom: 2,
  },
  settingDescription: {
    fontSize: 14,
    color: '#AAAAAA',
    lineHeight: 18,
  },
  versionContainer: {
    alignItems: 'center',
    paddingVertical: 30,
    marginBottom: 20,
  },
  versionText: {
    fontSize: 16,
    fontWeight: 'bold',
    color: '#FFFFFF',
    marginBottom: 4,
  },
  versionSubtext: {
    fontSize: 14,
    color: '#AAAAAA',
  },
});