import cv2
import mediapipe as mp

# Testa câmeras disponíveis
camera_index = None
for i in range(5):
    cap_test = cv2.VideoCapture(i)
    if cap_test.isOpened():
        print(f"Câmera encontrada no índice {i}")
        camera_index = i
        cap_test.release()
        break

if camera_index is None:
    print("Nenhuma câmera encontrada.")
    exit()

# Inicializa Mediapipe
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(max_num_hands=1, min_detection_confidence=0.7)
mp_drawing = mp.solutions.drawing_utils

def detect_fingers(hand_landmarks):
    finger_tips = [8, 12, 16, 20]
    thumb_tip = 4
    finger_states = [0, 0, 0, 0, 0]
    if hand_landmarks.landmark[thumb_tip].x < hand_landmarks.landmark[thumb_tip - 1].x:
        finger_states[0] = 1
    for idx, tip in enumerate(finger_tips):
        if hand_landmarks.landmark[tip].y < hand_landmarks.landmark[tip - 2].y:
            finger_states[idx + 1] = 1
    return finger_states

# Abre a câmera detectada
cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

while cap.isOpened():
    success, image = cap.read()
    if not success:
        print("Erro: frame vazio")
        continue

    image_rgb = cv2.cvtColor(cv2.flip(image, 1), cv2.COLOR_BGR2RGB)
    results = hands.process(image_rgb)
    image_bgr = cv2.cvtColor(image_rgb, cv2.COLOR_RGB2BGR)

    if results.multi_hand_landmarks:
        for hand_landmarks in results.multi_hand_landmarks:
            mp_drawing.draw_landmarks(image_bgr, hand_landmarks, mp_hands.HAND_CONNECTIONS)
            fingers_state = detect_fingers(hand_landmarks)
            num_fingers = sum(fingers_state)
            cv2.putText(image_bgr, f'Quantidade de dedos: {num_fingers}', (30, 100),
                        cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0, 255, 0), 3)
            print(f"Quantidade de dedos: {num_fingers}")

    cv2.imshow('Hand Tracking', image_bgr)
    if cv2.waitKey(5) & 0xFF == 27:
        break

cap.release()
cv2.destroyAllWindows()
