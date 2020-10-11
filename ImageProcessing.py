#--------------------------------------------------------------------------
#------- PLANTILLA DE CÓDIGO ----------------------------------------------
#------- Coceptos básicos de PDI-------------------------------------------
#------- Por: Jairo David Campaña Rosero   jairo.campana@udea.edu.co ------
#-------      CC 1010060870 -----------------------------------------------
#-------      Santiago Escobar Casas       santiago.escobar8@udea.edu.co --
#-------      CC 1214746431 -----------------------------------------------
#-------      Estudiantes de ingenieria de sistemas UdeA  -----------------
#------- Curso Procesamiento digital de Imágenes --------------------------
#------- Octubre 2020 -----------------------------------------------------
#--------------------------------------------------------------------------

#--------------------------------------------------------------------------
#--1. Importacion de librerias --------------------------------------------
#--------------------------------------------------------------------------
import numpy as np
import cv2

#--------------------------------------------------------------------------
#--2. Inicializacion del procesador de imagenes----------------------------
#--------------------------------------------------------------------------
class ImageProcessing:
    def __init__(self):        
        # Se configura la camara ------------------------------------------
        self.vid = cv2.VideoCapture(0)

        # Se configura la fuente de escritura y el grosor de las lineas ---
        self.font = cv2.FONT_HERSHEY_SIMPLEX
        self.line_thickness = 2

        # Es la variable que permite configurar el area optima del juego --
        self.beginGame = False
#--------------------------------------------------------------------------
#--3. Se obtiene la mascara de la mano con el guante-----------------------
#--------------------------------------------------------------------------
    def getMask(self, frame):
        # Define los limites del matiz, saturacion y brillo en los canales de hsv
        lowChannels = np.array([22, 132, 86]) 
        maxChannels = np.array([29, 255, 255])

        # Se define un kernel cuadrado de 20x20, que fue obtenido experimentalmente, 
        # para realizar el proceso morfologico de cierre realizado con el fin de 
        # corregir las imperfecciones en la creacion de la mascara
        kernel = np.ones((20,20),np.uint8)

        #Se convierte la imagen en formato HSV ----------------------------
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

        #Crea la mascura y realiza el proceso morfologico de cierre. ------
        mask = cv2.inRange(hsv, lowChannels, maxChannels)
        mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)

        return mask
