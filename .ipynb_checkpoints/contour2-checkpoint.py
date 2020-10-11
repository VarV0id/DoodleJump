import numpy as np
import cv2

#Cargamos una fuente de texto
font = cv2.FONT_HERSHEY_SIMPLEX

#Definir kernel
kernel = cv2.getStructuringElement(cv2.MORPH_RECT,(12,12))
 
#Establecemos el rango mínimo y máximo de HSV:
low = np.array([21,18,72])
high = np.array([75, 74, 213]) 
#Recordamos al usuario con qué tecla se sale:
print("\nPulsa 'ESC' para salir\n")
  
#Iniciar la webcam:
webcam = cv2.VideoCapture(0)

while(1): 
  #Capturamos una imagen con la webcam:
  valido, img = webcam.read() 
  #Si la imagen se ha capturado correctamente, continuamos:
  if valido: 
    #Convertimos la imagen a hsv:
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV) 
    #Detectamos los píxeles que estén dentro del rango que hemos establecido:    
    mask = cv2.inRange(hsv, low, high)
 
    #Eliminamos el ruido con un CLOSE seguido de un OPEN:
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
 
    #Mostramos la imagen original y la máscara:
    cv2.imshow("Webcam", img)
    cv2.imshow("Mask", mask)

    #Buscamos los contornos de las bolas y los dibujamos en verde
    contours,_ = cv2.findContours(mask, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
    cv2.drawContours(img, contours, -1, (0,255,0), 2)
    cv2.imshow("aux",img)    
    #Buscamos el centro de las bolas y lo pintamos en rojo
    for i in contours:
        #Calcular el centro a partir de los momentos
        M = cv2.moments(i)
        cx = int(M['m10']/M['m00'])
        cy = int(M['m01']/M['m00'])
    
        #Dibujar el centro
        cv2.circle(img,(cx, cy), 3, (0,0,255), -1)
    
        #Escribimos las coordenadas del centro
        cv2.putText(img,"(x: " + str(cx) + ", y: " + str(cy) + ")/ area:"+ str(cv2.contourArea(i)),(cx+10,cy+10), font, 0.3,(255,255,255),1)
    
    #Mostramos la imagen final
    cv2.imshow('Final', img)
 
    #Salir con 'ESC':
    k = cv2.waitKey(5) & 0xFF
    if k == 27:
      cv2.destroyAllWindows()
      break