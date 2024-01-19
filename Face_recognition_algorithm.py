import face_recognition
import pickle
from OurData import known_images


# Load known face encodings and names
known_encodings = []
known_names = []

for image_path, person_name in known_images:
    img = face_recognition.load_image_file(image_path)
    encoding = face_recognition.face_encodings(img)[0]
    known_encodings.append(encoding)
    known_names.append(person_name)

# Save the encoded data to a text file
with open('encoded_data.txt', 'wb') as file:
    data_to_save = {'encodings': known_encodings, 'names': known_names}
    pickle.dump(data_to_save, file)
