import cv2
import numpy as np
from Tkinter import *


def centerClick(event, x, y, flags, param):
    global center, frame
    clone = frame.copy()
    if event == cv2.EVENT_LBUTTONDOWN:
        center = (x,y)
        cv2.circle(frame, (x,y), 4, (255,0,0), -1)
        cv2.imshow('CenterClick', frame)
        frame = clone.copy() # resets to original image so that if the user reselects the center, the old circle will not appear

def centerImg(img, x_c, y_c): # shifts image so that it is centered at (x_c, y_c)
    dx = (width/2) - x_c
    dy = (height/2) - y_c
    shiftMatrix = np.float32([[1, 0, dx], [0, 1, dy]])
    return cv2.warpAffine(img, shiftMatrix, (width, height))

def locate(event, x, y, flags, param):
    global frame, particleStart, particleEnd, particleCenter, particleRadius
    clone = frame.copy()
    if event == cv2.EVENT_LBUTTONDOWN:
        particleStart = (x,y)
    elif event == cv2.EVENT_LBUTTONUP:
        particleEnd = (x,y)
        particleCenter = ((particleEnd[0] + particleStart[0])/2, (particleEnd[1] + particleStart[1])/2)
        d2 = ((particleEnd[0] - particleStart[0])**2) + ((particleEnd[1] - particleStart[1])**2)
        particleRadius = (d2**(0.5))/2
        cv2.circle(frame, particleCenter, int(particleRadius+0.5), (255,0,0), 1)
        cv2.imshow('Locate Ball', frame)
        frame = clone.copy() # resets to original image

def circumferencePoints(event, x, y, flags, param):
    global npts, center, frame, xpoints, ypoints, r, poly1, poly2
    if event == cv2.EVENT_LBUTTONDOWN:
        if (npts == 0):
            xpoints = np.array([x])
            ypoints = np.array([y])
        else:
            xpoints = np.append(xpoints,x)
            ypoints = np.append(ypoints,y)
        npts+=1
        cv2.circle(frame, (x,y), 3, (0,255,0), -1)
        clone = frame.copy()
        if (len(xpoints) > 2):
            bestfit = calc_center(xpoints, ypoints)
            center = (bestfit[0], bestfit[1])
            r = bestfit[2]
            poly1 = np.array([[0,0],[frame.shape[1],0],[frame.shape[1],frame.shape[0]], [0,frame.shape[0]]])
            poly2 = np.array([[bestfit[0]+r,bestfit[1]]])
            circpts = 100
            for i in range(1,circpts):
                theta =  2*np.pi*(float(i)/circpts)
                nextpt = np.array([[int(bestfit[0]+(r*np.cos(theta))),int(bestfit[1]+(r*np.sin(theta)))]])
                poly2 = np.append(poly2,nextpt,axis=0)
            cv2.circle(frame, center, 4, (255,0,0), -1)
            cv2.circle(frame, center, r, (0,255,0), 1)
        cv2.imshow('CenterClick', frame) 
        frame = clone.copy()

def calc_center(xp, yp):
    n = len(xp)
    circleMatrix = np.matrix([[np.sum(xp**2), np.sum(xp*yp), np.sum(xp)], [np.sum(xp*yp), np.sum(yp**2), np.sum(yp)], [np.sum(xp), np.sum(yp), n]])
    circleVec = np.transpose(np.array([np.sum(xp*((xp**2)+(yp**2))), np.sum(yp*((xp**2)+(yp**2))), np.sum((xp**2)+(yp**2))]))
    ABC = np.transpose(np.dot(np.linalg.inv(circleMatrix), circleVec))
    xc = ABC.item(0)/2
    yc = ABC.item(1)/2
    a = ABC.item(0)
    b = ABC.item(1)
    c = ABC.item(2)
    d = (4*c)+(a**2)+(b**2)
    diam = d**(0.5)
    return np.array([int(xc), int(yc), int(diam/2)])

def annotateImg(img, i):
    font = cv2.FONT_HERSHEY_TRIPLEX

    dpro = 'DigiPyRo'
    dproLoc = (25, 50)
    cv2.putText(img, dpro, dproLoc, font, 1, (255, 255, 255), 1)
    
    #img[(height-25)-spinlab.shape[0]:height-25, (width-25)-spinlab.shape[1]:width-25] = spinlab
    img[25:25+spinlab.shape[0], (width-25)-spinlab.shape[1]:width-25] = spinlab

    #perStamp = 'Period (T): ' + str(round(per,1)) + ' s'
    #perLoc = (25, height-75)
    #cv2.putText(img, perStamp, perLoc, font, 1, (255, 255, 255), 1)
    #timestamp = 'Time: ' + str(round(((i/fps)/per),1)) + ' T'
    timestamp = 'Time: ' + str(round((i/fps),1)) + ' s'
    tLoc = (width - 225, height-25)
    cv2.putText(img, timestamp, tLoc, font, 1, (255, 255, 255), 1)

    prpm = 'Physical Rotation: '
    if (physicalRPM > 0):
        prpm += '+'
    prpm += str(physicalRPM) + 'RPM'
    
    drpm = 'Digital Rotation: '
    if (digiRPM > 0):
        drpm += '+'
    drpm += str(digiRPM) + 'RPM'
    pLoc = (25, height - 25)
    dLoc = (25, height - 75)
    cv2.putText(img, prpm, pLoc, font, 1, (255, 255, 255), 1)
    cv2.putText(img, drpm, dLoc, font, 1, (255, 255, 255), 1)

