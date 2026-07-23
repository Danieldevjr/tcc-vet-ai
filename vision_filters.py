import cv2
import numpy as np
from PIL import Image, ImageFilter

def medir_nitidez(image_pil):
    """Calcula a Variância do Laplaciano para medir o foco da imagem."""
    img_cv = cv2.cvtColor(np.array(image_pil.convert('RGB')), cv2.COLOR_RGB2GRAY)
    return cv2.Laplacian(img_cv, cv2.CV_64F).var()

def verificar_dominio_biologico(image_pil):
    """Usa espaço HSV para detectar cores externas (Verde/Azul)."""
    img_np = np.array(image_pil.convert('RGB'))
    hsv = cv2.cvtColor(img_np, cv2.COLOR_RGB2HSV)
    
    lower_green, upper_green = np.array([35, 40, 40]), np.array([85, 255, 255])
    lower_blue, upper_blue = np.array([90, 40, 40]), np.array([130, 255, 255])
    
    mask_green = cv2.inRange(hsv, lower_green, upper_green)
    mask_blue = cv2.inRange(hsv, lower_blue, upper_blue)
    
    total_pixels = img_np.shape[0] * img_np.shape[1]
    pixels_incomuns = cv2.countNonZero(mask_green) + cv2.countNonZero(mask_blue)
    return (pixels_incomuns / total_pixels) * 100

# =====================================================================
# NOVA TÉCNICA: REALCE DE INTEGRIDADE CLÍNICA (PDI)
# =====================================================================
def aplicar_realce_pdi_avancado(image_pil):
    """
    Aplica CLAHE adaptativo apenas na Luminância (Canal L) 
    para destacar bordas e contornos biológicos apagados pelo desfoque.
    """
    # Converte PIL para OpenCV
    img_np = np.array(image_pil.convert('RGB'))
    img_cv = cv2.cvtColor(img_np, cv2.COLOR_RGB2BGR)

    # Separa a iluminação das cores (Espaço LAB)
    lab = cv2.cvtColor(img_cv, cv2.COLOR_BGR2LAB)
    l, a, b = cv2.split(lab)

    # Aplica o equalizador adaptativo de contraste apenas no brilho/textura
    clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8))
    cl = clahe.apply(l)

    # Remonta a imagem e transforma de volta para o padrão RGB da IA
    limg = cv2.merge((cl, a, b))
    enhanced_cv = cv2.cvtColor(limg, cv2.COLOR_LAB2BGR)
    img_final_rgb = cv2.cvtColor(enhanced_cv, cv2.COLOR_BGR2RGB)
    
    return Image.fromarray(img_final_rgb)