/**
 * Cliente de API para Fit_Control
 * 
 * Configuración centralizada de Axios con interceptors para JWT,
 * manejo de errores y retry automático.
 */

import axios, { AxiosInstance, AxiosError, AxiosResponse } from 'axios';
import AsyncStorage from '@react-native-async-storage/async-storage';

// Configuración de la API
const API_BASE_URL = __DEV__ 
  ? 'http://10.0.2.2:8000/api'  // Android emulator
  : 'https://api.fitcontrol.com/api';  // Producción

const API_TIMEOUT = 30000; // 30 segundos

// Crear instancia de Axios
export const apiClient: AxiosInstance = axios.create({
  baseURL: API_BASE_URL,
  timeout: API_TIMEOUT,
  headers: {
    'Content-Type': 'application/json',
    'Accept': 'application/json',
  },
});

// Interceptor de request para agregar token JWT
apiClient.interceptors.request.use(
  async (config) => {
    try {
      // Obtener token del storage
      const authData = await AsyncStorage.getItem('auth-storage');
      
      if (authData) {
        const { token } = JSON.parse(authData).state;
        
        if (token) {
          config.headers.Authorization = `Bearer ${token}`;
        }
      }
    } catch (error) {
      console.warn('Error retrieving auth token:', error);
    }
    
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Interceptor de response para manejo de errores y refresh de token
apiClient.interceptors.response.use(
  (response: AxiosResponse) => {
    return response;
  },
  async (error: AxiosError) => {
    const originalRequest = error.config as any;

    // Si el token ha expirado (401) y no es un retry
    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;

      try {
        // Intentar renovar el token
        const authData = await AsyncStorage.getItem('auth-storage');
        
        if (authData) {
          const { refreshToken } = JSON.parse(authData).state;
          
          if (refreshToken) {
            const refreshResponse = await axios.post(
              `${API_BASE_URL}/auth/refresh/`,
              { refresh: refreshToken }
            );

            const newToken = refreshResponse.data.access;
            
            // Actualizar token en storage
            const updatedAuthData = {
              ...JSON.parse(authData),
              state: {
                ...JSON.parse(authData).state,
                token: newToken,
              },
            };
            
            await AsyncStorage.setItem('auth-storage', JSON.stringify(updatedAuthData));
            
            // Reintentar request original con nuevo token
            originalRequest.headers.Authorization = `Bearer ${newToken}`;
            return apiClient(originalRequest);
          }
        }
      } catch (refreshError) {
        // Si falla el refresh, limpiar storage y redirigir al login
        await AsyncStorage.removeItem('auth-storage');
        // TODO: Navegar al login screen
        console.error('Token refresh failed:', refreshError);
      }
    }

    return Promise.reject(error);
  }
);

// Funciones auxiliares para diferentes tipos de requests

/**
 * Cliente para uploading de archivos (FormData)
 */
export const apiClientFormData = axios.create({
  baseURL: API_BASE_URL,
  timeout: 60000, // 1 minuto para uploads
  headers: {
    'Content-Type': 'multipart/form-data',
  },
});

// Aplicar los mismos interceptors al cliente de FormData
apiClientFormData.interceptors.request.use(apiClient.interceptors.request.handlers[0].fulfilled);
apiClientFormData.interceptors.response.use(
  apiClient.interceptors.response.handlers[0].fulfilled,
  apiClient.interceptors.response.handlers[0].rejected
);

/**
 * Tipos para responses comunes
 */
export interface ApiResponse<T = any> {
  data: T;
  message?: string;
  status: number;
}

export interface PaginatedResponse<T = any> {
  count: number;
  next: string | null;
  previous: string | null;
  results: T[];
}

/**
 * Funciones helper para requests comunes
 */
export const api = {
  get: <T = any>(url: string, params?: any) => 
    apiClient.get<T>(url, { params }),
  
  post: <T = any>(url: string, data?: any) => 
    apiClient.post<T>(url, data),
  
  put: <T = any>(url: string, data?: any) => 
    apiClient.put<T>(url, data),
  
  patch: <T = any>(url: string, data?: any) => 
    apiClient.patch<T>(url, data),
  
  delete: <T = any>(url: string) => 
    apiClient.delete<T>(url),
  
  upload: <T = any>(url: string, formData: FormData) => 
    apiClientFormData.post<T>(url, formData),
};

/**
 * Funciones para manejo de errores
 */
export const getErrorMessage = (error: any): string => {
  if (error.response?.data?.detail) {
    return error.response.data.detail;
  }
  
  if (error.response?.data?.message) {
    return error.response.data.message;
  }
  
  if (error.response?.data?.error) {
    return error.response.data.error;
  }
  
  if (error.message) {
    return error.message;
  }
  
  return 'Ha ocurrido un error inesperado';
};

export const isNetworkError = (error: any): boolean => {
  return !error.response && error.request;
};

export const isServerError = (error: any): boolean => {
  return error.response?.status >= 500;
};

export const isClientError = (error: any): boolean => {
  return error.response?.status >= 400 && error.response?.status < 500;
};

export default apiClient;