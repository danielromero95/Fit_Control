import cv2
import numpy as np

# Preprocesamiento de imágenes: conversión de espacio de color
def convert_color(frame, target_space='rgb'):
    """
    Convierte `frame` de BGR a RGB o a escala de grises.
    """
    if target_space == 'rgb':
        return cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    elif target_space == 'gray':
        return cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    else:
        raise ValueError(f"Espacio de color desconocido: {target_space}")


# Preprocesamiento de imágenes: redimensionar y normalizar
def preprocess_resize_normalize(frames, target_size=(256,256)):
    processed = []
    for f in frames:
        img = cv2.resize(f, target_size, interpolation=cv2.INTER_AREA)
        img = img.astype('float32') / 255.0
        processed.append(img)
    return np.stack(processed)  # shape: (n_frames, H, W, C)


# Preprocesamiento de imágenes: aplicar desenfoque gaussiano
def apply_gaussian_blur(frames, kernel_size=(3,3)):
    blurred = []
    for f in frames:
        # f es array float32 en [0,1]; convertir a uint8 si es necesario
        img_uint8 = (f * 255).astype('uint8')
        blur = cv2.GaussianBlur(img_uint8, kernel_size, 0)
        blur = blur.astype('float32') / 255.0
        blurred.append(blur)
    return blurred

# Preprocesamiento de imágenes: detección y recorte de personas
hog = cv2.HOGDescriptor()
hog.setSVMDetector(cv2.HOGDescriptor_getDefaultPeopleDetector())

def detect_and_crop_person(frame, margin=0.1):
    """
    Detecta persona y recorta con un margen relativo.
    Retorna el recorte y las coordenadas originales.
    """

    """
    Pruebas unitarias sugeridas:
    Test con imagen que contenga personas: verificar que el ROI sea más pequeño que la imagen original. 
    Test con imagen sin personas: ROI = imagen original.
    """
    rects, _ = hog.detectMultiScale(frame, winStride=(8,8))
    if len(rects) == 0:
        return frame  # Sin detección, devolver frame completo
    x, y, w, h = rects[0]
    # Aplicar margen
    dw = int(w * margin)
    dh = int(h * margin)
    x1 = max(0, x - dw)
    y1 = max(0, y - dh)
    x2 = min(frame.shape[1], x + w + dw)
    y2 = min(frame.shape[0], y + h + dh)
    return frame[y1:y2, x1:x2]

# Preprocesamiento de imágenes: aplicar CLAHE
def apply_CLAHE(frame):
    """
    Asume que `frame` está en RGB. Aplica CLAHE en canal Y y retorna frame RGB.
    """

    """
    Pruebas unitarias sugeridas:
    Test con imagen en escala de grises: verificar que el resultado sea igual al original.
    Test con imagen en color: verificar que el resultado tenga el mismo tamaño y tipo de datos.
    Test con imagen sin contraste: verificar que el resultado no cambie significativamente.
    Verificar que el output tenga valores en [0,1].
    """
    # Convertir a YUV
    yuv = cv2.cvtColor((frame * 255).astype('uint8'), cv2.COLOR_RGB2YUV)
    y, u, v = cv2.split(yuv)
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
    y_eq = clahe.apply(y)
    yuv_eq = cv2.merge((y_eq, u, v))
    rgb_eq = cv2.cvtColor(yuv_eq, cv2.COLOR_YUV2RGB)
    return rgb_eq.astype('float32') / 255.0
