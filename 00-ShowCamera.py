#
#  00-ShowCamera.py
#
#  Zeroth lesson in a tutorial for detecting a target in opencv using python on a raspberry pi.
#  This lesson all we do is create window displaying video and writing some text on top of it.
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

	#start timer
	t = cv2.getTickCount()

	# grab the raw NumPy array representing the image
	image = frame.array
	
	# end the timer
	t = cv2.getTickCount() - t
	time = t / cv2.getTickFrequency() * 1000 # multiply by 1000 to get miliseconds

	# time to draw on top of the original image....

	# draw some text with status...
	text = 'Detect Time: %.0f ms' % (time)
	cv2.putText(image, text, (10, 10), cv2.FONT_HERSHEY_SIMPLEX, 0.33, red, 1)

	# show the frame
	cv2.imshow(winName, image)
	
	# Important!  Clear the stream in preparation for the next frame
	rawCapture.truncate(0)
 
	# get the key from the keyboard
	key = cv2.waitKey(1) & 0xFF

	# if the `q` key or the 'esc' key was pressed, break from the loop
	if key == ord("q") or key == 27:
		break
