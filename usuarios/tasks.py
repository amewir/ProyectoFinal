from celery import shared_task
from .models import FacialData
import cv2
import numpy as np
import logging

logger = logging.getLogger(__name__)

@shared_task
def entrenar_modelo_async():
    try:
        facial_data = FacialData.objects.all().select_related('usuario')
        faces = []
        labels = []
        
        for data in facial_data:
            try:
                nparr = np.frombuffer(data.imagen.read(), np.uint8)
                img = cv2.imdecode(nparr, cv2.IMREAD_GRAYSCALE)
                faces.append(img)
                labels.append(data.usuario.id)
            except Exception as e:
                logger.error(f"Error procesando {data.id}: {str(e)}")
                continue
        
        if len(faces) > 0:
            model = cv2.face.LBPHFaceRecognizer_create()
            model.train(faces, np.array(labels))
            model.save('modelo_lbph.yml')
            
    except Exception as e:
        logger.error(f"Error en entrenamiento: {str(e)}")