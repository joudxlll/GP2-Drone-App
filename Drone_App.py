import tkinter as tk
import cv2
from PIL import Image, ImageTk
import pygame
import face_recognition
import time
import os
import datetime
from datetime import datetime
import firebase_admin
from firebase_admin import credentials, db
import pyrebase
from firebase_admin import credentials, storage
import shutil
import pickle
from djitellopy import tello, Tello
from OurData import known_images

# firebase connection _____________________
# keys to connect to firebase
config = {
    "apiKey": "AIzaSyD1L5kjuB6UYTPA8qjzepKQbLTV5BvNwC0",
    "authDomain": "drone-app-e0017.firebaseapp.com",
    "projectId": "drone-app-e0017",
    "storageBucket": "drone-app-e0017.appspot.com",
    "messagingSenderId": "768272782556",
    "appId": "1:768272782556:web:92e165813acee47877d019",
    "measurementId": "G-M3HHH2MSZB",
    "serviceAccount": "serviceAccountKey.json",
    "databaseURL": "https://drone-app-e0017-default-rtdb.firebaseio.com/"
}

# Initialize Firebase Admin SDK ((( storageBucket ))) for images
cred_storage = credentials.Certificate("serviceAccountKey.json")
firebase_storage = firebase_admin.initialize_app(cred_storage, {'storageBucket': 'gs://drone-app-e0017.appspot.com'}, name='storageApp')

# Initialize Firebase Admin SDK ((( databaseURL ))) for nodes
cred_database = credentials.Certificate("serviceAccountKey.json")
firebase_database = firebase_admin.initialize_app(cred_database, {'databaseURL': 'https://drone-app-e0017-default-rtdb.firebaseio.com/'}, name='databaseApp')




# Load the encoded data from the text file
with open('encoded_data.txt', 'rb') as file:
    loaded_data = pickle.load(file)

# Retrieve the encodings and names from the loaded data
known_encodings = loaded_data['encodings']
known_names = loaded_data['names']


# Define global variables
frame = None
img = None
name = None
face_name = None

person1Name = None
person2Name = None


# Initialize pygame mixer for sound
pygame.mixer.init()

# Create a Tello object
drone = tello.Tello()

# Connect to the Tello drone
drone.connect()

# Start video streaming
drone.streamon()


def update_frame():
    global frame, name, face_name
    face_name = None

    # Get video frame from Tello
    frame = drone.get_frame_read().frame
    height, width, _ = frame.shape

    # Calculate the width to maintain the original aspect ratio
    new_width = int((video_height / height) * width)
    frame = cv2.resize(frame, (new_width, video_height))

    # Perform face recognition
    recognize_known_faces()

    # Convert the modified frame to an image
    img = Image.fromarray(frame)
    img = ImageTk.PhotoImage(img)

    # Update the video_label with the new image
    video_label.config(image=img)
    video_label.image = img

    root.after(10, update_frame)


def recognize_known_faces():
    global frame, face_name
    face_name = None

    # Find face locations and face encodings in the current frame
    face_locations = face_recognition.face_locations(frame)
    frameconv = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    face_encodings = face_recognition.face_encodings(frameconv, face_locations)

    # Loop through each face found in the frame
    for (top, right, bottom, left), face_encoding in zip(face_locations, face_encodings):
        # Declare name as a global variable
        global name

        # Check if the face matches any known faces
        matches = face_recognition.compare_faces(known_encodings, face_encoding, tolerance=0.4)
        best_match_index = matches.index(True) if True in matches else None

        # If a match is found and confidence is high, set the name to the corresponding person's name
        if best_match_index is not None and matches[best_match_index] and face_recognition.face_distance([known_encodings[best_match_index]], face_encoding)[0] < 0.6:
            name = known_names[best_match_index]
            face_name = name
        else:
            name = "Unknown"

        # Draw a green rectangle around the face
        cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 0), 5)

        # Display the name below the face
        font = cv2.FONT_HERSHEY_DUPLEX
        text_size = 0.8  # Adjust the text size as needed
        text_thickness = 2  # Adjust the text thickness as needed
        text_color = (255, 255, 255)  # Text color (white)
        text_background_color = (255, 0, 0)  # Text background color (red)

        # Create a text box to get the size of the text
        (text_width, text_height), baseline = cv2.getTextSize(name, font, text_size, text_thickness)

        # Calculate the position of the text
        text_x = left + 6
        text_y = bottom + 20

        # Draw the text background
        cv2.rectangle(frame, (text_x, text_y - text_height - 5), (text_x + text_width + 5, text_y + 5),
                      text_background_color, -1)

        # Draw the text on the frame
        cv2.putText(frame, name, (text_x, text_y), font, text_size, text_color, text_thickness)





