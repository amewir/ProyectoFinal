import cv2
import numpy as np

def generar_embedding(imagen_path):
    """Generar embedding usando LBPH (OpenCV)"""
    img = cv2.imread(imagen_path, cv2.IMREAD_GRAYSCALE)
    img = cv2.resize(img, (200, 200))
    
    # Calcular histograma LBP
    lbp = cv2.LBP_create()
    hist = lbp.compute(img)
    
    return hist.flatten()