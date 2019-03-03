# -*- coding: utf-8 -*-
#usr/bin/python

import os
import copy
import cv2
import serial
import numpy as np

# constantes
ID_PORTA = "COM8" # numero porta COM do arduino.
ID_CAMERA = 0 #-1 qualquer camera
QUANT_COLUNAS = 640
QUANT_LINHAS = 480
QUANT_LIMIAR_PIXELS = 100
QUANT_FAIXAS_CORES = 3

# variaveis
cor_detectada = "branco" # "azul", "vermelho", "amarelo"

cores          = {QUANT_FAIXAS_CORES - 3: "azul",
                  QUANT_FAIXAS_CORES - 2: "vermelho",
                  QUANT_FAIXAS_CORES - 1: "verde"} 
faixa_azul     = {'menor': np.array([99, 115, 150]), 'maior': np.array([110, 255,  255])} # ok
faixa_vermelho = {'menor': np.array([136, 87, 111]), 'maior':  np.array([180, 255, 255])} # ok
faixa_verde  = {'menor': np.array([65,  100,  50]), 'maior': np.array([100,   255, 255])}   # testar

faixa          = {QUANT_FAIXAS_CORES - 3: faixa_azul, 
                  QUANT_FAIXAS_CORES - 2: faixa_vermelho, 
                  QUANT_FAIXAS_CORES - 1: faixa_verde}

roi = {'inicial': (QUANT_COLUNAS/4, QUANT_LINHAS/4),
       'final':  (QUANT_COLUNAS/2, QUANT_LINHAS/2)}  

camera = cv2.VideoCapture(ID_CAMERA)

def captura_imagem_camera(fonte):
    # Captura imagem da webcam
    return fonte.read()


def desenha_roi(fonte):
    # Desenha o quadrado que ira avaliar a cor que estiver nele.    
    cv2.rectangle(fonte, roi['inicial'], roi['final'], (0,255,0), 3)
    return fonte

def busca_cor_imagem(fonte):
	# Realiza a busca da cor, baseado na faixa de cores da função que a chama.
	contagem = 0	
	for i in range (roi['inicial'][1], roi['final'][1]):
		for j in range (roi['inicial'][0], roi['final'][0]):
			if(fonte[i, j] == 255):				
				contagem = contagem + 1	
	if (contagem > QUANT_LIMIAR_PIXELS):		
		return True
	else:
		return False

def detecta_cores(fonte):
    # Detecta as cores da imagem fonte.    
    fonte = cv2.cvtColor(fonte, cv2.COLOR_BGR2HSV)

    for i in range(QUANT_FAIXAS_CORES):
    	img = cv2.inRange(fonte, faixa[i]['menor'], faixa[i]['maior'])
    	cv2.imshow("t", img)
        if(busca_cor_imagem(img)):
        	return cores[i]
        	break;

def abre_serial():
	try:
		canal = serial.Serial(ID_PORTA)
		return canal
	except:
		print "Erro ao abrir porta serial, verificar numero da porta."
	

def envia_comando(canal, cor):	
	comando = None
	if(cor == cores[0]):
		# azul
		comando = '0'
	elif(cor == cores[1]):
		# vermelho
		comando = '1'
	elif(cor == cores[2]):
		# verde
		comando = '2'
	try:
		if(comando != None and canal.isOpen()):
			print comando
			canal.write(comando)
	except:
		print "Erro na porta de comunicacao"
	
# --------------------------------------- EXECUCAO ---------------------------------
canal = abre_serial()
while(True):
	# processamento da imagem
    _, imagem = captura_imagem_camera(camera)
    cv2.blur(imagem, (5,5))
    desenha_roi(copy.copy(imagem))    
    cor_detectada = detecta_cores(copy.copy(imagem))

    # comunicação serial    
    envia_comando(canal, cor_detectada)

    # exibição da imagem
    cv2.imshow("Imagem com ROI", desenha_roi(copy.copy(imagem)))    
    cv2.waitKey(30)
    print cor_detectada    
    
cv2.destroyAllWindows()
canal.close()