#--------------------------------------------------------------------------
#--4. Se obtiene el centroide de la mano y el area circular ---------------
#--------------------------------------------------------------------------
    def getCentroidsAndArea(self,mask):
        # Se encuentran los contornos de las figuras detectadas por la mascara
        contours,_ = cv2.findContours(mask, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
        
        # Variables usadas para encontrar los valores del objeto con mayor area
        maxCenter = 0
        maxRadius = 0
        maxArea = 0
        maxCountour = 0

        # Se itera sobre los contornos para encontrar el que tenga mayor area
        for i in contours:
            area, radius, center = self.getArea(i)
            if(area > maxArea):
                maxArea = area
                maxCountour = i
                maxRadius = radius
                maxCenter = center

        # Se encuentran los momentos del contorno mas grande para obtener el centroide
        M = cv2.moments(maxCountour)

        #Se controla el problema en el cual el momento M['m00'] sea cero
        try:
            cx = int(M['m10']/M['m00'])
            cy = int(M['m01']/M['m00'])
        except ZeroDivisionError:
            cx = 0 
            cy = -150
        
        # Se devuelve los puntos del centroide, area, radio y el centro de
        # del objeto de mayor area, que en este caso es la mano
        return cx, cy, maxArea, maxRadius, maxCenter

#--------------------------------------------------------------------------
#--5. Se obtiene un area circular que encierra el contorno ----------------
#--------------------------------------------------------------------------           
    def getArea(self, contour):

        # Se obtiene el centro del circulo y el radio del circulo
        (x,y),radius = cv2.minEnclosingCircle(contour)
        center = (int(x),int(y))
        radius = int(radius)
        # Se calcula el area circular con los parametros
        area_c = 3.14*radius**2

        # Se devuelve el area circular, el radio y el centro del contorno.
        return area_c, radius, center

#--------------------------------------------------------------------------
#--6. Se envia instrucciones al programa para determinar la accion a ------
#--realizar dependiendo del sector de la pantalla en donde se encuentre---- 
#--el centroide. Siendo 1 ir a la izquierda, 2 ir a la derecha, 3 saltar---
#--y 4 no hacer nada. 
#-------------------------------------------------------------------------- 
    def simulateKey(self, frame, cx, cy, ca):
        #Se verifica que el area circular sea superior a 30000 para--------
        #realizar la accion de salto---------------------------------------
        if(ca > 30000):
            return 3
        
        # Se detecta que el centroide este en la mitad inferior de la------
        # pantalla 
        if(cy > frame.shape[0]/2):

            # Si el centroide esta en la seccion izquierda o derecha de la-
            # pantalla se realiza la accion de movimiento a los lados -----
            if(cx < frame.shape[1]/2):
                return 1

            else:
                return 2
        return 4

#--------------------------------------------------------------------------
#--7. Se inicializa el procedimiento para obtener y procesar --------------
#-- Cada fotograma de la camara. ------------------------------------------
#--------------------------------------------------------------------------            
    def procesarImagen(self):
        # Se lee el frame y se invierte la imagen para la facilitar la 
        # interactividad con el juego -------------------------------------
        ret, frame = self.vid.read() 
        frame = cv2.flip(frame, 1)

        # Se obtiene la mascara para detectar la mano----------------------
        mask = self.getMask(frame)

        # Se hace un bitwise con la mascara para obtener el objeto---------
        result = cv2.bitwise_and(frame,frame, mask = mask)
        
        # Se obtienen los centroides y el area de la mascara---------------
        cx, cy, ca, radius, center = self.getCentroidsAndArea(mask)

        # Se verifica si ya fue realizado el proceso de calibracion -------
        if(not self.beginGame):
            # Se dibuja el circulo de calibracion del juego----------------
            frame = cv2.circle(frame,(cx, cy), 75, (0,0,255), -1)
            cv2.putText(frame,"Calibre su",(cx-40,cy-20), self.font, 0.5,(0,0,0),2)
            cv2.putText(frame,"mano aqui.",(cx-40,cy), self.font, 0.5,(0,0,0),2)
            cv2.putText(frame,"Mantengala",(cx-40,cy+20), self.font, 0.5,(0,0,0),2)
            cv2.putText(frame,"cerrada",(cx-40,cy+40), self.font, 0.5,(0,0,0),2)
            
            # Si la mano tiene un area entre 15000 y 20000 el juego inicia--
            if(ca > 15000 and ca < 20000):
                    self.beginGame = True
        else:
            # Crea dos circulos de calibracion en la pantalla---------------
            cv2.putText(frame,"Abra para saltar",(cx,cy-87), self.font, 0.5,(0,0,0),2)
            frame = cv2.circle(frame,(cx, cy), 80, (0,0,255), 3)
            frame = cv2.circle(frame,(cx, cy), 69, (0,0,255), 3)

        # Crea un punto en el centroide  y crea los mensajes de apoyo-------
        # para poder jugar--------------------------------------------------
        frame = cv2.circle(frame,(cx, cy), 3, (0,0,255), -1)
        cv2.putText(frame,"Descansar",(int(frame.shape[1]/2-50),30), self.font,1,(0,0,0),2)
        cv2.putText(frame,"Izquierda",(int(frame.shape[1]/3-100),int(frame.shape[0]/2)+30), self.font, 1,(0,0,0),2)
        cv2.putText(frame,"Derecha",(int(2*frame.shape[1]/3),int(frame.shape[0]/2)+30), self.font, 1,(0,0,0),2)
        cv2.line(frame, (0, int(frame.shape[0]/2)), (frame.shape[1], int(frame.shape[0]/2)), (0, 255, 0), thickness=self.line_thickness)
        cv2.line(frame, (int(frame.shape[1]/2), int(frame.shape[0]/2)), (int(frame.shape[1]/2), frame.shape[0]), (0, 255, 0), thickness=self.line_thickness)
        if(center != 0):
            frame = cv2.circle(frame,(cx,cy),radius,(0,255,0),2)
        # Muestra el mensaje de saltando si el area circular es superior a--
        # 30000-------------------------------------------------------------
        if(ca > 30000):
            cv2.putText(frame,"Saltando",(cx,cy+radius+20), self.font, 0.5,(0,0,0),2)
        
        # Imprime los resultados del frame y entorno grafico para la seccion
        # de procesamiento de imagenes del juego----------------------------
        cv2.imshow('Original',frame)
        cv2.imshow('result',result)
        return self.simulateKey(frame, cx, cy,ca)   


#--------------------------------------------------------------------------
#---------------- FIN DEL MODULO DEL PROCESAMIENTO DE IMAGENES ------------
#--------------------------------------------------------------------------