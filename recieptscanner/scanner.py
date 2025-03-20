import numpy as np
import cv2
import os
import imutils
from imutils.perspective import four_point_transform

os.environ["QT_QPA_PLATFORM"] = "offscreen" #error handling deto maj ne ni trqbva????? 

image = cv2.imread('testimage3.jpg')

#ot tuk

gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

blurred = cv2.GaussianBlur(gray, (5, 5), 0)

thresh = cv2.adaptiveThreshold(
    blurred, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 11, 2)

#do tuk - kopirah tiq neshta 2 puti shtoto nz kak ne bachkaha purviq put

kernel = np.ones((5, 5), np.uint8)
thresh = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel)

contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

contours = sorted(contours, key=cv2.contourArea, reverse=True)
screen_contour = None

for contour in contours:
    peri = cv2.arcLength(contour, True)
    approx = cv2.approxPolyDP(contour, 0.02 * peri, True)

    if len(approx) == 4: 
        screen_contour = approx
        break

if screen_contour is not None:
    debug_image = image.copy()
    cv2.drawContours(debug_image, [screen_contour], -1, (0, 255, 0), 2)

    warped = four_point_transform(image, screen_contour.reshape(4, 2))

    gray = cv2.cvtColor(warped, cv2.COLOR_BGR2GRAY)

    blurred = cv2.GaussianBlur(gray, (5, 5), 0)

    thresh = cv2.adaptiveThreshold(
        blurred, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 11, 2)

    kernel = np.ones((5, 5), np.uint8)
    thresh = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel)

    cv2.imwrite("warped_perspective.jpg", thresh)
    print("Perspective transformation completed successfully!")
else:
    print("No rectangular contour found.")
