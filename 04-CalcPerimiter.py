#
#  04-CalcPerimiter.py
#
#  Fourth lesson in a tutorial for detecting a target in opencv using python on a raspberry pi.
#  This lesson we calculate the perimter of the convex hull, and only keep big ones.
#
#    The algorithim follows these steps:
#		1. Uses a threshold to create a binary image
#		2. Finds the contours of the binary image
#		3. Gets the convex hull of each contour
#		4. Checks to see that the hull has a sufficently large hull
#
#   2/10/2016 - KAB - kevinabrandon@gmail.com
#


# import the necessary packages
from picamera.array import PiRGBArray
from picamera import PiCamera
import time
import cv2
import numpy as np

print 'press "q" or "esc" to quit!'

# a call back function for the trackbars... it does nothing...
def nothing(jnk):
	pass

#some color values we'll be using
red = (0, 0, 255)
green = (0, 255, 0)
blue = (255, 0, 0)

# the resoultion of the camera... common values: (1296,972), (640,480), (320,240), (240, 180)
# smaller resolutions work best when viewed remotely, however they all work great natively
resolution = (320,240)

# create the named window and the trackbars...
winName = 'Target Detect'
cv2.namedWindow(winName)
cv2.createTrackbar('showThreshold', winName, 0, 1, nothing)  # shows the threshold binary image if 1, shows the original otherwise
cv2.createTrackbar('threshold', winName, 100, 255, nothing)  # the threshold value
cv2.createTrackbar('minPerim', winName, 100, 1000, nothing)  # the minimum perimiter of the convex hull to be kept

# initialize the camera and grab a reference to the raw camera capture
# there are a lot of options we can do here... check out the examples
# at http://picamera.readthedocs.org/en/release-1.9/recipes1.html
camera = PiCamera()
camera.resolution = resolution
camera.shutter_speed = 10000
camera.exposure_mode = 'off'

rawCapture = PiRGBArray(camera, size=resolution)
 
# allow the camera to warmup
time.sleep(0.1)
 
# capture frames from the camera
for frame in camera.capture_continuous(rawCapture, format="bgr", use_video_port=True):

	# get the trackbar values...
	drawThresh = cv2.getTrackbarPos('showThreshold', winName)
	thresh = cv2.getTrackbarPos('threshold',winName)
	minPerim = cv2.getTrackbarPos('minPerim', winName)

	#start timer
	t = cv2.getTickCount()

	# grab the raw NumPy array representing the image
	drawnImage = image = frame.array

	# convert to a grayscale image
	gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

	# threshold the grayscale image
	ret, threshImg = cv2.threshold(gray_image, thresh, 255, cv2.THRESH_BINARY)

	# if the trackbar is set to 1, use the threshold image to draw on instead
	if drawThresh == 1:
		# convert the threshold image back to color so we can draw on it with colorful lines
		drawnImage = cv2.cvtColor(threshImg, cv2.COLOR_GRAY2RGB)

	# find the contours in the thresholded image...
	im2, contours, high = cv2.findContours(threshImg, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)

	hulls = []
	# for each contour we found...
	for cnt in contours:
		# get the convexHull
		hull = cv2.convexHull(cnt)
		# get the perimiter of the hull
		perim = cv2.arcLength(hull, True)
		# is the the perimiter of the hull > than the minimum allowed?
		if perim > minPerim: 
			# add it to the array of detected hulls.
			hulls.append(hull)

	# end the timer
	t = cv2.getTickCount() - t
	time = t / cv2.getTickFrequency() * 1000

	# time to draw on top of the original image....

	# define the hulls instead of the contours.
	cv2.drawContours(drawnImage, hulls, -1, green, 3)

	# draw some text with status...
	text = 'Detect Time: %.0f ms' % (time)
	cv2.putText(drawnImage, text, (10, 10), cv2.FONT_HERSHEY_SIMPLEX, 0.33, red, 1)
	text = '# Hulls: %d' % (len(hulls))
	cv2.putText(drawnImage, text, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.33, red, 1)
	
	# show the frame
	cv2.imshow(winName, drawnImage)
	
	# Important!  Clear the stream in preparation for the next frame
	rawCapture.truncate(0)
 
	# get the key from the keyboard
	key = cv2.waitKey(1) & 0xFF

	# if the `q` key was pressed, break from the loop
	if key == ord("q") or key = 27:
		break
