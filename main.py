import os
import sys
import cv2 
import cvzone
import argparse
import face_recognition
from database import *


def registeration(name, major):
    # Connect to the Firebase database
    if not connect_to_firebase_storage():
        return 
    
    folder_path = "Images"
    name = name.lower()
    upload_profile_photo(folder_path, name, major)


def attendance():
    # Connect to the Firebase database
    if not connect_to_firebase_storage():
        return 
    
    # Get encoded known faces and ids
    known_faces, known_ids = get_face_ids()

    # Set up the webcam
    cap = cv2.VideoCapture(1)
    cap.set(3, 640) # Weight 1280
    cap.set(4, 480) # Height 720
    imgBackground = cv2.imread('Resources/background.png')

    modeType = 0    # Control which confirmation page shows
    counter = 0     # Control # of downloading data from Firebase
    id = -1         # Detected student's id

    # Importing the mode images into a list
    folderModePath = 'Resources/Modes'
    modePathList = os.listdir(folderModePath)
    imgModeList = []
    for i in range(4):
        imgModeList.append(cv2.imread(os.path.join(folderModePath, str(i) + '.png')))
    
    # Face recognition
    while True:
        success, img = cap.read() # Connect the camera

        # Preprocess the images
        imgS = cv2.resize(img, (0, 0), None, 0.25, 0.25)
        imgS = cv2.cvtColor(imgS, cv2.COLOR_BGR2RGB)

        # Detect and encode the face
        faceCurFrame = face_recognition.face_locations(imgS)
        encodeCurFrame = face_recognition.face_encodings(imgS, faceCurFrame)

        # Display the image
        imgBackground[162:162 + 480, 55:55 + 640] = img
        imgBackground[44:44 + 633, 808:808 + 414] = imgModeList[modeType]

        # Face recognition
        if faceCurFrame:
            # Locate all faces in the screen
            for encodeFace, faceLoc in zip(encodeCurFrame, faceCurFrame):
                matches = face_recognition.compare_faces(known_faces, encodeFace) 
                faceDis = face_recognition.face_distance(known_faces, encodeFace)
                matchIndex = np.argmin(faceDis)

                # Ratangle all faces
                if matches[matchIndex]:
                    y1, x2, y2, x1 = faceLoc
                    y1, x2, y2, x1 = y1 * 4, x2 * 4, y2 * 4, x1 * 4
                    bbox = 55 + x1, 162 + y1, x2 - x1, y2 - y1
                    imgBackground = cvzone.cornerRect(imgBackground, bbox, rt=0)
                    id = known_ids[matchIndex]
                    if counter == 0:
                        # cvzone.putTextRect(imgBackground, "Loading", (275, 400))
                        cv2.imshow("Face Attendance", imgBackground)
                        cv2.waitKey(1)
                        counter = 1
                        modeType = 1

            if counter != 0:
                if counter == 1:
                    # Get the Image from the storage
                    studentInfo = get_student_profile(id)
                    name = studentInfo['name'].replace(" ", "-")
                    bucket = storage.bucket()
                    blob = bucket.get_blob(f'Images/{name}.jpeg')
                    array = np.frombuffer(blob.download_as_string(), np.uint8)
                    imgStudent = cv2.imdecode(array, cv2.COLOR_BGRA2BGR)
                    imgStudent = cv2.resize(imgStudent, (216, 216))
                    # Update the attendance
                    second = update_attendance_time(str(id))
                    if second > 10 and second < 60:
                        modeType = 3
                        counter = 0
                        imgBackground[44:44 + 633, 808:808 + 414] = imgModeList[modeType]
                
                
                if modeType != 3:
                    if 10 < counter < 20:
                        modeType = 2

                    imgBackground[44:44 + 633, 808:808 + 414] = imgModeList[modeType]

                    if counter <= 10:
                        studentInfo = get_student_profile(id)
                        cv2.putText(imgBackground, str(studentInfo['major']), (1000, 550),
                                    cv2.FONT_HERSHEY_COMPLEX, 0.5, (255, 255, 255), 1)
                        cv2.putText(imgBackground, str(id), (1000, 493),
                                    cv2.FONT_HERSHEY_COMPLEX, 0.5, (255, 255, 255), 1)
                        (w, h), _ = cv2.getTextSize(studentInfo['name'], cv2.FONT_HERSHEY_COMPLEX, 1, 1)
                        offset = (414 - w) // 2
                        cv2.putText(imgBackground, str(studentInfo['name']), (808 + offset, 445),
                                    cv2.FONT_HERSHEY_COMPLEX, 1, (50, 50, 50), 1)

                        imgBackground[175:175 + 216, 909:909 + 216] = imgStudent

                    counter += 1

                    if counter >= 20:
                        counter = 0
                        modeType = 0
                        studentInfo = []
                        imgStudent = []
                        imgBackground[44:44 + 633, 808:808 + 414] = imgModeList[modeType]
        else:
            modeType = 0
            counter = 0
        cv2.imshow("Face Attendance", imgBackground)
        cv2.waitKey(1)



if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Face Recognition Attendance with Real-Time DB')
    parser.add_argument('-d', '--mode', required=True, help='Type `register` to register a new student. Type `attendance` to record students attendances')
    parser.add_argument('-m', '--major', help='Input the major of new student. Please use lower case and a dash between each word')
    parser.add_argument('-n', '--name', help='Input the name of the new student. Please use lower case and a dash between first name and last name')
    args = parser.parse_args()

    if args.mode == 'register':
        if args.major is None or args.name is None:
            sys.exit("Error: When mode is 'register', the 'major' and 'name' arguments are required.")
        print("Registering a new student")
        print("Name: ", args.name)
        print("Major: ", args.major)
        registeration(args.name, args.major)

    elif args.mode == 'attendance':
        print("Recording students attendances")
        attendance()
    else:
        sys.exit("Error: Plesase select a correct mode. You can use `-h` for more information")