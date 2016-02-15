# StrongholdTargetFinder
This is a [Raspberry Pi](https://www.raspberrypi.org/) [OpenCV](http://opencv.org/) [python](https://www.python.org/) tutorial for detecting the [FRC Stronghold target](https://wpilib.screenstepslive.com/s/4485/m/24194/l/288983-target-info-and-retroreflection).

## Get the Pi Ready
I like to run with a headless pi - one that is not connected to a monitor, keyboard and mouse, and is only operated remotely.  I suggest [this tutorial](https://www.raspberrypi.org/forums/viewtopic.php?f=91&t=74176) to set it up.  The VNC server is essential to running with the desktop remotely.

## Install Python and OpenCV
Here I followed [this tutorial](http://www.pyimagesearch.com/2015/10/26/how-to-install-opencv-3-on-raspbian-jessie/) and it worked great for installing OpenCV 3.1.1

## Install git and clone this repository
Install git by typing: `sudo apt-get install git`
Then clone this project by typing:  `git clone https://github.com/kevinabrandon/StrongholdTargetFinder.git`

## Run the tutorias
To run a program simply type `python` followed by the filename of the program:
```python 00-ShowCamera.py```