def start():
    vid = cv2.VideoCapture(filenameVar.get())

    global width, height, numFrames, fps, fourcc, video_writer, spinlab, npts
    npts = 0
    spinlab = cv2.imread('/Users/sammay/Desktop/SPINLab/DigiRo/spinlogo.png')
    #spinlab = cv2.resize(spinlab,spinlab.shape, interpolation = cv2.INTER_CUBIC)
    numFrames = int(vid.get(cv2.cv.CV_CAP_PROP_FRAME_COUNT))
    width = int(vid.get(cv2.cv.CV_CAP_PROP_FRAME_WIDTH))
    height = int(vid.get(cv2.cv.CV_CAP_PROP_FRAME_HEIGHT))
    #fps = (vid.get(cv2.cv.CV_CAP_PROP_FPS))
    fps = 29.97
    fourcc = cv2.cv.CV_FOURCC('m','p','4','v')
    video_writer = cv2.VideoWriter(savefileVar.get(), fourcc, fps, (width, height))

    global physicalRPM, digiRPM, dtheta, per
    physicalRPM = physRPMVar.get()
    digiRPM = digiRPMVar.get()
    dtheta = digiRPM*(6/fps)
    per = 60*(1 / np.abs(float(digiRPM)))

    startFrame = fps*startTimeVar.get()
    numFrames = int(fps*(endTimeVar.get() - startTimeVar.get()))

    # Close GUI window so rest of program can run
    root.destroy()

    global frame, center
    
    # Open first frame from video, user will click on center
    vid.set(cv2.cv.CV_CAP_PROP_POS_FRAMES, startFrame)
    ret, frame = vid.read()
    cv2.namedWindow('CenterClick')
    cv2.setMouseCallback('CenterClick', circumferencePoints)

    cv2.imshow('CenterClick', frame)
    cv2.waitKey(0)
    cv2.destroyWindow('CenterClick')

    # Select initial position of ball
    vid.set(cv2.cv.CV_CAP_PROP_POS_FRAMES, startFrame)
    ret, frame = vid.read()
    cv2.namedWindow('Locate Ball')
    cv2.setMouseCallback('Locate Ball', locate)

    cv2.imshow('Locate Ball', frame)
    cv2.waitKey(0)
    cv2.destroyWindow('Locate Ball')


    t = np.empty(numFrames)
    ballX = np.empty(numFrames)
    ballY = np.empty(numFrames)
    ballPts = 0 #will identify the number of times that Hough Circle transform identifies the ball
    for i in range(numFrames):
        ret, frame = vid.read() # read next frame from video

        M = cv2.getRotationMatrix2D(center, i*dtheta, 1.0)
        rotated = cv2.warpAffine(frame, M, (width, height))
        cv2.fillPoly(rotated, np.array([poly1, poly2]), 0)
        cv2.circle(rotated, center, 4, (255,0,0), -1)
        centered = centerImg(rotated, center[0], center[1])
    
    
        centered = cv2.resize(centered,(width,height), interpolation = cv2.INTER_CUBIC)
        gray = cv2.cvtColor(centered, cv2.COLOR_BGR2GRAY)
        gray = cv2.medianBlur(gray,5)
        ballLoc = cv2.HoughCircles(gray, cv2.cv.CV_HOUGH_GRADIENT, 1, 20, param1=50, param2=20, minRadius = int(particleRadius * 0.7), maxRadius = int(particleRadius * 1.3))
        if type(ballLoc) != NoneType :
            for j in ballLoc[0,:]:
                cv2.circle(centered, (j[0],j[1]), j[2], (0,255,0),1)
                cv2.circle(centered, (j[0],j[1]), 2, (0,0,255), -1)
                ballX[ballPts] = j[0]
                ballY[ballPts] = j[1]
	    t[ballPts] = i*fps      
            ballPts += 1
        for k in range(ballPts-1):
            cv2.circle(centered, (int(ballX[k]), int(ballY[k])), 1, (255,0,0), -1)    	


        annotateImg(centered, i)
        video_writer.write(centered)

    ballX -= center[0]
    ballY -= center[1]    
    cv2.destroyAllWindows()
    vid.release()
    video_writer.release()

root = Tk()
root.title('DigiPyRo')
startButton = Button(root, text = "Start!", command = start)
startButton.grid(row=5, column=0)
digiRPMVar = DoubleVar()
physRPMVar = DoubleVar()
digiRPMEntry = Entry(root, textvariable=digiRPMVar)
physRPMEntry = Entry(root, textvariable=physRPMVar)
digiLabel = Label(root, text="Please enter desired digital rotation (RPM).")
physLabel = Label(root, text="Please enter physical rotation (RPM).")
digiRPMEntry.grid(row=1, column=1)
physRPMEntry.grid(row=0, column=1)
digiLabel.grid(row=1, column=0)
physLabel.grid(row=0, column=0)

filenameVar = StringVar()
filenameEntry = Entry(root, textvariable = filenameVar)
filenameLabel = Label(root, text="Specify full path to movie.")
filenameEntry.grid(row=2, column=1)
filenameLabel.grid(row=2, column=0)

savefileVar = StringVar()
savefileEntry = Entry(root, textvariable = savefileVar)
savefileLabel = Label(root, text="Save DigiPyRo-ed video as:")
savefileEntry.grid(row=3, column=1)
savefileLabel.grid(row=3, column=0)

startTimeVar = DoubleVar()
endTimeVar = DoubleVar()
startTimeEntry = Entry(root, textvariable = startTimeVar)
endTimeEntry = Entry(root, textvariable = endTimeVar)
startTimeLabel = Label(root, text="Select start and end times (in seconds)")
startTimeLabel.grid(row=4, column=0)
startTimeEntry.grid(row=4, column=1)
endTimeEntry.grid(row=4, column=2)

root.mainloop()
