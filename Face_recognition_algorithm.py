import face_recognition
import pickle
import cv2
from OurData import known_images

# Load known face encodings and names
known_encodings = []
known_names = []

for image_path, person_name in known_images:
    img = cv2.imread(image_path)

    # Convert the image to RGB format
    img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

    # Check if any faces are found in the image
    face_locations = face_recognition.face_locations(img_rgb)
    if face_locations:
        encoding = face_recognition.face_encodings(img_rgb, face_locations)[0]
        known_encodings.append(encoding)
        known_names.append(person_name)
    else:
        print(f"No face found in {image_path}")

# Save the encoded data to a text file
with open('encoded_data.txt', 'wb') as file:
    data_to_save = {'encodings': known_encodings, 'names': known_names}
    pickle.dump(data_to_save, file)
