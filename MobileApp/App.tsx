import React, { useEffect, useState } from 'react';
import { SafeAreaView, View, Text, StyleSheet, Button, ActivityIndicator, Alert } from 'react-native';

// La URL de tu API local. 
// ¡OJO! Desde el emulador de Android, no puedes usar 'localhost' o '127.0.0.1'.
// Debes usar la dirección IP especial '10.0.2.2' que apunta al 'localhost' de tu ordenador.
const API_URL = 'http://localhost:8081/api/workouts/';

const App = () => {
  // --- Estados de nuestro componente ---
  
  // 'loading' nos servirá para mostrar un indicador de carga mientras esperamos la respuesta.
  const [loading, setLoading] = useState(false);
  
  // 'data' guardará los datos que recibamos de la API.
  const [data, setData] = useState(null);
  
  // 'error' guardará cualquier error que ocurra durante la petición.
  const [error, setError] = useState(null);

  // --- Función para llamar a la API ---
  const fetchWorkouts = () => {
    setLoading(true); // Empezamos a cargar
    setError(null);   // Limpiamos errores anteriores
    
    fetch(API_URL)
      .then(response => {
        // Si la respuesta no es OK (ej. error 500), lanzamos un error
        if (!response.ok) {
          throw new Error('La respuesta de la red no fue OK');
        }
        return response.json(); // Convertimos la respuesta a JSON
      })
      .then(json => {
        setData(json); // Guardamos los datos en nuestro estado
      })
      .catch(error => {
        console.error(error);
        setError('Ha ocurrido un error al obtener los datos.'); // Guardamos el error
        Alert.alert("Error de Conexión", "No se pudo conectar con el servidor. Asegúrate de que el servidor de Django está funcionando.");
      })
      .finally(() => {
        setLoading(false); // Terminamos de cargar, tanto si hubo éxito como si hubo error
      });
  };

  // --- Renderizado del componente ---
  return (
    <SafeAreaView style={styles.container}>
      <View style={styles.content}>
        <Text style={styles.title}>FitControl App</Text>
        <Text style={styles.subtitle}>Conexión con el Backend</Text>
        
        <View style={styles.buttonContainer}>
          <Button title="Cargar Entrenamientos" onPress={fetchWorkouts} disabled={loading} />
        </View>
        
        <View style={styles.resultContainer}>
          {/* Si está cargando, muestra el indicador */}
          {loading && <ActivityIndicator size="large" color="#0000ff" />}
          
          {/* Si hay un error, muestra el mensaje de error */}
          {error && <Text style={styles.errorText}>{error}</Text>}
          
          {/* Si tenemos datos, los mostramos */}
          {data && (
            <View>
              <Text style={styles.successText}>¡Conexión exitosa!</Text>
              <Text style={styles.dataText}>Datos recibidos de la API:</Text>
              {/* Usamos JSON.stringify para mostrar el objeto de datos de forma legible */}
              <Text style={styles.rawData}>{JSON.stringify(data, null, 2)}</Text>
            </View>
          )}
        </View>
      </View>
    </SafeAreaView>
  );
};

// --- Estilos ---
const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: '#f0f0f0' },
  content: { padding: 20, alignItems: 'center' },
  title: { fontSize: 28, fontWeight: 'bold', marginBottom: 10 },
  subtitle: { fontSize: 18, color: 'gray', marginBottom: 30 },
  buttonContainer: { marginVertical: 20 },
  resultContainer: {
    marginTop: 20,
    padding: 15,
    width: '100%',
    backgroundColor: 'white',
    borderRadius: 8,
    borderWidth: 1,
    borderColor: '#ddd',
    minHeight: 100,
    justifyContent: 'center',
    alignItems: 'center',
  },
  successText: { color: 'green', fontWeight: 'bold', marginBottom: 10 },
  errorText: { color: 'red', fontWeight: 'bold' },
  dataText: { fontWeight: 'bold', marginBottom: 5 },
  rawData: { fontFamily: 'monospace' }, // Usamos una fuente monoespaciada para el JSON
});

export default App;