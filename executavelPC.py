# Executável para PC, utilizando a biblioteca OpenCV para processamento de imagens.
# juntamente de uma webcam, o código captura vídeo da câmera, 
# processa a imagem para detectar linhas e calcula um erro baseado na posição da linha detectada em relação ao centro da imagem.

import cv2
import numpy as np
import time

erro = 0

cap = cv2.VideoCapture(0)

centro = 135
altura = 140
largura = 270

divisao_altura = int(largura/5)

esqP_val = 0
esq_val  = 0
centro_val = 0
dir_val  = 0
dirP_val = 0


def separacao_colunas():

    esqP = thresh[:, 0:divisao_altura]
    esq  = thresh[:, divisao_altura:divisao_altura*2]
    centro = thresh[:, divisao_altura*2:divisao_altura*3]
    dir  = thresh[:, divisao_altura*3:divisao_altura*4]
    dirP = thresh[:, divisao_altura*4:largura]

    cv2.line(im, (divisao_altura, 0), (divisao_altura, altura), (255,0,0), 1)
    cv2.line(im, (divisao_altura*2, 0), (divisao_altura*2, altura), (255,0,0), 1)
    cv2.line(im, (divisao_altura*3, 0), (divisao_altura*3, altura), (255,0,0), 1)
    cv2.line(im, (divisao_altura*4, 0), (divisao_altura*4, altura), (255,0,0), 1)

    esqP_val = np.sum(esqP == 255)
    esq_val  = np.sum(esq == 255)
    centro_val = np.sum(centro == 255)
    dir_val  = np.sum(dir == 255)
    dirP_val = np.sum(dirP == 255)

    return esqP_val, esq_val, centro_val, dir_val, dirP_val

    

while True:

    ret, im = cap.read()

    if not ret:
        print("Erro ao capturar imagem")
        break

    # Redimensiona para igual ao Raspberry
    im = cv2.resize(im, (largura, altura))

    # Cortar parte inferior
    # im = im[60:120, 0:240]

    gray = cv2.cvtColor(im, cv2.COLOR_BGR2GRAY)

    gray = cv2.GaussianBlur(gray, (5,5), 0)

    _, thresh = cv2.threshold(
        gray,
        70,
        255,
        cv2.THRESH_BINARY_INV
    )

    contours, _ = cv2.findContours(
        thresh,
        cv2.RETR_EXTERNAL,
        cv2.CHAIN_APPROX_SIMPLE
    )

    esqP_val, esq_val, centro_val, dir_val, dirP_val = separacao_colunas()

    if contours:

        c = max(contours, key=cv2.contourArea)

        if cv2.contourArea(c) > 200:

            M = cv2.moments(c)

            if M["m00"] != 0:

                cx = int(M["m10"] / M["m00"])

                soma = esqP_val + esq_val + centro_val + dir_val + dirP_val
                erro = ((esqP_val*2)+esq_val)-((dirP_val*2)+dir_val)
                if soma > 0:
                    erro = erro/soma

                cv2.circle(im, (cx, 30), 5, (0,255,0), -1)

    

    print((erro*100))

    cv2.imshow("Camera", im)
    cv2.imshow("Thresh", thresh)

    if cv2.waitKey(1) == 27:
        break

cap.release()
cv2.destroyAllWindows()