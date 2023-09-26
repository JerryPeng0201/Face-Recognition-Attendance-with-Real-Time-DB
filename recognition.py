import cv2
import face_recognition


def face_encoder(profile_img):
    profile_img = cv2.cvtColor(profile_img, cv2.COLOR_BGR2RGB)
    encoded_face = face_recognition.face_encodings(profile_img)[0]
    return encoded_face