import os
import imutils
import pytesseract
import re
import json
from dateutil import parser
from imutils.perspective import four_point_transform
import numpy as np
import cv2


os.environ["QT_QPA_PLATFORM"] = "offscreen"  

#1 - English
#2 - Bulgarian
choice = 2
if choice == 1: 
    language_choice = "english"    
elif choice == 2:
    language_choice = "bulgarian"

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

image = cv2.imread('./testimages/testimage12.jpg')
if image is None:
    print("Error: Image not loaded. Check your file path.")
    exit(1)

#Preprocessing
gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
blurred = cv2.GaussianBlur(gray, (5, 5), 0)
thresh = cv2.adaptiveThreshold(
    blurred, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 11, 2)

kernel = np.ones((5, 5), np.uint8)
thresh = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel)

contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
contours = sorted(contours, key=cv2.contourArea, reverse=True)

screen_contour = None
img_area = image.shape[0] * image.shape[1]
min_area_threshold = img_area * 0.4  # 0.4 ot snimkata, tova moje da se smenq svobodno
valid_contours = []

for contour in contours:
    peri = cv2.arcLength(contour, True)
    approx = cv2.approxPolyDP(contour, 0.02 * peri, True)
    if len(approx) == 4:
        area = cv2.contourArea(approx)
        if area >= min_area_threshold:
            valid_contours.append((approx, area))

use_full_image = False

if valid_contours:
    screen_contour = max(valid_contours, key=lambda x: x[1])[0]
else:
    print(" No valid 4-point contour meeting area threshold found. Using full image for OCR.")
    use_full_image = True
    screen_contour = None

if not use_full_image and screen_contour is not None:
    debug_image = image.copy()
    cv2.drawContours(debug_image, [screen_contour], -1, (0, 255, 0), 2)
    cv2.imwrite("debug_contour.jpg", debug_image)

    warped = four_point_transform(image, screen_contour.reshape(4, 2))
    cv2.imwrite("warped_perspective.jpg", warped)
    print("Perspective transformation completed successfully!")
else:
    print("Using full image without transformation.")
    warped = image.copy()

#Debug
debug_all = image.copy()
cv2.drawContours(debug_all, contours, -1, (0, 255, 0), 2)
cv2.imwrite("debug_all_contours.jpg", debug_all)

#Process image
inverted_filtered = cv2.bitwise_not(warped)
resized = cv2.resize(inverted_filtered, None, fx=2, fy=2, interpolation=cv2.INTER_CUBIC)
custom_config = r'--oem 3 --psm 6'
extracted_text = pytesseract.image_to_string(resized, config=custom_config, lang=config["ocr_lang"])


if len(extracted_text.strip()) < 10:
    base_extracted_text = pytesseract.image_to_string(image, config=custom_config, lang=config["ocr_lang"])
    if len(base_extracted_text.strip()) < 10:
        print("Error: The image does not contain enough text information. Please retake the image.")
        extracted_text = ""
    else:
        extracted_text = base_extracted_text

# Extracted Text Cleanup

def clean_ocr_text(text, language):
    if language == "bulgarian":
        allowed_chars = "абвгдежзийклмнопрстуфхцчшщъьюяАБВГДЕЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЮЯ" \
                        "0123456789.,:/-лвBGN "  
    else:
        allowed_chars = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ" \
                        "0123456789.,:/-$%()&@ USD"  

    cleaned_text = ''.join(char for char in text if char in allowed_chars or char.isspace())
    return cleaned_text


extracted_text = clean_ocr_text(extracted_text, language_choice)


#Extracting Data from the Text 
def format_date(date_str):
    try:
        parsed_date = parser.parse(date_str, dayfirst=True)  
        return parsed_date.strftime("%d.%m.%Y") 
    except ValueError:
        return None
    


def extract_structured_data(ocr_text, language):

    lines = [line.strip() for line in ocr_text.split("\n") if line.strip()]
    items = []
    date = None
    total = None
    store_name = None

    #OCR errors
    ocr_text = ocr_text.replace("USDS", "USD").replace("USD$", "USD").replace("oad", "00")
    if language == "bulgarian":
        ocr_text = ocr_text.replace("счма", "сума")

    if language == "bulgarian":
        total_regex = r'(общо|обща сума)[:\s]*([\d,\.]+)\s*(лв|BGN)?'
        date_regex = r'(\d{2}[./-]\d{2}[./-]\d{4})'
        default_currency = "BGN"
    else:
        total_regex = r'(?<!sub\s)(?<!subtotal\s)(total|receipt total)[^\d]{0,10}([\d,\.]+)\s*(USD|\$)?'
        date_regex = r'(\d{2}/\d{2}/\d{4})'
        default_currency = "USD"

    date_match = re.search(date_regex, ocr_text)
    if date_match:
        try:
            parsed_date = parser.parse(date_match.group(1), dayfirst=True)
            date = parsed_date.strftime("%d.%m.%Y")
        except:
            date = date_match.group(1)

    total_match = re.search(total_regex, ocr_text, re.IGNORECASE)
    if total_match:
        amount = total_match.group(2).replace(",", ".")
        currency = total_match.group(3) or default_currency
        total = f"{amount} {currency}"
    elif language == "bulgarian":
        for i, line in enumerate(lines):
            line_clean = line.lower()
            if "обща сума" in line_clean or "обша сума" in line_clean:  
                next_line = lines[i+1] if i+1 < len(lines) else ""
                combined = line + " " + next_line

                match = re.search(r'([\d,.]+)\s*(лв|bgn)?', combined.lower())
                if match:
                    amount = match.group(1).replace(",", ".")
                    currency = match.group(2) or default_currency
                    total = f"{amount} {currency.upper()}"
                    break

    if not total:
        return { "error": "No total found. Please retake the image." }

    bad_keywords = ["court", "drive", "square", "ny", "cambridge", "zip", "tax", "routing", "terms", "receipt", "total", "date", "bank", "paypal", "email"]
    item_pattern = re.compile(r'^(\d+)\s+(.*?)\s+([\d,\.]+)\s+([\d,\.]+)$')

    for line in lines:
        line_lower = line.lower()
        if any(bad in line_lower for bad in bad_keywords):
            continue

        match = item_pattern.match(line)
        if match:
            qty = int(match.group(1))
            name = match.group(2).strip()
            unit_price = float(match.group(3).replace(",", "."))
            # total_price_from_line = float(match.group(4).replace(",", "."))  # Optional
            total_price = round(qty * unit_price, 2)
            if name and len(name) > 2:
                items.append({
                    "name": name,
                    "price": f"{total_price:.2f} {default_currency}"
                })

    for line in lines:
        if len(line) > 3 and not any(char.isdigit() for char in line):
            store_name = line.strip()
            break

    result = {}
    if date:
        result["receipt_date"] = date
    if store_name:
        result["store_name"] = store_name
    if items:
        result["items"] = items
    result["total"] = total

    return result

structured = extract_structured_data(extracted_text, language_choice)

print(json.dumps(structured, indent=4, ensure_ascii=False))
