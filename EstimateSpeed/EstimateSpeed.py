import cv2
import dlib
import time
import threading
import math
from datetime import datetime
import os
from datetime import date
import datetime
import numpy as np

carCascade = cv2.CascadeClassifier('car_detect_harrcascade.xml')

video = cv2.VideoCapture('videoham1new.mp4')

speedLimit = 20
WIDTH = 1280
HEIGHT = 720

drawing = False
point1 = ()
point2 = ()
drawingTwo = False
pointTwo_1 = ()
pointTwo_2 = ()
Mouse_count = False

def mouse_drawing(event, x, y, flags, params):
    global point1, point2, drawing
    global pointTwo_1, pointTwo_2, drawingTwo, Mouse_count

    # ----------Mouse 1-------
    if Mouse_count == False:
        if event == cv2.EVENT_LBUTTONDOWN:
            if drawing is False:
                drawing = True
                point1 = (x, y)
            # else:
            # drawing = False

        elif event == cv2.EVENT_MOUSEMOVE:
            if drawing is True:
                point2 = (x,y)
        elif event == cv2.EVENT_LBUTTONUP:
            drawing = False
            Mouse_count = True

def estimateSpeed(location1, location2):
	d_pixels = math.sqrt(math.pow(location2[0] - location1[0], 2) + math.pow(location2[1] - location1[1], 2))
	ppm = 7
	d_meters = d_pixels / ppm

	fps = 12
	speed = d_meters * fps * 3.6
	return speed
def blackout(image):
    xBlack = 0
    yBlack = 0
    triangle_cnt = np.array( [[0,0], [xBlack,0], [0,yBlack]] )
    triangle_cnt2 = np.array( [[WIDTH,0], [WIDTH-xBlack,0], [WIDTH,yBlack]] )
    cv2.drawContours(image, [triangle_cnt], 0, (0,0,0), -1)

    return image

