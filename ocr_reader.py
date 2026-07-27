import cv2
import easyocr
import re
from ai_parking import park_vehicle

reader = easyocr.Reader(['en'])

image = cv2.imread("test.jpg")

results = reader.readtext(image)

plate = ""

for result in results:
    plate += result[1] + " "

plate = plate.upper()

plate = re.sub(r'[^A-Z0-9]', '', plate)

plate = plate.replace("IND", "")
plate = plate.replace("INO", "")
plate = plate.replace("IN", "")

plate = plate.replace("O", "0")
plate = plate.replace("I", "1")

print("Final Plate :", plate)

if len(plate) >= 8:
    park_vehicle(plate)
else:
    print("Plate not detected correctly.")