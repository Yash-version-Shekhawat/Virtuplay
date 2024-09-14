import tkinter as tk
from PIL import Image, ImageTk
import cv2
import cvzone
from cvzone.HandTrackingModule import HandDetector
import numpy as np

def play_game_1():

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

                y1 = y - h1 // 2
                y1 = np.clip(y1, 25, 436)
                if hand['type'] == "Left":
                    img = cvzone.overlayPNG(img, imgSlider1, (78, y1))
                    if 78 < ballPos[0] < 78 + w1 and y1 < ballPos[1] < y1 + h1:
                        speedX = -speedX
                        ballPos[0] = ballPos[0] + 30
                        score[0] = score[0] + 1

                if hand['type'] == "Right":
                    img = cvzone.overlayPNG(img, imgSlider2, (1178, y1))
                    if 1178 - 50 < ballPos[0] < 1178 - 30 and y1 < ballPos[1] < y1 + h1:
                        speedX = -speedX
                        ballPos[0] = ballPos[0] - 30
                        score[1] = score[1] + 1

        if ballPos[0] < 70 or ballPos[0] > 1190:
            gameOver = True
        if gameOver:
            img = imgEnd
            cv2.putText(img, str(score[0] + score[1]).zfill(2), (580, 385), cv2.FONT_HERSHEY_SIMPLEX, 3, (0, 0, 180), 5)

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

    print("Launching Ping-Pong")

def play_game_2():

    import math
    import random
    import cvzone
    import cv2
    import numpy as np
    from cvzone.HandTrackingModule import HandDetector
    cap = cv2.VideoCapture(0)
    cap.set(3, 1280)
    cap.set(4, 720)

    detector = HandDetector(detectionCon=0.8, maxHands=1)

    class SnakeGameClass:
        def __init__(self, pathFood):
            self.points = []
            self.lengths = []
            self.currentLength = 0
            self.allowedLength = 200
            self.previousHead = 0, 0

            self.imgFood = cv2.imread(pathFood, cv2.IMREAD_UNCHANGED)
            self.hFood, self.wFood, _ = self.imgFood.shape
            self.foodPoint = 0, 0
            self.randomFoodLocation()
            self.score = 0
            self.gameOver = False

        def randomFoodLocation(self):
            self.foodPoint = random.randint(100, 1000), random.randint(100, 600)

        def update(self, imgMain, currentHead):

            if self.gameOver:
                cvzone.putTextRect(imgMain, "GameOver", [300, 400], scale=7, thickness=5, offset=20)
                cvzone.putTextRect(imgMain, f'Score: {self.score}', [300, 550], scale=7, thickness=5, offset=20)

            else:
                px, py = self.previousHead
                cx, cy = currentHead

                self.points.append([cx, cy])
                distance = math.hypot(cx - px, cy - py)
                self.lengths.append(distance)
                self.currentLength += distance
                self.previousHead = cx, cy

                if self.currentLength > self.allowedLength:
                    for i, length in enumerate(self.lengths):
                        self.currentLength -= length
                        self.lengths.pop(i)
                        self.points.pop(i)
                        if self.currentLength < self.allowedLength:
                            break

                rx, ry = self.foodPoint
                if rx - self.wFood // 2 < cx < rx + self.wFood // 2 and ry - self.hFood // 2 < cy < ry + self.hFood // 2:
                    print("ate")
                    self.randomFoodLocation()
                    self.allowedLength += 50
                    self.score += 1

                if self.points:
                    for i, point in enumerate(self.points):
                        if i != 0:
                            cv2.line(imgMain, self.points[i - 1], self.points[i], (0, 0, 255), 20)
                    cv2.circle(img, self.points[-1], 20, (200, 0, 200), cv2.FILLED)

                # draw food
                rx, ry = self.foodPoint
                imgMain = cvzone.overlayPNG(imgMain, self.imgFood, (rx - self.wFood // 2, ry - self.hFood // 2))

                cvzone.putTextRect(imgMain, f'Score: {self.score}', [50, 80], scale=3, thickness=3, offset=10)

                # collision
                pts = np.array(self.points[:-2], np.int32)
                pts = pts.reshape((-1, 1, 2))
                cv2.polylines(imgMain, [pts], False, (0, 200, 0), 3)
                minDist = cv2.pointPolygonTest(pts, (cx, cy), True)

                if -1 <= minDist <= 1:
                    print("hit")
                    self.gameOver = True
                    self.points = []
                    self.lengths = []
                    self.currentLength = 0
                    self.allowedLength = 150
                    self.previousHead = 0, 0
                    self.randomFoodLocation()

            return imgMain

    game = SnakeGameClass("Resources/laddoo (1).png")

    while True:
        success, img = cap.read()
        img = cv2.flip(img, 1)
        hands, img = detector.findHands(img, flipType=False)

        if hands:
            lmList = hands[0]['lmList']
            pointIndex = lmList[8][0:2]
            img = game.update(img, pointIndex)
        cv2.imshow("Image", img)
        key = cv2.waitKey(1)
        if key == ord("r"):

            game.gameOver = False


    print("Launching Hungry-Snake")

# Create the main application window
root = tk.Tk()
root.title("MY GAMES")
root.geometry("800x500")

background_image = Image.open("Resources/bg (1).jpg")
background_photo = ImageTk.PhotoImage(background_image)

canvas = tk.Canvas(root, width=800, height=600)
canvas.pack(fill="both", expand=True)

canvas.create_image(0, 0, image=background_photo, anchor="nw")

canvas.create_text(400, 200, text="VIRTUAL GAMES", font=("Arial Bold", 50), fill="white", anchor="center")


button1 = tk.Button(root, text="PING-PONG", command=play_game_1, bg="blue", fg="black", font=("Arial", 18))
button1.place(relx=0.3, rely=0.7, anchor="center")

button2 = tk.Button(root, text="HUNGRY SNAKE", command=play_game_2, bg="yellow", fg="black", font=("Arial", 18))
button2.place(relx=0.7, rely=0.7, anchor="center")

# Start the Tkinter event loop
root.mainloop()
