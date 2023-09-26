import os
import cv2
import json
import random
import numpy as np
import firebase_admin
from firebase_admin import credentials
from firebase_admin import db
from firebase_admin import storage
from datetime import datetime
from recognition import *


def connect_to_firebase_db():
    try:
        cred = credentials.Certificate("serviceAccountKey.json")
        firebase_admin.initialize_app(cred, {
            'databaseURL': ''
        })
        print("Connection to Firebase Real-Time Database established successfully!")
        return True
    except Exception as e:
        print(f"Failed to connect to Firebase Real-Time Database: {e}")
        return False


def connect_to_firebase_storage():
    try:
        cred = credentials.Certificate("")
        firebase_admin.initialize_app(cred, {
            'databaseURL': '',
            'storageBucket': ''
        })
        print("Connection to Firebase Storage established successfully!")
        return True
    except Exception as e:
        print(f"Failed to connect to Firebase Storage: {e}")
        return False


def register_new_student(name: str, major: str, face_id):
    # Connect to the student id node
    ref = db.reference('Students-ids')

    # Generate an id for the new student
    id_ = str(random.randint(100000, 999999))
    while True:
        student_ref = ref.child(id_)
        student = student_ref.get()
        if not student:
            break
        id_ = random.randint(100000, 999999)
    
    # Get current date
    today = datetime.now()
    formatted_date = today.strftime('%Y-%m-%d')
    
    # Generate a new profile for the new student:
    major = major.replace("-", " ")
    student = {
        id_:{
            'name': name,
            'major': major,
            'face_id': face_id,
            'register_time': formatted_date,
            'last_attendance_time': None
        }
    }

    # Update the database
    try:
        for key, value in student.items():
            ref.child(key).set(value)
        print(f"New student {id_} has been successfully registered.")
        return id_
    except Exception as e:
        print(f"Failed to register student {id_}. Error: {e}")
        return 


def update_attendance_time(student_id):
    # Connect to the student node
    ref = db.reference(f'Students-ids/{student_id}')
    studentInfo = ref.get()
    #print(studentInfo)

    # Check if 'last_attendance_time' exists
    if studentInfo and 'last_attendance_time' not in studentInfo:
        ref.update({'last_attendance_time': datetime.now().strftime("%Y-%m-%d %H:%M:%S")})
        print(f"Updated last_attendance_time for student {student_id}.")
    elif not studentInfo:
        print(f"No student found with ID {student_id}.")
    else:
        datetimeObject = datetime.strptime(studentInfo['last_attendance_time'], "%Y-%m-%d %H:%M:%S")
        secondsElapsed = (datetime.now() - datetimeObject).total_seconds()
        if secondsElapsed > 60:
            ref.child('last_attendance_time').set(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
            print(f"Updated last_attendance_time for student {student_id}.")
        else:
            print(f"The attendance of student {student_id} has been recorded")
    return secondsElapsed


def upload_profile_photo(folder_path, student_name, major):    
    # Upload the student's profile picture to Storage
    file_name = f'{folder_path}/{student_name + ".jpeg"}'
    bucket = storage.bucket()
    blob = bucket.blob(file_name)
    blob.upload_from_filename(file_name)

    # Encode the new student's face and create a face id
    profile_img = cv2.imread(os.path.join(folder_path, student_name + ".jpeg"))
    face_id = json.dumps(face_encoder(profile_img).tolist())
    #print(face_id)

    # Generate a profile for the new student 
    name = student_name.replace("-", " ")
    student_id = register_new_student(name, major, face_id)
    print(f"The profile photo and corresponding face id for student {student_id} has been uploaded.")


def get_face_ids():    
    known_faces = []
    known_ids = []
    ref = db.reference('Students-ids')
    snapshot = ref.get()

    if snapshot:
        for key, value in snapshot.items():
            face_id = np.array(json.loads(value['face_id']))
            known_faces.append(face_id)
            known_ids.append(key)
            
    return known_faces, known_ids


def get_student_profile(student_id):
    ref = db.reference(f'Students-ids/{student_id}')
    studentInfo = ref.get()

    return studentInfo

