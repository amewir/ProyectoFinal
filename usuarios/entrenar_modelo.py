# entrenando_modelo.py (actualizado)
import cv2
import os
import numpy as np
import django
import logging

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'veterinaria.settings')
django.setup()

from usuarios.models import Usuario

logger = logging.getLogger(__name__)

data_path = "O:\PROYECTOFINAL\Data"
people_list = os.listdir(data_path)
labels = []
faces_data = []

for name_dir in people_list:
    person_path = os.path.join(data_path, name_dir)
    
    try:
        user = Usuario.objects.get(username=name_dir)
        user_id = user.id
    except Usuario.DoesNotExist:
        logger.warning(f"Usuario {name_dir} no encontrado, omitiendo...")
        continue

    for file_name in os.listdir(person_path):
        img_path = os.path.join(person_path, file_name)
        img = cv2.imread(img_path, cv2.IMREAD_GRAYSCALE)
        if img is not None:
            faces_data.append(img)
            labels.append(user_id)
        else:
            logger.warning(f"Error al cargar imagen: {img_path}")

model = cv2.face.LBPHFaceRecognizer_create()
model.train(faces_data, np.array(labels))
model.save("modelo_lbph.yml")
print("Modelo actualizado con IDs de usuario!")