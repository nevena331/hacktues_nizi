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

debug_image = thresh.copy()
cv2.drawContours(debug_image, [screen_contour], -1, (0, 255, 0), 2)

filtered = four_point_transform(thresh, screen_contour.reshape(4, 2))
cv2.imwrite("imagefiltered.jpg", filtered)


#Text from Image Scanner

import pytesseract

inverted_filtered = cv2.bitwise_not(filtered)
resized = cv2.resize(inverted_filtered, None, fx=2, fy=2, interpolation=cv2.INTER_CUBIC)
custom_config = r'--oem 3 --psm 6'  # OCR Engine Mode 3, Page Segmentation Mode 6 
extracted_text = pytesseract.image_to_string(resized, config=custom_config, lang="eng")


#Text Sender

import re
import json

def extract_receipt_data(ocr_text):
    data = {}

    lines = ocr_text.strip().split("\n")
    data["Store Name"] = lines[0].strip()

    datetime_match = re.search(r'(\w{3} \d{2}/\d{2}/\d{4}) (\d{1,2}:\d{2} [APM]{2})', ocr_text)
    date_match = re.search(r'(\d{2}/\d{2}/\d{4})', ocr_text)

    if datetime_match:
        data["Date & Time"] = f"{datetime_match.group(1)} {datetime_match.group(2)}"
    elif date_match:
        data["Date & Time"] = date_match.group(1)

    subtotal_match = re.search(r'Sub\s*Total\s*USD?\$?\s*([\d.]+)', ocr_text, re.IGNORECASE)
    subtotal = float(subtotal_match.group(1)) if subtotal_match else None

    tip_match = re.search(r'Tip[:\s]+([\d.]+)', ocr_text, re.IGNORECASE)
    tip = float(tip_match.group(1)) if tip_match else None

    total_match = re.search(r'Total\s*USD?\$?\s*([\d.]+)', ocr_text, re.IGNORECASE)
    total_price = float(total_match.group(1)) if total_match else None

    print(subtotal,tip,total_price)
    if(tip is not None):
        if(total_price==subtotal and tip>0):
            total_price = None
    elif(total_price==subtotal):
        subtotal = None

    if subtotal is None and tip is None and total_price is None:
        return json.dumps({"error": "No subtotal, tip, or total found. This might not be a valid receipt."}, indent=4)

    if subtotal is not None and total_price is not None and (tip is None):
        tip = round(total_price - subtotal, 2) 

    elif tip is not None and total_price is not None and subtotal is None:
        subtotal = round(total_price - tip, 2)  

    elif subtotal is not None and tip is not None and total_price is None:
        total_price = round(subtotal + tip, 2) 

    if total_price is not None and subtotal is None and tip is None:
        data["Total Price"] = total_price
        return json.dumps(data, indent=4)

    if tip is None:
        return json.dumps({"error": "Unable to calculate Tip. Receipt might be incomplete."}, indent=4)

    data["Subtotal"] = subtotal
    data["Tip"] = tip

    return json.dumps(data, indent=4)


print(extract_receipt_data(extracted_text) )
