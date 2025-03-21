import os
import imutils
import pytesseract
import re
import json
from dateutil import parser
from imutils.perspective import four_point_transform
import numpy as np
import cv2

#Language select
os.environ["QT_QPA_PLATFORM"] = "offscreen"  

print("1 - English")
print("2 - Bulgarian")
'''
while True:
    try:
        choice = int(input("Enter choice (1 or 2): ").strip())
        if choice in [1, 2]:
            break
        else:
            print("Invalid choice. Please enter 1 or 2.")
    except ValueError:
        print("Invalid input. Please enter a number (1 or 2).")
'''
choice=1
if (choice == 1): 
    language_choice = "english"    
elif(choice==2):
    language_choice="bulgarian"

def set_language_config(language):
    if language == "bulgarian":
        return {
            "ocr_lang": "bul+eng",
            "subtotal_regex": r'(Subtotal|Междинна сума)\s*(?:BGN|лв)?\s*([\d,.]+)',
            "tip_regex": r'(Tip|Бакшиш)[:\s]+([\d,.]+)',
            "total_regex": r'(Total|Общо)\s*(?:BGN|лв)?\s*([\d,.]+)',
            "date_regex": r'(\d{2}[./-]\d{2}[./-]\d{4})'
        }
    else: 
        return {
            "ocr_lang": "eng",
            "subtotal_regex": r'Sub\s*Total\s*USD?\$?\s*([\d.]+)',
            "tip_regex": r'Tip[:\s]+([\d.]+)',
            "total_regex": r'Total\s*USD?\$?\s*([\d.]+)',
            "date_regex": r'(\d{2}/\d{2}/\d{4})'
        }

config = set_language_config(language_choice)

image = cv2.imread('./testimages/testimage4.jpeg')

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
    cv2.imwrite("debug_contour.jpg", debug_image)

    # Apply perspective transform to "rotate" and crop the receipt.
    warped = four_point_transform(image, screen_contour.reshape(4, 2))
    
    cv2.imwrite("warped_perspective.jpg", warped)
    print("Perspective transformation completed successfully!")
else:
    print("No rectangular contour found.")


#Text from Image Scanner

import pytesseract

inverted_filtered = cv2.bitwise_not(warped)
resized = cv2.resize(inverted_filtered, None, fx=2, fy=2, interpolation=cv2.INTER_CUBIC)
custom_config = r'--oem 3 --psm 6'  # OCR Engine Mode 3, Page Segmentation Mode 6 
extracted_text = pytesseract.image_to_string(resized, config=custom_config, lang="eng")

#Extracting from text

def format_date(date_str):
    try:
        parsed_date = parser.parse(date_str, dayfirst=True)  
        return parsed_date.strftime("%d.%m.%Y") 
    except ValueError:
        return None

def extract_receipt_data(ocr_text):
    data = {}

    lines = ocr_text.strip().split("\n")
    data["Store Name"] = lines[0].strip()

    date_match = re.search(config["date_regex"], ocr_text)
    if date_match:
        data["Date & Time"] = format_date(date_match.group(1))

    subtotal_match = re.search(config["subtotal_regex"], ocr_text, re.IGNORECASE)
    tip_match = re.search(config["tip_regex"], ocr_text, re.IGNORECASE)
    total_match = re.search(config["total_regex"], ocr_text, re.IGNORECASE)

    subtotal = float(subtotal_match.group(1).replace(',', '.')) if subtotal_match else None
    tip = float(tip_match.group(1).replace(',', '.')) if tip_match else None
    total_price = float(total_match.group(1).replace(',', '.')) if total_match else None

    print(subtotal, tip, total_price)

    if tip is not None:
        if total_price == subtotal and tip > 0:
            total_price = None
    elif total_price == subtotal:
        subtotal = None

    if subtotal is None and tip is None and total_price is None:
        return json.dumps({"error": "No subtotal, tip, or total found. This might not be a valid receipt."}, indent=4)

    if subtotal is not None and total_price is not None and tip is None:
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
    data["Total Price"] = total_price

    return json.dumps(data, indent=4)

print(extract_receipt_data(extracted_text))