def trackMultipleObjects():
	rectangleColor = (0, 255, 0)
	frameCounter = 0
	currentCarID = 0
	fps = 0

	point1 = (100, 100)
	point2 = (1000, 600)

	carTracker = {}
	carNumbers = {}
	carLocation1 = {}
	carLocation2 = {}
	speed = [None] * 1000

	out = cv2.VideoWriter('outpy.avi',cv2.VideoWriter_fourcc('M','J','P','G'), 10, (WIDTH,HEIGHT))

	while True:
		start_time = time.time()
		rc, image = video.read()
		if type(image) == type(None):
			break
		image = cv2.resize(image, (WIDTH, HEIGHT))
		resultImage = blackout(image)
		frameCounter = frameCounter + 1
		carIDtoDelete = []
		for carID in carTracker.keys():
			trackingQuality = carTracker[carID].update(image)
			if trackingQuality < 7:
				carIDtoDelete.append(carID)
		for carID in carIDtoDelete:
			#print ('Removing carID ' + str(carID) + ' from list of trackers.')
			#print ('Removing carID ' + str(carID) + ' previous location.')
			#print ('Removing carID ' + str(carID) + ' current location.')
			carTracker.pop(carID, None)
			carLocation1.pop(carID, None)
			carLocation2.pop(carID, None)

		if point1 and point2:
			r = cv2.rectangle(resultImage, point1, point2, (100, 50, 200), 5)
			frame_ROI = image[point1[1]:point2[1], point1[0]:point2[0]]
			if drawing is False:
				ROI_grayscale = cv2.cvtColor(frame_ROI, cv2.COLOR_BGR2GRAY)
				cars_ROI = carCascade.detectMultiScale(ROI_grayscale, 1.3, 20, 18, (24, 24))
				for (x, y, w, h) in cars_ROI:
					cv2.putText(resultImage, " " + str(cars_ROI.shape[0]), (970, 90),cv2.FONT_HERSHEY_TRIPLEX, 1, (0, 255,255), 1)
					if cars_ROI.shape[0] > 4 :
						cv2.putText(resultImage, 'Canh bao xe dong di chuyen cham !!! ', (150, 90), cv2.FONT_HERSHEY_SIMPLEX, 0.75, (255, 255, 255),2)

		if not (frameCounter % 10):
			gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
			cars = carCascade.detectMultiScale(gray, 1.3, 20, 18, (24, 24))

			for (_x, _y, _w, _h) in cars:
				x = int(_x)
				y = int(_y)
				w = int(_w)
				h = int(_h)

				x_bar = x + 0.5 * w
				y_bar = y + 0.5 * h

				matchCarID = None

				for carID in carTracker.keys():
					trackedPosition = carTracker[carID].get_position()

					t_x = int(trackedPosition.left())
					t_y = int(trackedPosition.top())
					t_w = int(trackedPosition.width())
					t_h = int(trackedPosition.height())

					t_x_bar = t_x + 0.5 * t_w
					t_y_bar = t_y + 0.5 * t_h

					if ((t_x <= x_bar <= (t_x + t_w)) and (t_y <= y_bar <= (t_y + t_h)) and (x <= t_x_bar <= (x + w)) and (y <= t_y_bar <= (y + h))):
						matchCarID = carID

				if matchCarID is None:

					tracker = dlib.correlation_tracker()
					tracker.start_track(image, dlib.rectangle(x, y, x + w, y + h))

					carTracker[currentCarID] = tracker
					carLocation1[currentCarID] = [x, y, w, h]

					currentCarID = currentCarID + 1

		for carID in carTracker.keys():
			trackedPosition = carTracker[carID].get_position()

			t_x = int(trackedPosition.left())
			t_y = int(trackedPosition.top())
			t_w = int(trackedPosition.width())
			t_h = int(trackedPosition.height())

			carLocation2[carID] = [t_x, t_y, t_w, t_h]

		end_time = time.time()

		if not (end_time == start_time):
			fps = 1.0/(end_time - start_time)
			today = date.today()
			now = datetime.datetime.now()
			d1 = today.strftime("%d/%m/%Y")
			d2 = now.strftime(" %H:%M:%S")
			d3 = ("HE THONG CANH BAO XE UN TAC DUA VAO TOC DO ")
			d4 = ("So xe trong o: ")

		cv2.putText(resultImage, ' ' + str(d3), (450, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.75, (255.215, 0), 2)
		cv2.putText(resultImage, '' + str(d4), (750, 90), cv2.FONT_HERSHEY_SIMPLEX, 1, (0,255, 255), 2)
		cv2.putText(resultImage, "Number : {:03d}".format(currentCarID), (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.75,(0, 191, 255), 2)



		for i in carLocation1.keys():
			if frameCounter % 1 == 0:
				[x1, y1, w1, h1] = carLocation1[i]
				[x2, y2, w2, h2] = carLocation2[i]

				carLocation1[i] = [x2, y2, w2, h2]

				if [x1, y1, w1, h1] != [x2, y2, w2, h2]:
					if (speed[i] == None or speed[i] == 0) and y1 >= 280 and y1 <= 285:
						speed[i] = estimateSpeed([x1, y1, w1, h1], [x2, y2, w2, h2])

					if speed[i] != None and y1 >= 150:
						cv2.putText(resultImage, str(int(speed[i])) + " km/hr", (int(x1 + w1/2), int(y1-10)),cv2.FONT_HERSHEY_SIMPLEX, 0.75, (255, 0, 255), 2)
						if speed[i] < speedLimit:
							#cv2.putText(resultImage, 'Canh bao ', (250, 70), cv2.FONT_HERSHEY_SIMPLEX, 0.75,(255,255,255), 2)
							cv2.putText(resultImage, 'De nghi kiem tra camera ', (250, 70), cv2.FONT_HERSHEY_SIMPLEX, 0.75,(255,255,255), 2)

		cv2.imshow('result', resultImage)
		out.write(resultImage)
		if cv2.waitKey(33) == 27:
			break
	cv2.destroyAllWindows()
if __name__ == '__main__':
	trackMultipleObjects()


