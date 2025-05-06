import cv2
import os

# Configuración inicial
person_name = "Angel"
data_path = "O:\PROYECTOFINAL\Data"  # Ajustar la ruta
person_path = os.path.join(data_path, person_name)

if not os.path.exists(person_path):
    os.makedirs(person_path)

# Inicializar cámara
cap = cv2.VideoCapture(0)
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
count = 0

while True:
    ret, frame = cap.read()
    if not ret:
        break

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    faces = face_cascade.detectMultiScale(gray, 1.3, 5)

    for (x, y, w, h) in faces:
        cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
        rostro = gray[y:y + h, x:x + w]
        rostro = cv2.resize(rostro, (150, 150), interpolation=cv2.INTER_CUBIC)
        cv2.imwrite(os.path.join(person_path, f"rostro_{count}.jpg"), rostro)
        count += 1

    cv2.imshow("Capturando Rostros", frame)
    if cv2.waitKey(1) == 27 or count >= 300:  # 27 = ESC
        break

cap.release()
cv2.destroyAllWindows()