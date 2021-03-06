# OpenCV 3.0.0  scan restricted area of input frames for circles of certain size
# Expect two circles; output average X center, and dX between the two circles
# J.Beale July 12 2015

import argparse
import datetime
import imutils
import time
import cv2
import numpy as np
import sys

yCropFrac = 3.7      # (14) crop off this (1/x) fraction of the top
xCropFrac = 30      # (14) crop off this (1/x) fraction of the left
fActive = 15.0      # (14) 1/y vertical fraction of active strip
rf = 1.0             # relative scaling factor
# --------------------------------------------------------------------------
# construct the argument parser and parse the arguments
ap = argparse.ArgumentParser()
ap.add_argument("-v", "--video", help="path to the video file")
ap.add_argument("-a", "--min-area", type=int, default=(rf*rf*500), help="minimum area size")
args = vars(ap.parse_args())

record = True  # should we record video output?
voname = 'track-out5.avi' # name of video output to save

fname = "none"
# if the video argument is None, then we are reading from webcam
if args.get("video", None) is None:
    camera = cv2.VideoCapture(0)
    time.sleep(4)
# otherwise, we are reading from a video file
else:
    fname = args["video"]
    camera = cv2.VideoCapture(fname)
    
grabbed, imgRAW = camera.read()   # get very first frame
if (not grabbed):
  print "Could not read input file %s" % fname
  sys.exit(-1)
  
ys,xs = imgRAW.shape[:2]  # get (ysize, xsize) and ignore #-channels if present

if (record):
    video = cv2.VideoWriter(voname, -1, 25, (xs,ys))  # open output video to record

# ===========================================================================
# loop over the frames of the video
# ===========================================================================
while grabbed:
  (grabbed, imgRAW) = camera.read()
  if not grabbed:
        break

  ys,xs = imgRAW.shape[:2]  # get (ysize, xsize) and ignore #-channels if present
  ys1, xs1 = ys, xs
  imgG = cv2.cvtColor(imgRAW,cv2.COLOR_BGR2GRAY)

  #print "x,y = %d,%d" % (xs, ys)
  ycrop = int(ys1/yCropFrac)  # fraction of top edge of frame to mask
  ycrop2 = ycrop + int(ys1/fActive)  # mask off bottom part
  xcrop = int(xs1/xCropFrac)  # fraction of left edge to mask
  cv2.rectangle( imgG, ( 0,0 ), ( xs1, ycrop), ( 0,0,0 ), -1, 8 ) # black rect (cover time-date)
  cv2.rectangle( imgG, ( 0,ycrop2 ), ( xs1-1, ys1-1), ( 0,0,0 ), -1, 8 ) # cover bottom fgnd
  cv2.rectangle( imgG, ( 0,0 ), ( xcrop, ys1-1), ( 0,0,0 ), -1, 8 ) # black rect at left edge
  
  img = cv2.medianBlur(imgG,5)
  cimg = cv2.cvtColor(imgG,cv2.COLOR_GRAY2BGR)

  circles = cv2.HoughCircles(img,cv2.HOUGH_GRADIENT,1,20,
                            param1=40,param2=17,minRadius=5,maxRadius=9) # param1 = 50 param2 = 19

  maxObjects = 3                               # how many circles to remember                
  x = np.float32(np.zeros(maxObjects))         # x center coordinates    
  count = 0  
  if (circles is None):
    # print "No circles found"
    cv2.imshow('detected circles',imgRAW)
  else:     
    # print "size = %5.1f" % circles.size                            
    circles = np.uint16(np.around(circles))

    for i in circles[0,:]:
      count += 1   # how many circles
      xc = int(i[0])
      yc = int(i[1])
      rc = int(i[2])
      y1 = int(yc+rc+4)
      y2 = int(yc+100)
      # draw the outer circle
      cv2.circle(imgRAW,(xc,yc),rc+2,(0,255,0),2,cv2.LINE_AA)
      # draw the center of the circle
      cv2.circle(imgRAW,(xc,yc),2,(0,0,255),2,cv2.LINE_AA)
      # draw vertical line below circle
      cv2.line(imgRAW,(xc,y1),(xc,y2),(0,0,255),2)
      
      # print "%d, %5.1f, %5.1f, %5.1f" % (count,i[0]/hscalefac,i[1],i[2]) # circle parameters (x,y) r
      if (count < 3):
        x[count] = i[0]  # x center coordinate of this circle

    if (record):
      video.write(imgRAW)                    # save frame of output video
    cv2.imshow('detected circles',imgRAW)
    if (count > 1):
      print "%5.1f, %5.1f" % ((x[2]+x[1])/2,  abs(x[2]-x[1]))

  cv2.waitKey(1)
  
# cleanup the files and close any open windows
if (record):
    video.release()      
cv2.destroyAllWindows()
