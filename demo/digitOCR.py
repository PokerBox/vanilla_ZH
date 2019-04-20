try:
    from PIL import Image
except ImportError:
    import Image
import pytesseract
import cv2
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files (x86)\Tesseract-OCR\tesseract.exe"
# Get bounding box estimates
print(pytesseract.image_to_boxes(Image.open('test.jpg')), lang='chi_sim')
#cv2.rectangle(frame, p1, p2, (255, 0, 0), 2, 1)