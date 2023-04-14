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

def extract_and_save_faces(dir_path, file_name):
    print("extract_and_save_faces")
    vc = cv2.VideoCapture(f'{dir_path}/{file_name}')

    count = 0
    max_count = 6

    while (vc.isOpened()):
        ret, frame = vc.read()

        if not ret or count == max_count:
            break

        # BGR => Blue Green Red
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        detected_faces = face_recognition.face_locations(frame_rgb)

        if len(detected_faces):
            for detected_face in detected_faces:
                top, right, bottom, left = detected_face
                cv2.rectangle(frame, (left, top), (right, bottom), (255, 0, 0), 2)
                
            cv2.imwrite(f'{dir_path}/{count}.jpg', frame)
        count += 1

    # close the video capture
    cv2.destroyAllWindows()
    vc.release()

    os.remove(f'{dir_path}/{file_name}')
    return count == max_count
