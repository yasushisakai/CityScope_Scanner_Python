# imports packages
import numpy as np
import argparse
import cv2
import socket

##################################################

colRangeDict = {0: [np.array([0, 70, 50], np.uint8),  # red down
                    np.array([10, 255, 255], np.uint8)],  # red up
                1: [np.array([0, 0, 0], np.uint8),  # black d
                    np.array([0, 0, 50], np.uint8)],  # black u
                2: [np.array([0, 0, 50], np.uint8),  # white d
                    np.array([0, 0, 100], np.uint8)]}  # wihte u

colDict = {0: (0, 0, 255),  # red
           1: (0, 0, 0),  # black
           2: (255, 255, 255)}  # white

##################################################


def colorSelect(meanColor):
    # convert color to hsv for oclidian distance
    bgrToHsv = cv2.cvtColor(meanColor, cv2.COLOR_BGR2HSV)
    bgrToGray = cv2.cvtColor(meanColor, cv2.COLOR_BGR2GRAY)
    # # try to find if this color is in range [0 or 255]

    colRange = int(cv2.inRange(
        bgrToHsv, colRangeDict[0][0], colRangeDict[0][1]))
    if colRange == 255:
        colResult = 0
    elif colRange != 255:
        if int(bgrToGray) < 125:
            colResult = 1
        else:
            colResult = 2
    return colResult

##################################################


def max_rgb_filter(image):
    # split the image into its BGR components
    (B, G, R) = cv2.split(image)
    # find the maximum pixel intensity values for each
    # (x, y)-coordinate,, then set all pixel values less
    # than M to zero
    M = np.maximum(np.maximum(R, G), B)
    R[R < M] = 0
    G[G < M] = 0
    B[B < M] = 0
    # merge the channels back together and return the image
    return cv2.merge([B, G, R])


##################################################


def sendOverUDP(udpPacket):
    UDP_IP = "127.0.0.1"
    UDP_PORT = 5005
    # convert to string and encode the packet
    udpPacket = str(udpPacket).encode()
    # debug
    print('\n', "UDP message:", '\n', udpPacket)
    # open UDP socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.sendto(udpPacket, (UDP_IP, UDP_PORT))


##################################################

def checkForNewGrid():
    '''
pseudo code here:
if no change to results array, do nothing
else, compse the sliced submatrix of X*Y for each grid cell

import numpy as np
    a = np.reshape(np.arange(162), (18, 9))
    print(a)
    b = a[0: 3, 0: 3]
    print(b)

'''

##################################################


def findType(meanColor):
    print('########################################################')
    cc = 0
    for i in range(0, gridX*3, 3):
        for j in range(0, gridY*3, 3):
            # make submatrix of 3x3
            subMatrix = resultColorArray[i:(i+3), j:(j+3)].flatten()
            # print it
            print('\n', cc, '\n', subMatrix)
            cc += 1

##################################################


# hardcode the locations of the scanners
scannersHardcodeList = [
    15, 43, 85, 113, 155, 183,
    18, 46, 88, 116, 158, 186,
    21, 49, 91, 119, 161, 189
]


def makeGridOrigins(videoResX, videoResY):

    # actual locations of scanners
    scannersLocationsArr = []
    # zreo the counter
    c = 0
    for x in range(0, videoResX - int(videoResX/14), int(videoResX/14)):
        for y in range(0, videoResX-int(videoResX/8), int(videoResY/8)):

            #
            # check if this poistion is in hardcoded locations
            # array and if so get its position
            #
            if c in scannersHardcodeList:
                # cv2.circle(distortVid, (x, y), 20, (255, 0, 0),
                #            thickness=1, lineType=8, shift=0)

                # # create text display on bricks
                # cv2.putText(distortVid, str(c),
                #             (x-2, y), cv2.FONT_HERSHEY_SIMPLEX,
                #             0.3, (0, 0, 255))

                # append this loction to array for scanners
                scannersLocationsArr.append([x, y])
            # count
            c += 1
    print("Init scanner array: ", scannersLocationsArr,
          '\n', len(scannersLocationsArr))
    return scannersLocationsArr


'''

for x in range(0, gridX*step*3, step):
        for y in range(0, gridY*step*3, step):

            # set scanner crop box size and position
            # at x,y + crop box size
            crop = distortVid[y:y+cropSize, x:x+cropSize]

            # draw rects with mean value of color
            meanCol = cv2.mean(crop)

            # convert colors to rgb
            b, g, r, _ = np.uint8(meanCol)
            mCol = np.uint8([[[b, g, r]]])

            # select the right color based on sample
            scannerCol = MODULES.colorSelect(mCol)
            thisColor = colors[scannerCol]

            # draw rects with frame colored by range result
            cv2.rectangle(distortVid, (x-1, y-1),
                          (x+cropSize + 1, y+cropSize + 1),
                          thisColor, 1)

            # draw the mean color itself
            cv2.rectangle(distortVid, (x, y),
                          (x+cropSize, y+cropSize),
                          meanCol, -1)

            # create text display on bricks
            cv2.putText(distortVid, str(scannerCol),
                        (x + int(cropSize/3), y+cropSize), cv2.FONT_HERSHEY_SIMPLEX,
                        0.3, (0, 0, 0))

            # add colors to array for type analysis
            colorArr[counter] = scannerCol
            counter += 1

    # create the output colors array
    resultColorArray = colorArr.reshape(gridSize, gridSize).transpose()

    # draw the video to screen
    cv2.imshow("webcamWindow", distortVid)

    # break video loop by pressing ESC
    key = cv2.waitKey(10) & 0xFF
    if key == 27:
        break

        '''
