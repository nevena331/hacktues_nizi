import numpy as np
import cv2
import os
import imutils
from imutils.perspective import four_point_transform


#Image Filtering

os.environ["QT_QPA_PLATFORM"] = "offscreen" #error handling deto maj ne ni trqbva????? 

image = cv2.imread('./testimages/testimage4.jpeg')

gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

#blurred = cv2.GaussianBlur(gray, (5, 5), 0)

#thresh = cv2.adaptiveThreshold(
#    blurred, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 11, 2)

kernel = np.ones((5, 5), np.uint8)
thresh = cv2.morphologyEx(gray, cv2.MORPH_CLOSE, kernel)

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
    debug_image = thresh.copy()
    cv2.drawContours(debug_image, [screen_contour], -1, (0, 255, 0), 2)

    filtered = four_point_transform(thresh, screen_contour.reshape(4, 2))

    cv2.imwrite("imagefiltered.jpg", filtered)

    print("Perspective transformation completed successfully!")
else:
    print("No rectangular contour found.")

    #return message to user to post a better image;


#Text from Image Scanner

import pytesseract

inverted_filtered = cv2.bitwise_not(filtered)
resized = cv2.resize(inverted_filtered, None, fx=2, fy=2, interpolation=cv2.INTER_CUBIC)
custom_config = r'--oem 3 --psm 6'  # OCR Engine Mode 3, Page Segmentation Mode 6 
extracted_text = pytesseract.image_to_string(resized, config=custom_config, lang="eng")

print(extracted_text)