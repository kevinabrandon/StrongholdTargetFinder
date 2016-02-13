#
#  07-CheckVertHoriz.py
#
#  Seventh lesson in a tutorial for detecting a target in opencv using python on a raspberry pi.
#  	This lesson we check the 4 sides of the box to see if they are aligned vertically and horizontally.  
#  	We only keep the ones that are.
#  
#    The algorithim follows these steps:
#		1. Uses a threshold to create a binary image
#		2. Finds the contours of the binary image
#		3. Gets the convex hull of each contour
#		4. Checks to see that the hull has a sufficently large hull
#		5. Approximates the hull in order to get only 4 points (mostly a rectangle)
#		6. Checks the angles of each corner of the hull to verify they are close to 90 degrees
#		7. Checks the sides of the rectangle to see if they are alligned vertically and horizontally.
#
#		* Also there is an auto-exposure algorithim running to keep the image with a constant average pixel value.
#
#
#   2/13/2016 - KAB - kevinabrandon@gmail.com
#


# import the necessary packages
from picamera.array import PiRGBArray
from picamera import PiCamera
import math
import time
import cv2
import numpy as np

print 'detectTarget!!!  press "q" or "esc" to quit!'

# a call back function for the trackbars... it does nothing...
def nothing(jnk):
	pass

# returns the magnitude of a 2d vector
def Mag2D(v):
	return math.sqrt(v[0]**2 + v[1]**2)

# returs the normalized 2d vector
def Norm2D(v):
	vmag = Mag2D(v)
	return [ v[0] / vmag,  v[1] / vmag]

# returns the dot product of a 2d vector
def DotProd2D(v1, v2):
	return v1[0] * v2[0] + v1[1] * v2[1]

# returns the angle between two vectors in degrees
# 	the angle between two vectors is the arccosine of the dot product between their 
#	normalized vectors:	http://www.euclideanspace.com/maths/algebra/vectors/angleBetween/
def AngleBetweenVectors(v1, v2):
	dot = min(DotProd2D(Norm2D(v1), Norm2D(v2)), 1)	# dot product of the normalized vectors
	return math.acos(dot) * 180 / math.pi

# a function that checks the 4 corners and sides of a quadrilateral.  
# If all 4 corners are close to 90 degrees (+/- epsilon) AND
# all edges are near horizontal or vertical (+/- phi) return true
def HaveRightAnglesAndHoriz(corners, epsilon, phi):
	# require verts to have a length of 4
	if len(corners) != 4:
		return False

	# loop through each vertex
	for i in range(4):
		i0 = i 				# index to the first vertex
		i1 = (i + 1) % 4	# index to the second vertex... we're going to find the angle here!
		i2 = (i + 2) % 4	# index to the third vertex

		v1 = corners[i1][0] - corners[i0][0]	# the first normalized vector
		v2 = corners[i2][0] - corners[i1][0]	# the second normalized vector

		theta = AngleBetweenVectors(v1, v2)		# get the angle between the two vectors

		# if the difference between theta and 90 degrees is greater than epsilon then return false
		if abs(theta - 90) > epsilon:
			return False 

		# now check the side of the rectangle to see if it's level
		axis = None 

		# if abs(x) > abs(y) then the vector is more horizontal
		if abs(v1[0]) > abs(v1[1]):	
			axis = [1,0]	# vector pointing right, used to compare with horizontal sides.
		else:
			axis = [0,1]	# vector pointing up, used to compare with vertical sides

		theta = abs(AngleBetweenVectors(v1, axis))	# gets the angle bettween our side and it's axis

		if theta > 90:  # the angle may be 180 degrees, so check to see if it's big, if it is subtract 180
			theta -= 180

		# now check to see if the angle is greater than phi (the maximum tollarnace)
		if abs(theta) > phi:
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
cv2.createTrackbar('showThreshold', winName, 0, 1, nothing)  # shows the threshold binary image if 1, shows the original otherwise
cv2.createTrackbar('threshold', winName, 35, 255, nothing)  # the threshold value
cv2.createTrackbar('minPerim', winName, 100, 1000, nothing)  # the minimum perimiter of the convex hull to be kept
cv2.createTrackbar('autoShutter', winName, 22, 255, nothing) # used to automatically set the shutter speed, this is the target average pixel value.
cv2.createTrackbar('off90Degrees', winName, 20, 45, nothing) # used to require angles of detected target to be near 90 degrees (this is how near)
cv2.createTrackbar('offHoriz', winName, 20, 45, nothing) # used to require the target to be aligned horizontally (+/- this variable)

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
	autoShutter = cv2.getTrackbarPos('autoShutter', winName)
	off90 = cv2.getTrackbarPos('off90Degrees', winName)
	offHoriz = cv2.getTrackbarPos('offHoriz', winName)
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
	ret, threshImg = cv2.threshold(gray_image, thresh, 255, cv2.THRESH_BINARY)

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
		# get the convexHull:
		hull = cv2.convexHull(cnt)
		# get the perimiter of the hull:
		perim = cv2.arcLength(hull, True)

		# is the the perimiter of the hull > than the minimum allowed?
		if perim > minPerim: 
			#approximate the hull:
			aproxHull = cv2.approxPolyDP(hull, 0.1 * perim, True)

			# only add this target if it has 4 verticies
			if len(aproxHull) == 4:
				# check to see if the 4 verticies are near right angles and the rectangle isn't rotated
				if HaveRightAnglesAndHoriz(aproxHull, off90, offHoriz):
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
