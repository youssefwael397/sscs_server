import os
import face_recognition
import cv2


def save_logo(logo, file_name):
    logo.save(f"static/users/logo/{file_name}")


def delete_logo(logo):
    if logo and os.path.exists(f"static/users/logo/{logo}"):
        os.remove(f"static/users/logo/{logo}")


def save_file(file, file_name, path):
    file.save(f"{path}/{file_name}")


def delete_file(file_name, path):
    if file_name and os.path.exists(f"{path}/{file_name}"):
        os.remove(f"{path}/{file_name}")

# Load the pre-trained face detection model (Haar cascade classifier)
face_cascade = cv2.CascadeClassifier('utils/haarcascade_frontalface_default.xml')

def detect_faces(frame):
    # Convert the frame to grayscale for face detection
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # Perform face detection using the cascade classifier
    faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))

    # Draw rectangles around the detected faces
    # for (x, y, w, h) in faces:
    #     cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)

    return faces


def extract_and_save_faces(dir_path, file_name):
    print("extract_and_save_faces")
    vc = cv2.VideoCapture(f'{dir_path}/{file_name}')

    count = 0
    max_count = 6

    while count < max_count:
        ret, frame = vc.read()
        print(count)

        if not ret or count == max_count:
            break

        # BGR => Blue Green Red
        frame = cv2.resize(frame, None, fx=0.5, fy=0.5)
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        # detected_faces = face_recognition.face_locations(frame_rgb)
        detected_faces = detect_faces(frame_rgb)
        print(detected_faces)
        if len(detected_faces):
            cv2.imwrite(f'{dir_path}/{count}.jpg', frame)
            count += 1
            # for detected_face in detected_faces:
                # top, right, bottom, left = detected_face
                # cv2.rectangle(frame, (left, top), (right, bottom), (255, 0, 0), 2)
                

    # close the video capture
    cv2.destroyAllWindows()
    vc.release()

    os.remove(f'{dir_path}/{file_name}')
    if count == max_count: 
        return True
    else:
        return False 
