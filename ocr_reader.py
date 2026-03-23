# import cv2
# import pytesseract
# import re

# # set tesseract path (change if needed)
# pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"





# def extract_valid_plate(text):

#     import re

#     pattern = r'[A-Z]{2}[0-9]{2}[A-Z]{2}[0-9]{4}'

#     match = re.search(pattern, text)

#     if match:
#         return match.group()

#     return ""


# # ------------------------------
# # Clean OCR text
# # ------------------------------

# def clean_text(text):

#     text = text.upper()
#     text = text.replace(" ", "")
#     text = re.sub(r'[^A-Z0-9]', '', text)

#     return text


# # ------------------------------
# # Correct OCR mistakes
# # ------------------------------

# def correct_plate(text):

#     if len(text) < 10:
#         return text

#     text = list(text)

#     # Fix digits
#     digit_map = {
#         'O': '0',
#         'Q': '0',
#         'I': '1',
#         'L': '1',
#         'Z': '2',
#         'S': '5',
#         'B': '8',
#         'A': '4'
#     }

#     # Fix letters
#     letter_map = {
#         '0': 'O',
#         '1': 'I',
#         '2': 'Z',
#         '5': 'S',
#         '8': 'B'
#     }

#     # State letters
#     for i in [0,1]:
#         if text[i] in letter_map:
#             text[i] = letter_map[text[i]]

#     # District numbers
#     for i in [2,3]:
#         if text[i] in digit_map:
#             text[i] = digit_map[text[i]]

#     # Series letters
#     for i in [4,5]:
#         if text[i] in letter_map:
#             text[i] = letter_map[text[i]]

#     # Last numbers
#     for i in range(6,10):
#         if text[i] in digit_map:
#             text[i] = digit_map[text[i]]

#     return "".join(text)
# # ------------------------------
# # Image enhancement
# # ------------------------------

# def enhance_plate(img):

#     img = cv2.copyMakeBorder(img,10,10,10,10,cv2.BORDER_CONSTANT,value=[255,255,255])

#     gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

#     gray = cv2.bilateralFilter(gray, 11, 17, 17)

#     thresh = cv2.adaptiveThreshold(
#         gray,
#         255,
#         cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
#         cv2.THRESH_BINARY,
#         11,
#         2
#     )

#     kernel = cv2.getStructuringElement(cv2.MORPH_RECT,(3,3))
#     thresh = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel)

#     return thresh





# # ------------------------------
# # Read plate text
# # ------------------------------

# def read_plate(plate_img):

#     print("OCR FUNCTION RUNNING")

#     processed = enhance_plate(plate_img)

#     config = r'--oem 3 --psm 8 -c tessedit_char_whitelist=ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'

#     text = pytesseract.image_to_string(processed, config=config)

#     text = clean_text(text)

#     text = correct_plate(text)
    
#     text = extract_valid_plate(text)

#     match = re.search(r'[A-Z]{2}[0-9]{2}[A-Z]{2}[0-9]{4}', text)

#     if match:
#         return match.group()

#     return ""







from paddleocr import PaddleOCR
import re
import cv2

ocr = PaddleOCR(use_angle_cls=True, lang='en')



def clean_text(text):
    text = text.upper()
    text = text.replace(" ", "")
    text = re.sub(r'[^A-Z0-9]', '', text)
    return text

def extract_plate(text):

    pattern = r'[A-Z]{2}[0-9]{2}[A-Z]{2}[0-9]{4}'

    match = re.search(pattern, text)

    if match:
        return match.group()

    return text


def read_plate(plate_img):

    if plate_img is None or plate_img.size == 0:
        return ""

    # convert to gray
    plate_img = cv2.cvtColor(plate_img, cv2.COLOR_BGR2GRAY)

    result = ocr.ocr(plate_img, cls=False)

    # 🔥 FIX: handle None safely
    if result is None or len(result) == 0:
        return ""

    plate_text = ""

    for line in result:
        if line is None:
            continue

        for word in line:
            if word is None:
                continue

            plate_text += word[1][0]

    plate_text = clean_text(plate_text)
    plate_text = extract_plate(plate_text)
    
    

    return plate_text
    return plate_text