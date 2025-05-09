import os
import cv2
import numpy as np
from django.core.management.base import BaseCommand
from django.conf import settings
from usuarios.models import Usuario  # Cambia a tu modelo si tiene otro nombre

class Command(BaseCommand):
    help = 'Entrena el modelo LBPH con imágenes faciales'

    def handle(self, *args, **kwargs):
        data_dir = r'O:\PROYECTOFINAL\media\facial_data\2025\05\08'
        faces = []
        labels = []
        errores = 0

        self.stdout.write(f"📁 Leyendo imágenes en: {data_dir}")

        for root, dirs, files in os.walk(data_dir):
            for file in files:
                print(f"Procesando archivo: {file}")  # Depuración

                if file.startswith('User_') and file.endswith('.jpg'):
                    try:
                        # Extraer el nombre de usuario del archivo
                        username = file.split('User_')[1].split('-')[0]
                        print(f"Nombre de usuario extraído: {username}")  # Depuración

                        # Obtener el objeto de usuario desde la base de datos
                        user = Usuario.objects.get(username=username)
                        img_path = os.path.join(root, file)

                        # Cargar la imagen en escala de grises
                        img = cv2.imread(img_path, cv2.IMREAD_GRAYSCALE)
                        
                        if img is None:
                            self.stdout.write(self.style.WARNING(f"❌ No se pudo cargar la imagen: {img_path}"))
                            continue

                        # Detectar rostros en la imagen
                        face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
                        faces_detected = face_cascade.detectMultiScale(img, scaleFactor=1.05, minNeighbors=3)
                        print(f"Rostros detectados en {file}: {len(faces_detected)}")  # Depuración

                        for (x, y, w, h) in faces_detected:
                            rostro = img[y:y+h, x:x+w]
                            rostro = cv2.resize(rostro, (200, 200))
                            faces.append(rostro)
                            labels.append(user.id)
                            print(f"Rostro añadido: {user.id}")  # Depuración
                            break  # Solo 1 rostro por imagen

                    except Usuario.DoesNotExist:
                        errores += 1
                        self.stdout.write(self.style.WARNING(f"⚠️ Usuario no encontrado para imagen: {file}"))
                    except Exception as e:
                        errores += 1
                        self.stdout.write(self.style.ERROR(f"❌ Error procesando {file}: {str(e)}"))

        # Verificar si hay rostros detectados
        if not faces:
            self.stdout.write(self.style.ERROR("❌ No se encontraron rostros válidos para entrenar"))
            return

        self.stdout.write(f"✅ {len(faces)} rostros detectados. Entrenando modelo...")

        # Crear y entrenar el modelo LBPH
        model = cv2.face.LBPHFaceRecognizer_create()
        model.train(faces, np.array(labels))

        # Verificar y crear el directorio para el modelo
        model_path = os.path.join(settings.MEDIA_ROOT, 'modelo_lbph.yml')
        if not os.path.exists(settings.MEDIA_ROOT):
            os.makedirs(settings.MEDIA_ROOT)  # Crear directorio si no existe

        # Guardar el modelo entrenado
        model.write(model_path)

        self.stdout.write(self.style.SUCCESS(f"🎉 Modelo entrenado correctamente y guardado en: {model_path}"))
        
        if errores:
            self.stdout.write(self.style.WARNING(f"⚠️ Hubo {errores} errores durante el entrenamiento."))
