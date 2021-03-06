#
#  07-AdaptiveThreshold.py
#
#  Seventh lesson in a tutorial for detecting a target in opencv using python on a raspberry pi.
#  This lesson we check the four corners of our detection and measure the angles, we only keep detections where the angles are near 90 degrees
#
#    The algorithim follows these steps:
#		1. Uses a threshold or an optional adaptive threshold to create a binary image
#		2. Finds the contours of the binary image
#		3. Gets the convex hull of each contour
#		4. Checks to see that the hull has a sufficently large hull
#		5. Approximates the hull in order to get only 4 points (mostly a rectangle)
#		6. Checks each side to make sure they are mostly horizontal or vertical
#
#		* Also there is an auto-exposure algorithim running to keep the image with a constant average pixel value.
#
#   2/15/2016 - KAB - kevinabrandon@gmail.com
#

# import the necessary packages
from picamera.array import PiRGBArray
from picamera import PiCamera
import math
import time
import cv2
import numpy as np

print 'press "q" or "esc" to quit!'

# a call back function for the trackbars... it does nothing...
def nothing(jnk):
	pass

# a function that checks the 4 sides of a quadrilatal.  
# If all 4 sides are close to horizontal or vertical (+/- epsilon) return true
def CheckAngles(corners, epsilon):
	# require 4 corners
	if len(corners) != 4:
		return False

	# loop through each corner
	for i in range(4):
		i0 = i 				# index to the first corner
		i1 = (i + 1) % 4	# index to the next corner

		x = abs(corners[i1][0][0] - corners[i0][0][0])	# the difference in x
		y = abs(corners[i1][0][1] - corners[i0][0][1])	# the difference in y
		
		# if x > y, then it's mostly horizontal
		if x > y:	
			# the angle off horizontal
			theta = math.atan2(y,x) * 180 / math.pi
		else:
			# the angle off vertical 
			theta = math.atan2(x,y) * 180 / math.pi

		# if the angle is greater than epsilon, then it's not vertical or horizontal, so return false
		if abs(theta) > epsilon:
			return False 

	# if we get here then all corners have been checked and are okay.
	return True

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
cv2.createTrackbar('showThreshold', winName, 1, 1, nothing)  # shows the threshold binary image if 1, shows the original otherwise
cv2.createTrackbar('useAdaptiveThresh', winName, 1, 1, nothing) # 0 means regular threshold, 1 means adaptive threshold
cv2.createTrackbar('adaptiveThreshSize', winName, 11, 55, nothing) # size of adaptive threshold window 
cv2.createTrackbar('threshold', winName, 6, 255, nothing)  # the threshold value
cv2.createTrackbar('minPerim', winName, 100, 1000, nothing)  # the minimum perimiter of the convex hull to be kept
cv2.createTrackbar('autoShutter', winName, 22, 255, nothing) # used to automatically set the shutter speed, this is the target average pixel value.
cv2.createTrackbar('angleOffHoriz', winName, 20, 45, nothing) # used to require sides to be aligned vertical or horizontal

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
	useAdaptive = cv2.getTrackbarPos('useAdaptiveThresh', winName)
	thresh = cv2.getTrackbarPos('threshold',winName)
	minPerim = cv2.getTrackbarPos('minPerim', winName)
	autoShutter = cv2.getTrackbarPos('autoShutter', winName)
	eps = cv2.getTrackbarPos('angleOffHoriz', winName)
	adaptiveSize = cv2.getTrackbarPos('adaptiveThreshSize', winName)
	if adaptiveSize < 3: adaptiveSize = 3
	if adaptiveSize % 2 == 0: adaptiveSize += 1
	ss = camera.shutter_speed	# also get the shutter speed.

	#start timer
	t = cv2.getTickCount()

	# grab the raw NumPy array representing the image
	drawnImage = image = frame.array

	# convert to a grayscale image
	gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

	# calculate the avarage pixel value
	avg = cv2.mean(gray_image)

	# threshold the grayscale image
	if useAdaptive == 0:
		ret, threshImg = cv2.threshold(gray_image, thresh, 255, cv2.THRESH_BINARY)
	else:
		threshImg = cv2.adaptiveThreshold(gray_image, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY_INV, adaptiveSize, thresh)
	# if the trackbar is set to 1, use the threshold image to draw on instead
	if drawThresh == 1:
		# convert the threshold image back to color so we can draw on it with colorful lines
		drawnImage = cv2.cvtColor(threshImg, cv2.COLOR_GRAY2RGB)

	# find the contours in the thresholded image...
	im2, contours, high = cv2.findContours(threshImg, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)

	# the arrays of detected targets, they're empty now, but we'll fill them next.
	finalTargets = []

	# for each contour we found...
	for cnt in contours:
		# get the convexHull
		hull = cv2.convexHull(cnt)

		# get the perimiter of the hull
		perim = cv2.arcLength(hull, True)

		# is the the perimiter of the hull is > than the minimum allowed?
		if perim >= minPerim: 
			#approximate the hull:
			aproxHull = cv2.approxPolyDP(hull, 0.1 * perim, True)

			# only add this target if it has 4 verticies
			if len(aproxHull) == 4:
				# check to see if the 4 sides are near horizontal or vertical
				if CheckAngles(aproxHull, eps):
					# add the contour to the list of final targets
					finalTargets.append(aproxHull)

	# end the timer
	t = cv2.getTickCount() - t
	time = t / cv2.getTickFrequency() * 1000

	# time to draw on top of the original image....

	# draw all the detected hulls back on the original image (green with a width of 3)
	cv2.drawContours(drawnImage, finalTargets, -1, green, 3)
	
	# draw some text with status...
	text = 'Detect Time: %.0f ms' % (time)
	cv2.putText(drawnImage, text, (10, 10), cv2.FONT_HERSHEY_SIMPLEX, 0.33, red, 1)
	text = 'Avg Pixel: %.0f' % (avg[0])
	cv2.putText(drawnImage, text, (10, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.33, red, 1)
	text = '# Detections: %d' % (len(finalTargets))
	cv2.putText(drawnImage, text, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.33, red, 1)
	text = 'shutter speed: %d' % (ss)
	cv2.putText(drawnImage, text, (10, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.33, red, 1)

	# show the frame
	cv2.imshow(winName, drawnImage)
	
	# Important!  Clear the stream in preparation for the next frame
	rawCapture.truncate(0)
 
 	# calculate the increment for the shutter speed by 1% of it's current value
 	inc = 0
	if avg[0] > (autoShutter + 2):
	 	inc = -max(int(ss * 0.10), 2)  # if it's less than 2 use 2 
	if avg[0] < (autoShutter - 2):
	 	inc = max(int(ss * 0.10), 2)  # if it's less than 2 use 2 

	# print 'avg: %.0f, target value: %d, ss: %d, inc: %d' % (avg[0], autoShutter, ss, inc)
	
	# set the shutter speed
	camera.shutter_speed = ss + inc

	# get the key from the keyboard
	key = cv2.waitKey(1) & 0xFF

	# if the `q` or 'esc' key was pressed, break from the loop
	if key == ord("q") or key == 27:
		break
