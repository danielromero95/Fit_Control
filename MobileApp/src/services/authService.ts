/**
 * Servicio de autenticación para Fit_Control
 * 
 * Maneja todas las operaciones de autenticación con la API del backend.
 */

import { apiClient } from './apiClient';
import { User } from '../store/authStore';

interface LoginCredentials {
  username: string;
  password: string;
}

interface RegisterData {
  username: string;
  email: string;
  password: string;
  confirmPassword: string;
}

interface AuthResponse {
  access: string;
  refresh: string;
  user: User;
}

interface RefreshResponse {
  access: string;
  refresh?: string;
}

class AuthService {
  /**
   * Iniciar sesión
   */
  async login(credentials: LoginCredentials): Promise<AuthResponse> {
    try {
      const response = await apiClient.post('/auth/login/', credentials);
      return response.data;
    } catch (error: any) {
      throw new Error(
        error.response?.data?.detail || 
        error.response?.data?.message ||
        'Error al iniciar sesión'
      );
    }
  }

  /**
   * Registrar nuevo usuario
   */
  async register(userData: RegisterData): Promise<AuthResponse> {
    try {
      // Validar que las contraseñas coincidan
      if (userData.password !== userData.confirmPassword) {
        throw new Error('Las contraseñas no coinciden');
      }

      const { confirmPassword, ...registerData } = userData;
      const response = await apiClient.post('/auth/register/', registerData);
      
      return response.data;
    } catch (error: any) {
      throw new Error(
        error.response?.data?.detail || 
        error.response?.data?.message ||
        'Error al registrarse'
      );
    }
  }

  /**
   * Renovar token de acceso
   */
  async refreshToken(refreshToken: string): Promise<RefreshResponse> {
    try {
      const response = await apiClient.post('/auth/refresh/', {
        refresh: refreshToken,
      });
      return response.data;
    } catch (error: any) {
      throw new Error(
        error.response?.data?.detail || 
        'Error al renovar token'
      );
    }
  }

  /**
   * Verificar token
   */
  async verifyToken(token: string): Promise<boolean> {
    try {
      await apiClient.post('/auth/verify/', { token });
      return true;
    } catch (error) {
      return false;
    }
  }

  /**
   * Actualizar perfil del usuario
   */
  async updateProfile(profileData: any): Promise<User> {
    try {
      const response = await apiClient.patch('/users/profile/', profileData);
      return response.data;
    } catch (error: any) {
      throw new Error(
        error.response?.data?.detail || 
        error.response?.data?.message ||
        'Error al actualizar perfil'
      );
    }
  }

  /**
   * Obtener perfil del usuario actual
   */
  async getCurrentUser(): Promise<User> {
    try {
      const response = await apiClient.get('/users/me/');
      return response.data;
    } catch (error: any) {
      throw new Error(
        error.response?.data?.detail || 
        'Error al obtener datos del usuario'
      );
    }
  }

  /**
   * Cambiar contraseña
   */
  async changePassword(data: {
    oldPassword: string;
    newPassword: string;
    confirmPassword: string;
  }): Promise<void> {
    try {
      if (data.newPassword !== data.confirmPassword) {
        throw new Error('Las contraseñas no coinciden');
      }

      await apiClient.post('/auth/change-password/', {
        old_password: data.oldPassword,
        new_password: data.newPassword,
      });
    } catch (error: any) {
      throw new Error(
        error.response?.data?.detail || 
        error.response?.data?.message ||
        'Error al cambiar contraseña'
      );
    }
  }

  /**
   * Solicitar restablecimiento de contraseña
   */
  async requestPasswordReset(email: string): Promise<void> {
    try {
      await apiClient.post('/auth/password-reset/', { email });
    } catch (error: any) {
      throw new Error(
        error.response?.data?.detail || 
        'Error al solicitar restablecimiento de contraseña'
      );
    }
  }

  /**
   * Confirmar restablecimiento de contraseña
   */
  async confirmPasswordReset(data: {
    token: string;
    newPassword: string;
    confirmPassword: string;
  }): Promise<void> {
    try {
      if (data.newPassword !== data.confirmPassword) {
        throw new Error('Las contraseñas no coinciden');
      }

      await apiClient.post('/auth/password-reset-confirm/', {
        token: data.token,
        new_password: data.newPassword,
      });
    } catch (error: any) {
      throw new Error(
        error.response?.data?.detail || 
        'Error al restablecer contraseña'
      );
    }
  }
}

export const authService = new AuthService();