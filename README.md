# Face Recognition Attendance System with Real-Time Database
## Introduction
This project introduces a student addendance system by utilizing face recognition technology. It uses Google Firebase Real-Time database and Storage to store registered students' profile photos and id information. It contains two main functions: 
-   **Register a new student to the database**
    For this function, the system asks the user to provide the name and major of the new student. Then the system can generate a profile for the student in JSON format. The profile contains the following information:
    ```json
    id: {
        'name': "student's name",
        'major': "student's major",
        'register_time': "the date that the student is registered",
        'last_attendance_time': None
        'face_id': []
    }
    ```
    The `id` is a 6-digit randomly generated number. It can iteratly check if the new generated id is unique in the database. If it is, then the number will be assigned to the new student. Otherwise, generate a new one until it becomes unique. The `face_id` is calculated after reading the new student's photo. This is used to recognized student for future attendance. This profile information will be uploaded to Google Firebase Real-Time database, and the student's photo will be uploaded to Google Firebase Storage.
-   **Record a student's attendance**
    For this function, the system enables the video camera to see the student's face. If a registered student's face is recognized, the system will get the student's information and update the `last_attendance_time` from student's profile. This performance is only valid within 60 seconds. If the system keeps detecting the same face within 60 seconds, it will not update the `last_attendance_time` after the first one, and it will print `The attendance for this student has been recorded`. The system then gets student's name and major, and display them on the board. Meanwhile, it draws a green rectangle on the detected face.

## How to use it?
-   You must setup your own Firebase dataset at [here](https://firebase.google.com/) first. 

-   After setting up your database, please update the following code from `database.py`:
    ```python
    def connect_to_firebase_storage():
        try:
            cred = credentials.Certificate("PATH TO YOUR OWN CERTIFICATE FILE")
            firebase_admin.initialize_app(cred, {
                'databaseURL': "[YOUR OWN URL]",
                'storageBucket': "[YOUR OWN URL]"
            })
            print("Connection to Firebase Storage established successfully!")
            return True
        except Exception as e:
            print(f"Failed to connect to Firebase Storage: {e}")
            return False
    ```

-   To register a new student into the database, use the following command:
    ```
    $ python3 main.py -d register -m [student's name] -n [student's name]
    ```
    **Note:** The student's photo must be ready to be read and must be named as "firstname-lastname.jpeg"
-   To record a registered student's attendance, use the following command:
    ```
    $ python3 main.py -d attendance
    ```