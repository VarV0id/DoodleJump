"""
EJEMPLO 6 (bis) - Webcam
 
Este código detecta colores en un vídeo en tiempo real. Los parámetros
pueden ajustarse mediante sliders.
 
Escrito por Glare y Transductor
www.robologs.net
"""
import cv2
import numpy as np
 
#Iniciar la webcam:
webcam = cv2.VideoCapture(0)
#Nota: si no funciona, puedes cambiar el 0 por 1 o por la dirección de tu webcam (ej. "/dev/video0")
 
 
#Función auxiliar:
def nothing(x):
   pass
 
 
#Creamos la ventana con los sliders:
cv2.namedWindow('Parametros')
cv2.createTrackbar('Hue Minimo','Parametros',0,179,nothing)
cv2.createTrackbar('Hue Maximo','Parametros',0,179,nothing)
cv2.createTrackbar('Saturation Minimo','Parametros',0,255,nothing)
cv2.createTrackbar('Saturation Maximo','Parametros',0,255,nothing)
cv2.createTrackbar('Value Minimo','Parametros',0,255,nothing)
cv2.createTrackbar('Value Maximo','Parametros',0,255,nothing)
cv2.createTrackbar('Kernel X', 'Parametros', 1, 30, nothing)
cv2.createTrackbar('Kernel Y', 'Parametros', 1, 30, nothing)
 
 
#Recordamos al usuario con qué tecla se cierra:
print("\nPulsa 'ESC' para salir\n")
 
 
while(1):
 
  #Capturamos una imagen con la webcam:
  valido, img = webcam.read()
 
  #Si la imagen se ha capturado correctamente, continuamos:
  if valido:
 
    #Convertimos la imagen a hsv:
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
 
    #Leemos los sliders y guardamos los valores de H,S,V para construir los rangos:
    hMin = cv2.getTrackbarPos('Hue Minimo','Parametros')
    hMax = cv2.getTrackbarPos('Hue Maximo','Parametros')
    sMin = cv2.getTrackbarPos('Saturation Minimo','Parametros')
    sMax = cv2.getTrackbarPos('Saturation Maximo','Parametros')
    vMin = cv2.getTrackbarPos('Value Minimo','Parametros')
    vMax = cv2.getTrackbarPos('Value Maximo','Parametros')
 
    #Establecemos el rango mínimo y máximo de HSV:
    color_bajos = np.array([hMin, sMin, vMin])
    color_altos = np.array([hMax, sMax, vMax])
 
    #Detectamos los píxeles que estén dentro del rango que hemos establecido:
    mask = cv2.inRange(hsv, color_bajos, color_altos)
 
    #Leemos los sliders que definen las dimensiones del Kernel:
    kernelx = cv2.getTrackbarPos('Kernel X', 'Parametros')
    kernely = cv2.getTrackbarPos('Kernel Y', 'Parametros')
 
    #Creamos el kernel y eliminamos el ruido:
    kernel = np.ones((kernelx, kernely), np.uint8)
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)


    masked = cv2.bitwise_and(img,img, mask=mask)
 
    #Mostramos la imagen original y la máscara:
    cv2.imshow("Webcam", img)
    cv2.imshow("Mask", mask)
    cv2.imshow("Masked", masked)
 
    #Salimos si se pulsa 'ESC':
    k = cv2.waitKey(5) & 0xFF
    if k == 27:
      cv2.destroyAllWindows()
      break
 
webcam.release()