def button1_click():
    print("_______________________________________________")
    print("Button 1 is pressed")
    pygame.mixer.music.load("ButtonClick .mp3")  # Replace with the path to your second sound file
    pygame.mixer.music.play()

    #_____ delete old image _________
    folder_path = "faces"
    # Specify the first word of the image name
    first_word = "person(1)"
    # List all files in the folder
    files = os.listdir(folder_path)
    # Find files with the specified first word in the name
    matching_files = [file for file in files if file.lower().startswith(first_word.lower())]
    # Delete matching files
    for file in matching_files:
        file_path = os.path.join(folder_path, file)
        os.remove(file_path)
        print(f"Deleted: {file_path}")
    print("Deletion old image person 1 complete.")


    global ret, frame, name, face_name, person1Name, known_images

    if face_name != None and face_name != "Unknown":
        print(f"person 1 name is : {face_name}")
        person1Name = face_name

        # Save the frame if the face is recognized
        save_path = f"faces/person(1)_{face_name}_*{int(time.time())}.jpg"
        cv2.imwrite(save_path, cv2.cvtColor(frame, cv2.COLOR_RGB2BGR))
        print(f"Image saved at {save_path}")



        # Print the path of the known image for the recognized person
        for known_image_path, known_person_name in known_images:
            if known_person_name == face_name:

                print(f"Known image path for {face_name}: {known_image_path}")
                destination_folder = "faces"
                new_image_name = f"person(1)1_original_{face_name}_*{int(time.time())}"
                # Check if the original file exists
                if os.path.isfile(known_image_path):
                    # Extract file extension
                    _, extension = os.path.splitext(known_image_path)

                    # Create the destination folder if it doesn't exist
                    os.makedirs(destination_folder, exist_ok=True)

                    # Construct the new file path in the destination folder with the new name
                    new_path = os.path.join(destination_folder, f"{new_image_name}{extension}")

                    # Copy the file to the destination folder with the new name
                    shutil.copy2(known_image_path, new_path)

                else:
                    print(f"Error: The file {known_image_path} does not exist.")

                break

        print("_______________________________________________")

    else:
        print("face is unknown")
        print("_______________________________________________")
    face_name = None




def button2_click():
    print("_______________________________________________")
    print("Button 2 is pressed")
    pygame.mixer.music.load("ButtonClick .mp3")  # Replace with the path to your second sound file
    pygame.mixer.music.play()


    #_____ delete old image _________
    folder_path = "faces"
    # Specify the first word of the image name
    first_word = "person(2)"
    # List all files in the folder
    files = os.listdir(folder_path)
    # Find files with the specified first word in the name
    matching_files = [file for file in files if file.lower().startswith(first_word.lower())]
    # Delete matching files
    for file in matching_files:
        file_path = os.path.join(folder_path, file)
        os.remove(file_path)
        print(f"Deleted: {file_path}")
    print("Deletion old image person 2 complete.")



    global ret, frame, name, face_name, person2Name

    if face_name != None and face_name != "Unknown":
        print(f"person 2 name is :{face_name}")
        person2Name = face_name

        # Save the frame if the face is recognized
        save_path = f"faces/person(2)_{face_name}_*{int(time.time())}.jpg"
        cv2.imwrite(save_path, cv2.cvtColor(frame, cv2.COLOR_RGB2BGR))
        print(f"Image saved at {save_path}")


        # Print the path of the known image for the recognized person
        for known_image_path, known_person_name in known_images:
            if known_person_name == face_name:

                print(f"Known image path for {face_name}: {known_image_path}")
                destination_folder = "faces"
                new_image_name = f"person(2)2_original_{face_name}_*{int(time.time())}"
                # Check if the original file exists
                if os.path.isfile(known_image_path):
                    # Extract file extension
                    _, extension = os.path.splitext(known_image_path)

                    # Create the destination folder if it doesn't exist
                    os.makedirs(destination_folder, exist_ok=True)

                    # Construct the new file path in the destination folder with the new name
                    new_path = os.path.join(destination_folder, f"{new_image_name}{extension}")

                    # Copy the file to the destination folder with the new name
                    shutil.copy2(known_image_path, new_path)

                else:
                    print(f"Error: The file {known_image_path} does not exist.")

                break

        print("_______________________________________________")

    else:
        print("face is unknown")
        print("_______________________________________________")
    face_name = None



