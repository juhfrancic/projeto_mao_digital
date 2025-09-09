import cv2
from cvzone.HandTrackingModule import HandDetector
import serial
import time

# Inicializa detector de mãos
detector = HandDetector(maxHands=1, detectionCon=0.8)
video = cv2.VideoCapture(1)

# Inicializa comunicação com Arduino
arduino = serial.Serial(port='COM3', baudrate=115200, timeout=1)
time.sleep(2)  # Espera Arduino resetar

def fingers_up_custom(hand):
    """
    Retorna lista [dedo1,...,dedo5] onde 1 = levantado, 0 = abaixado
    Funciona com palma ou dorso para câmera.
    Ordem: [polegar, indicador, médio, anelar, mínimo]
    """
    lmList = hand["lmList"]  # lista de 21 landmarks da mão
    tipo = hand["type"]      # "Left" ou "Right"

    dedos = []

    # ---- Polegar ----
    # Comparar eixo X porque o polegar aponta pro lado
    if tipo == "Left":
        if lmList[4][0] > lmList[3][0]:
            dedos.append(1)
        else:
            dedos.append(0)
    else:  # Rightcc
        if lmList[4][0] < lmList[3][0]:
            dedos.append(1)
        else:
            dedos.append(0)

    # ---- Outros dedos ----
    # Se a ponta (tip) estiver acima da junta do dedo, ele está levantado
    for tip in [8, 12, 16, 20]:  # indicador, médio, anelar, mínimo
        if lmList[tip][1] < lmList[tip - 2][1]:  # compara eixo Y
            dedos.append(1)
        else:
            dedos.append(0)

    return dedos

while True:
    _, img = video.read()
    img = cv2.flip(img, 1)

    hands, img = detector.findHands(img, draw=True)
    if hands:
        hand = hands[0]

        # Corrige inversão causada pelo flip
        if hand["type"] == "Left":
            hand["type"] = "Right"
        else:
            hand["type"] = "Left"

        # Dedos levantados (custom)
        fingerup = fingers_up_custom(hand)

        # Conta quantos dedos estão levantados
        num_fingers = sum(fingerup)

        # Envia para o Arduino
        arduino.write(f"{num_fingers}\n".encode())
        print(f"Número de dedos: {num_fingers}, Estado: {fingerup}")

        # Mostra número de dedos na tela
        cv2.putText(img, f'Dedos: {num_fingers}', (50, 100),
                    cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 255, 0), 3)

    cv2.imshow("Video", img)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break
    time.sleep(0.1)

video.release()
cv2.destroyAllWindows()