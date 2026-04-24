import cv2
import numpy as np
from picamera2 import Picamera2
import time
from libcamera import Transform
import RPi.GPIO as GPIO
import time

GPIO.setmode(GPIO.BCM)
GPIO.setup(18, GPIO.OUT)
GPIO.setup(14, GPIO.OUT)
GPIO.setup(15, GPIO.OUT)
GPIO.setup(5, GPIO.OUT)
GPIO.setup(6, GPIO.OUT)
GPIO.setup(13, GPIO.OUT)
pwmE = GPIO.PWM(18, 1000)  # pino 18, frequncia 1000Hz
pwmD = GPIO.PWM(13, 1000)

pwmE.start(0) 
pwmD.start(0) 

erroA = 0


picam2 = Picamera2()

config = picam2.create_video_configuration(
    main={"format": "RGB888","size":(240, 120)},
    transform=Transform(0)
)

picam2.configure(config)
picam2.start()

tStart = time.time()

centro = 120  # metade da largura (240)

def motorE(vel):
    
    if vel > 0:
        
        GPIO.output(14, GPIO.LOW)
        GPIO.output(15, GPIO.HIGH)
        pwmE.ChangeDutyCycle(max(min(vel, 100), 0))
    
    else:
        
        vel = (vel+1)*-1
        GPIO.output(14, GPIO.HIGH)
        GPIO.output(15, GPIO.LOW)
        pwmE.ChangeDutyCycle(max(min(vel, 100), 0))
        
def motorD(vel):
    
    if vel > 0:
        
        GPIO.output(5, GPIO.HIGH)
        GPIO.output(6, GPIO.LOW)
        pwmD.ChangeDutyCycle(max(min(vel, 100), 0))
    
    else:
        
        vel = (vel+1)*-1
        GPIO.output(5, GPIO.LOW)
        GPIO.output(6, GPIO.HIGH)
        pwmD.ChangeDutyCycle(max(min(vel, 100), 0))

def segueLinha():
    
    kp = 1.5
    kd = 5
    velocidade = 100
    derivada = (erro - erroA) *kd
    proporcional = erro*kp
    
    velE = velocidade+(proporcional+derivada)
    velD = velocidade-(proporcional+derivada)
    
    motorE(velE)
    motorD(velD)
    
    erro = erroA

while True:

    im = picam2.capture_array()

    # Converter para escala de cinza
    gray = cv2.cvtColor(im, cv2.COLOR_BGR2GRAY)

    gray = cv2.GaussianBlur(gray, (5,5), 0)

    # Threshold (linha preta vira branca)
    _, thresh = cv2.threshold(
        gray,
        100,
        255,
        cv2.THRESH_BINARY_INV
    )

    # Detectar contornos
    contours, _ = cv2.findContours(
        thresh,
        cv2.RETR_EXTERNAL,
        cv2.CHAIN_APPROX_SIMPLE
    )

    if contours:

        # Maior contorno = linha
        c = max(contours, key=cv2.contourArea)

        M = cv2.moments(c)

        if M["m00"] != 0:

            cx = int(M["m10"] / M["m00"])
            cy = int(M["m01"] / M["m00"])

            # Desenhar centro
            cv2.circle(im, (cx, cy), 5, (0,255,0), -1)

            # Calcular erro
            erro = cx - centro

            print("Erro:", erro)

    cv2.imshow("Camera", im)
    cv2.imshow("Thresh", thresh)
    
    segueLinha()
    

    if cv2.waitKey(1) == 27:
        break

picam2.stop()
cv2.destroyAllWindows()