def button3_click():
    print("_______________________________________________")
    print("Button 3 is pressed")
    pygame.mixer.music.load("ButtonClick .mp3")  # Replace with the path to your second sound file
    pygame.mixer.music.play()

    global person1Name, person2Name

    if (person1Name != None and person1Name != "") and (person2Name != None and person2Name != ""):

        # check if image is exist or have more than 2 image
        folder_path = "faces"
        # List all files in the folder
        files = os.listdir(folder_path)
        # Filter only image files (you can customize the image file extensions)
        image_files = [file for file in files if file.lower().endswith(('.png', '.jpg', '.jpeg'))]

        # Check if there are at least two image files
        if len(image_files) == 4:
        #STEP 1  //  add to node to raeltime firebase
            # Get the current date and time
            current_datetime = datetime.now()

            # Format the date and time as desired
            formatted_date = current_datetime.strftime("%Y_%m_%d_%H:%M:%S")

            # Print the formatted date
            print(f"file ID is the date&time now >>>> {formatted_date}")
        # Reference the database using the initialized app for the database
            #ref = db.reference(app=firebase_database,url=f'https://drone-project-e4c72-default-rtdb.europe-west1.firebasedatabase.app/{formatted_date}')

        # Get a reference to the database
            ref = db.reference(f'/{formatted_date}',app=firebase_database,url=f'https://drone-app-e0017-default-rtdb.firebaseio.com/{formatted_date}')

            # Push the random number to the database
            ref.push(f"person1:{person1Name}")
            ref.push(f"person2:{person2Name}")
            print(f"done upload first person Node : {person1Name} / second person Node : {person2Name} ")
            # reset names
            person1Name = None
            person2Name = None

        # STEP 2  //  add to Images to Storage firebase
            # Initialize Firebase
            firebase = pyrebase.initialize_app(config)
            storage = firebase.storage()

            # Folder containing images
            images_folder = "faces"  # Replace with the actual path to your images folder

            # List files in the images folder
            image_files = [f for f in os.listdir(images_folder) if os.path.isfile(os.path.join(images_folder, f))]

            # Filter images based on the first word of the name
            filtered_images = [image for image in image_files if image.startswith("person")]

            # Upload filtered images to Firebase Storage in the "my_images" folder
            for image in filtered_images:
                local_image_path = os.path.join(images_folder, image) #faces/person1.png
                firebase_image_path = os.path.join(f"{formatted_date}", image)
                storage.child(firebase_image_path).put(local_image_path)

                print(f"Image '{image}' uploaded to Firebase Storage with ticket name :  {formatted_date}")

            for image_file in image_files:
                image_path = os.path.join(folder_path, image_file)
                os.remove(image_path)

        else:
            print("images folder is empty or have a lot of image please try again")
            print("_______________________________________________")
    else:
        print("names is empty please try again")
        print("_______________________________________________")



def button4_click():

    global person1Name, person2Name
    print("_______________________________________________")
    print("Button 4 is pressed")
    pygame.mixer.music.load("ButtonClick .mp3")  # Replace with the path to your second sound file
    pygame.mixer.music.play()


    person1Name = None
    person2Name = None

    folder_path = "faces"
    # List all files in the folder
    files = os.listdir(folder_path)

    # Filter only image files (you can customize the image file extensions)
    image_files = [file for file in files if file.lower().endswith(('.png', '.jpg', '.jpeg'))]

    # Check if image_files is empty and print the statement accordingly
    if not image_files:
        print("the data is empty !")
        print("_______________________________________________")
    else:
        # Delete all image files
        for image_file in image_files:
            image_path = os.path.join(folder_path, image_file)
            os.remove(image_path)

        print("All data is rest")
        print("_______________________________________________")


# Create the main window
root = tk.Tk()
root.title("Drone App")

# Calculate screen width and height
screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()

# Set window size and position
window_width = 1000
window_height = 700
x_position = (screen_width - window_width) // 2  # Center on the screen
y_position = 0  # Top of the screen

# Set window geometry
root.geometry(f"{window_width}x{window_height}+{x_position}+{y_position}")

# Load background image
background_image = Image.open("background.png")  # Replace with your image file
background_image = ImageTk.PhotoImage(background_image)

# Create a Canvas as the main container for the background image
canvas = tk.Canvas(root, width=window_width, height=window_height)
canvas.pack()

# Place the background image on the canvas
canvas.create_image(0, 0, anchor=tk.NW, image=background_image)

# Open the webcam
cap = cv2.VideoCapture(0)

# Create video label with a blue border
video_height = 400
video_label = tk.Label(root, width=700, height=video_height, bg="black", borderwidth=5, relief="solid")
video_label.place(x=138, y=50)

# Create buttons with updated styles
button1 = tk.Button(root, text="Take First Person", bg="white", activebackground="white", command=button1_click, font=("Arial", 15), fg="black", bd=2)
button2 = tk.Button(root, text="Take Second Person", bg="white", activebackground="white", command=button2_click, font=("Arial", 15), fg="black", bd=2)
button3 = tk.Button(root, text="Upload Ticket", bg="white", activebackground="white", command=button3_click, font=("Arial", 15), fg="black", bd=2)
button4 = tk.Button(root, text="Rest All Data", bg="white", activebackground="white", command=button4_click, font=("Arial", 15), fg="black", bd=2)

# Place buttons in the window
button1.place(x=115, y=600, width=180, height=50)
button2.place(x=315, y=600, width=180, height=50)
button3.place(x=515, y=600, width=180, height=50)
button4.place(x=715, y=600, width=180, height=50)

# Start the video streaming from Tello drone
update_frame()

# Start the main loop
root.mainloop()

# Stop video streaming from Tello drone
drone.streamoff()

# End the Tello connection
drone.end()
