import mediapipe as mp
import cv2
import screen_brightness_control as sbc


mpHands = mp.solutions.hands
Hands = mpHands.Hands(static_image_mode=False,
                      max_num_hands=1,
                      min_detection_confidence=0.5,
                      min_tracking_confidence=0.5)
mpDraw = mp.solutions.drawing_utils

cap = cv2.VideoCapture(0)
pTime = 0


class handDetector():
    def __init__(self, mode=False, maxHands=2, complexity=1, detectionConfidence=0.5, trackConfidence=0.5):
        self.mode = mode
        self.maxHands = maxHands
        self.complexity = complexity
        self.detectionConfidence = detectionConfidence
        self.trackConfidence = trackConfidence
        self.mpHands = mp.solutions.hands
        self.hands = self.mpHands.Hands(self.mode, self.maxHands, self.complexity, self.detectionConfidence,
                                        self.trackConfidence)
        self.mpDraw = mp.solutions.drawing_utils

        self.tipIds = [4, 8, 12, 16, 18]

    def findHands(self, img, draw=True):
        imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        self.results = self.hands.process(imgRGB)

        if self.results.multi_hand_landmarks:
            for handLms in self.results.multi_hand_landmarks:
                if draw:
                    self.mpDraw.draw_landmarks(img, handLms, self.mpHands.HAND_CONNECTIONS)
        return img

    def findPosition(self, img, handNo=0, draw=True):
        self.lmList = []
        if self.results.multi_hand_landmarks:
            myHand = self.results.multi_hand_landmarks[handNo]

            for id, lm in enumerate(myHand.landmark):
                h, w, c = img.shape
                cx, cy = int(lm.x * w), int(lm.y * h)
                self.lmList.append([id, cx, cy])

                if draw:
                    cv2.circle(img, (cx, cy), 5, (255, 0, 255), cv2.FILLED)

        return self.lmList

    def fingersUp(self):
        fingers = []

        if self.lmList[self.tipIds[0]][1] > self.lmList[self.tipIds[0] - 1][1]:
            fingers.append(1)
        else:
            fingers.append(0)

        for id in range(1, 5):
            if self.lmList[self.tipIds[id]][2] < self.lmList[self.tipIds[id] - 2][2]:
                fingers.append(1)
            else:
                fingers.append(0)

        return fingers
detector = handDetector()
while True:


    T, frame = cap.read()
    imgRGB = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    hands = Hands.process(imgRGB)
    img = detector.findHands(frame)
    lmList = detector.findPosition(frame)
    cv2.putText(img=img, text='Left - Brightness Increase', org=(0, 200), fontFace=cv2.FONT_HERSHEY_TRIPLEX, fontScale=1,
                color=(0, 255, 100), thickness=1)
    cv2.putText(img=img, text='Right - Brightness Decrease', org=(0, 250), fontFace=cv2.FONT_HERSHEY_TRIPLEX,
                fontScale=1,
                color=(0, 0, 250), thickness=1)

    if hands.multi_hand_landmarks:
        for handLms in hands.multi_hand_landmarks:
            for id, lm in enumerate(handLms.landmark):
                h, w, c = frame.shape
                cx, cy = int(lm.x * w), int(lm.y * h)
                if id == 8:
                    cv2.circle(frame, (cx, cy), 3, (200, 255, 0), cv2.FILLED)


                    x = (cx * 100) / w
                    x = 100 - x
                    sbc.set_brightness(x)



    cv2.imshow("hand", frame)
    cv2.waitKey(1)