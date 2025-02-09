import cv2 as cv
import face_recognition as fr
import os
from openpyxl import Workbook, load_workbook
from datetime import datetimeq

# Path to student images
path = 'student_images'
images = []
className = []
rollNumbers = {}

# Mapping of names to roll numbers
name_to_roll = {
    "Jafir": 3,
    "Hasib": 10,
    "Hasan": 26,
    "Rafi": 18,
    "Masrafi": 25,
    "Md.Sanzis Hasnat": 26,
    "Md.Rafshan Jani": 27
}

# Read and encode images
mylist = os.listdir(path)
for cl in mylist:
    curImg = cv.imread(f"{path}/{cl}")
    images.append(curImg)
    name = os.path.splitext(cl)[0]
    className.append(name)
    if name in name_to_roll:
        rollNumbers[name] = name_to_roll[name]

def encodingImages(images):
    encodelist = []
    for img in images:
        img = cv.cvtColor(img, cv.COLOR_BGR2RGB)
        encodings = fr.face_encodings(img)
        if encodings:
            encodelist.append(encodings[0])
    return encodelist

encodelistKnown = encodingImages(images)
print("Encoding complete")

# Excel setup
excel_file = 'attendance.xlsx'
if not os.path.exists(excel_file):
    workbook = Workbook()
    sheet = workbook.active
    sheet.append(["ID", "Name", "Date", "Time", "Roll Number", "Presence Indicator"])
    workbook.save(excel_file)

# Initialize webcam
capture = cv.VideoCapture(0)  # Use default webcam (change to 1, 2, etc., for other cameras)

if not capture.isOpened():
    print("Error: Could not open webcam.")
    exit()

id_counter = 1

while True:
    isTrue, img = capture.read()
    if not isTrue:
        print("Error: Could not read frame from webcam.")
        break

    imgS = cv.resize(img, (0, 0), None, 0.25, 0.25)
    imgS = cv.cvtColor(imgS, cv.COLOR_BGR2RGB)

    faceCurrloc = fr.face_locations(imgS)
    faceCurrEnc = fr.face_encodings(imgS, faceCurrloc)

    for encodeface, faceloc in zip(faceCurrEnc, faceCurrloc):
        matches = fr.compare_faces(encodelistKnown, encodeface)
        faceDis = fr.face_distance(encodelistKnown, encodeface)
        matchindex = faceDis.argmin()

        if matches[matchindex]:
            name = className[matchindex]
            roll_number = name_to_roll.get(name, "Unknown")
            print(f"Name: {name}, Roll Number: {roll_number}")

            # Log attendance in Excel
            now = datetime.now()
            current_date = now.strftime("%Y-%m-%d")
            current_time = now.strftime("%H:%M:%S")

            workbook = load_workbook(excel_file)
            sheet = workbook.active

            logged_today = False
            for row in sheet.iter_rows(values_only=True):
                if row[1] == name and row[2] == current_date:
                    logged_today = True
                    break

            if not logged_today:
                sheet.append([id_counter, name, current_date, current_time, roll_number, 1])
                workbook.save(excel_file)
                id_counter += 1
                print(f"Logged {name} into Excel.")

    # Display webcam feed
    cv.imshow("Webcam Feed", img)

    # Exit loop on 'q'
    if cv.waitKey(1) & 0xFF == ord('q'):
        break

capture.release()
cv.destroyAllWindows()