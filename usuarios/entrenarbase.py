import os
import cv2
import numpy as np
from PIL import Image
import django
import sys

# Inicializar Django
sys.path.append('O:/PROYECTOFINAL')  # Ajusta según tu estructura
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "veterinaria.settings")  # ← Cambiar
django.setup()

from usuarios.models import Usuario  # Ajusta si el modelo está en otro lugar

# Rutas
dataset_path = 'O:/PROYECTOFINAL/media/facial_data'
modelo_path = 'O:/PROYECTOFINAL/media/modelo_lbph.yml'

# Inicializar el reconocedor y el detector de rostros
recognizer = cv2.face.LBPHFaceRecognizer_create()
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

faces = []
ids = []

# Recorrer directorios de imágenes
for root, dirs, files in os.walk(dataset_path):
    for file in files:
        if file.lower().endswith(('.jpg', '.png')):
            path = os.path.join(root, file)
            filename = os.path.basename(file)

            # Extraer el nombre de usuario del nombre del archivo: User_juanperez-01.jpg
            if filename.startswith('User_'):
                nombre = filename.split('User_')[1].split('-')[0]

                try:
                    usuario = Usuario.objects.get(username=nombre)  # O usa otro campo como .nombre si aplica
                    user_id = usuario.id
                except Usuario.DoesNotExist:
                    print(f"⚠️ Usuario '{nombre}' no encontrado en la base de datos.")
                    continue

                # Leer imagen y convertir a escala de grises
                pil_image = Image.open(path).convert('L')
                img_numpy = np.array(pil_image, 'uint8')

                # Detectar rostro
                rostros = face_cascade.detectMultiScale(img_numpy)
                for (x, y, w, h) in rostros:
                    rostro_recortado = img_numpy[y:y+h, x:x+w]
                    faces.append(rostro_recortado)
                    ids.append(user_id)

# Entrenar el modelo
if faces and ids:
    recognizer.train(faces, np.array(ids))
    recognizer.save(modelo_path)
    print(f"✅ Modelo entrenado y guardado en: {modelo_path}")
else:
    print("❌ No se encontraron rostros válidos para entrenar.")
