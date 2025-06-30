import React from 'react';
import { View, Text, StyleSheet } from 'react-native';

export const ContactScreen = () => (
  <View style={styles.container}>
    <Text style={styles.text}>Pantalla de Contacto</Text>
  </View>
);

const styles = StyleSheet.create({
  container: { flex: 1, justifyContent: 'center', alignItems: 'center' },
  text: { fontSize: 24 },
});