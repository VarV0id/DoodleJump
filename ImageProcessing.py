#--------------------------------------------------------------------------
#------- PLANTILLA DE CÓDIGO ----------------------------------------------
#------- Coceptos básicos de PDI-------------------------------------------
#------- Por: Jairo David Campaña Rosero   jairo.campana@udea.edu.co ------
#-------      CC 1010060870 -----------------------------------------------
#-------      Santiago Escobar Casas       santiago.escobar8@udea.edu.co --
#-------      CC 1214746431 -----------------------------------------------
#-------      Estudiantes de ingenieria de sistemas UdeA  -----------------
#------- Curso Básico de Procesamiento de Imágenes y Visión Artificial-----
#------- V2 Abril de 2015--------------------------------------------------
#--------------------------------------------------------------------------
#--------------------------------------------------------------------------
#--1. Importacion de librerias --------------------------------------------
#--------------------------------------------------------------------------
import numpy as np
import cv2
class ImageProcessing:
#--------------------------------------------------------------------------
#--2. Inicializacion del procesador de imagenes----------------------------
#--------------------------------------------------------------------------

    def __init__(self):
        self.vid = cv2.VideoCapture(0)
        self.font = cv2.FONT_HERSHEY_SIMPLEX
        self.line_thickness = 2
        self.beginGame = False
#--------------------------------------------------------------------------
#--3. Se obtiene la mascara de la mano con el guante-----------------------
#--------------------------------------------------------------------------
    def getMask(self, frame):
        # Define los limites de matiz, saturacion y brillo en los canales de hsv
        lowChannels = np.array([22, 132, 86]) 
        maxChannels = np.array([29, 255, 255])

        # Se define un kernel cuadrado de 20x20, que fue obtenido experimentalmente, 
        # para realizar el proceso morfologico de cierre realizado con el fin de 
        # corregir las imperfecciones en la creacion de la mascara
        kernel = np.ones((20,20),np.uint8)

        #Se convierte la imagen en formato HSV
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

        #Crea la mascura y realiza el proceso morfologico de cierre.
        mask = cv2.inRange(hsv, lowChannels, maxChannels)
        mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)

        return mask
#--------------------------------------------------------------------------
#--4. Se obtiene el centroide de la mano y el area circular ---------------
#--------------------------------------------------------------------------
    def getCentroidsAndArea(self,mask):
        contours,_ = cv2.findContours(mask, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
        maxCenter = 0
        maxRadius = 0
        maxArea = 0
        maxCountour = 0
        for i in contours:
            #Calcular el centro a partir de los momentos
            area, radius, center = self.getArea(i)
            if(area > maxArea):
                maxArea = area
                maxCountour = i
                maxRadius = radius
                maxCenter = center
        M = cv2.moments(maxCountour)

        try:
            cx = int(M['m10']/M['m00'])
            cy = int(M['m01']/M['m00'])
        except ZeroDivisionError:
            cx = 0 
            cy = -150
        return cx, cy, maxArea, maxRadius, maxCenter
            
    def getArea(self, contour):
        (x,y),radius = cv2.minEnclosingCircle(contour)
        center = (int(x),int(y))
        radius = int(radius)
            #img = cv2.circle(img,center,radius,(0,255,0),2)
        area_c = 3.14*radius**2
        return area_c, radius, center

    def simulateKey(self, frame, cx, cy, ca):
        if(ca > 30000):
            return 3
        if(cy > frame.shape[0]/2):
            if(cx < frame.shape[1]/2):
                return 1

            else:
                return 2
        return 4
           
    def procesarImagen(self):
        ret, frame = self.vid.read() 
        frame = cv2.flip(frame, 1)
        mask = self.getMask(frame)
        result = cv2.bitwise_and(frame,frame, mask = mask)
        cx, cy, ca, radius, center = self.getCentroidsAndArea(mask)
        if(not self.beginGame):
            frame = cv2.circle(frame,(cx, cy), 75, (0,0,255), -1)
            cv2.putText(frame,"Calibre",(cx-20,cy), self.font, 0.5,(0,0,0),2)
            cv2.putText(frame,"su mano aqui",(cx-60,cy+20), self.font, 0.5,(0,0,0),2)
            if(ca > 15000 and ca < 20000):
                    self.beginGame = True
        else:
            cv2.putText(frame,"Abra para saltar",(cx,cy-87), self.font, 0.5,(0,0,0),2)
            frame = cv2.circle(frame,(cx, cy), 80, (0,0,255), 3)
            frame = cv2.circle(frame,(cx, cy), 69, (0,0,255), 3)
        frame = cv2.circle(frame,(cx, cy), 3, (0,0,255), -1)
        cv2.putText(frame,"Descansar",(int(frame.shape[1]/2-50),30), self.font,1,(0,0,0),2)
        cv2.putText(frame,"Izquierda",(int(frame.shape[1]/3-100),int(frame.shape[0]/2)+30), self.font, 1,(0,0,0),2)
        cv2.putText(frame,"Derecha",(int(2*frame.shape[1]/3),int(frame.shape[0]/2)+30), self.font, 1,(0,0,0),2)
        cv2.line(frame, (0, int(frame.shape[0]/2)), (frame.shape[1], int(frame.shape[0]/2)), (0, 255, 0), thickness=self.line_thickness)
        cv2.line(frame, (int(frame.shape[1]/2), int(frame.shape[0]/2)), (int(frame.shape[1]/2), frame.shape[0]), (0, 255, 0), thickness=self.line_thickness)
        if(center != 0):
            frame = cv2.circle(frame,(cx,cy),radius,(0,255,0),2)
            #cv2.putText(frame," area:"+ str(ca),(cx+10,cy+10), self.font, 0.7,(0,0,0),1)
        if(ca > 30000):
            cv2.putText(frame,"Saltando",(cx,cy+radius+20), self.font, 0.5,(0,0,0),2)
        #Mostramos los resultados y salimos:
        cv2.imshow('Original',frame)
        cv2.imshow('mask',mask)
        return self.simulateKey(frame, cx, cy,ca)   

            