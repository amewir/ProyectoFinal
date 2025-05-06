import cv2
import os
import numpy as np

data_path = "O:\PROYECTOFINAL\Data"
people_list = os.listdir(data_path)
labels = []
faces_data = []
label = 0

for name_dir in people_list:
    person_path = os.path.join(data_path, name_dir)
    
    for file_name in os.listdir(person_path):
        img_path = os.path.join(person_path, file_name)
        img = cv2.imread(img_path, cv2.IMREAD_GRAYSCALE)
        faces_data.append(img)
        labels.append(label)
    
    label += 1

# Crear y entrenar el modelo LBPH
model = cv2.face.LBPHFaceRecognizer_create()
model.train(faces_data, np.array(labels))

# Guardar modelo
model.save("modelo_lbph.yml")
print("Modelo LBPH entrenado y guardado!")