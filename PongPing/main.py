import cv2
import cvzone
from cvzone.HandTrackingModule import HandDetector
import numpy as np
cap = cv2.VideoCapture(0)
cap.set(3, 1280)
cap.set(4, 720)

imgStart = cv2.imread("Resources/start.png")
imgEnd = cv2.imread("Resources/khatm.png")
imgBall = cv2.imread("Resources/ball.png", cv2.IMREAD_UNCHANGED)
imgSlider1 = cv2.imread("Resources/bat1.png", cv2.IMREAD_UNCHANGED)
imgSlider2 = cv2.imread("Resources/bat2.png", cv2.IMREAD_UNCHANGED)

detector = HandDetector(detectionCon=0.8, maxHands=2)

ballPos = [100, 100]
speedX = 10
speedY = 10

score = [0, 0]

gameOver = False

while True:
    _, img = cap.read()
    img = cv2.flip(img, 1)
    hands, img = detector.findHands(img, flipType=False)

    img = cv2.addWeighted(img, 0.1, imgStart, 0.8, 0)

    if hands:
        for hand in hands:
            x, y, w, h = hand['bbox']

            w1 = 26
            h1 = 129

            y1 = y - h1//2
            y1 = np.clip(y1, 25, 436)
            if hand['type'] == "Left":
                img = cvzone.overlayPNG(img, imgSlider1, (78, y1))
                if 78 < ballPos[0] < 78 + w1 and y1 < ballPos[1] < y1+h1:
                    speedX = -speedX
                    ballPos[0] = ballPos[0] + 30
                    score[0] = score[0] + 1

            if hand['type'] == "Right":
                img = cvzone.overlayPNG(img, imgSlider2, (1178, y1))
                if 1178-50 < ballPos[0] < 1178-30 and y1 < ballPos[1] < y1+h1:
                    speedX = -speedX
                    ballPos[0] = ballPos[0] - 30
                    score[1] = score[1] + 1

    if ballPos[0] < 70 or ballPos[0] > 1190:
        gameOver = True
    if gameOver:
        img = imgEnd
        cv2.putText(img, str(score[0]+score[1]).zfill(2), (580, 385), cv2.FONT_HERSHEY_SIMPLEX, 3, (0, 0, 180), 5)

    else:
        if ballPos[1] >= 511 or ballPos[1] <= 29:
            speedY = -speedY

        ballPos[0] = ballPos[0] + speedX
        ballPos[1] = ballPos[1] + speedY

        img = cvzone.overlayPNG(img, imgBall, ballPos)

        cv2.putText(img, str(score[0]), [280, 650], cv2.FONT_HERSHEY_SIMPLEX, 3, (255, 255, 255), 5)
        cv2.putText(img, str(score[1]), [920, 650], cv2.FONT_HERSHEY_SIMPLEX, 3, (255, 255, 255), 5)

    cv2.imshow("Image", img)

    key = cv2.waitKey(1)
    if key == ord('r'):
        ballPos = [100, 100]
        speedX = 10
        speedY = 10
        score = [0, 0]
        gameOver = False


