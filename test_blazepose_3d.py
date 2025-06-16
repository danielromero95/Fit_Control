import cv2
import mediapipe as mp
import numpy as np

# --- Funciones de Cálculo ---
def calculate_angle_3d(p1, p2, p3):
    """Calcula el ángulo entre 3 puntos en el espacio 3D."""
    v1 = np.array([p1.x - p2.x, p1.y - p2.y, p1.z - p2.z])
    v2 = np.array([p3.x - p2.x, p3.y - p2.y, p3.z - p2.z])
    
    dot_product = np.dot(v1, v2)
    magnitude_v1 = np.linalg.norm(v1)
    magnitude_v2 = np.linalg.norm(v2)
    
    if magnitude_v1 == 0 or magnitude_v2 == 0:
        return 180.0

    angle_rad = np.arccos(dot_product / (magnitude_v1 * magnitude_v2))
    return np.degrees(angle_rad)

# --- Configuración de MediaPipe ---
mp_pose = mp.solutions.pose
pose = mp_pose.Pose(
    static_image_mode=False,
    model_complexity=2,  # El modelo más preciso
    enable_segmentation=False,
    smooth_landmarks=True
)
mp_drawing = mp.solutions.drawing_utils

# --- Procesamiento del Vídeo ---
video_path = 'test_squat.mp4'
cap = cv2.VideoCapture(video_path)

if not cap.isOpened():
    print(f"Error: No se pudo abrir el vídeo en la ruta: {video_path}")
    exit()

frame_count = 0
while cap.isOpened():
    success, image = cap.read()
    if not success:
        print("Fin del vídeo.")
        break

    frame_count += 1
    # Convertir la imagen a RGB para MediaPipe
    image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    
    # Procesar la imagen y obtener los resultados
    results = pose.process(image_rgb)

    # Dibujar los landmarks 2D en el vídeo para visualización
    if results.pose_landmarks:
        mp_drawing.draw_landmarks(
            image, results.pose_landmarks, mp_pose.POSE_CONNECTIONS)

    # --- La Magia del 3D ---
    if results.pose_world_landmarks:
        landmarks_3d = results.pose_world_landmarks.landmark
        
        # Extraer puntos de interés (lado izquierdo como ejemplo)
        left_hip = landmarks_3d[mp_pose.PoseLandmark.LEFT_HIP.value]
        left_knee = landmarks_3d[mp_pose.PoseLandmark.LEFT_KNEE.value]
        left_ankle = landmarks_3d[mp_pose.PoseLandmark.LEFT_ANKLE.value]
        left_shoulder = landmarks_3d[mp_pose.PoseLandmark.LEFT_SHOULDER.value]
        
        # Calcular ángulos clave
        knee_angle = calculate_angle_3d(left_hip, left_knee, left_ankle)
        torso_angle = calculate_angle_3d(left_shoulder, left_hip, left_knee)
        
        # Imprimir resultados en la consola
        print(f"--- Frame {frame_count} ---")
        print(f"  Profundidad (Altura Cadera Y): {left_hip.y:.2f} m")
        print(f"  Ángulo de Rodilla: {knee_angle:.1f}°")
        print(f"  Ángulo del Torso: {torso_angle:.1f}°")

        # Mostrar los ángulos en la imagen
        cv2.putText(image, f"Rodilla: {knee_angle:.1f}", (10, 30), 
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        cv2.putText(image, f"Torso: {torso_angle:.1f}", (10, 70), 
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

    # Mostrar la imagen
    cv2.imshow('BlazePose 3D - Banco de Pruebas', image)

    if cv2.waitKey(5) & 0xFF == 27:  # Presiona ESC para salir
        break

cap.release()
cv2.destroyAllWindows()
pose.close()