import tkinter as tk
from tkinter import *
import cv2
from PIL import Image, ImageTk
import os
import numpy as np
from keras.models import Sequential
from keras.layers import Dense, Dropout, Flatten, Conv2D, MaxPooling2D

# Define the emotion model structure
emotion_model = Sequential()
emotion_model.add(Conv2D(32, kernel_size=(3, 3), activation='relu', input_shape=(48, 48, 1)))
emotion_model.add(Conv2D(64, kernel_size=(3, 3), activation='relu'))
emotion_model.add(MaxPooling2D(pool_size=(2, 2)))
emotion_model.add(Dropout(0.25))
emotion_model.add(Conv2D(128, kernel_size=(3, 3), activation='relu'))
emotion_model.add(MaxPooling2D(pool_size=(2, 2)))
emotion_model.add(Conv2D(128, kernel_size=(3, 3), activation='relu'))
emotion_model.add(MaxPooling2D(pool_size=(2, 2)))
emotion_model.add(Dropout(0.25))
emotion_model.add(Flatten())
emotion_model.add(Dense(1024, activation='relu'))
emotion_model.add(Dropout(0.5))
emotion_model.add(Dense(7, activation='softmax'))

# Load pre-trained model weights
emotion_model.load_weights('model.weights.h5')
cv2.ocl.setUseOpenCL(False)

# Load the Haar Cascade for face detection
facecasc = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

# Dictionary to label all emotions
emotion_dict = {0: "Angry", 1: "Disgusted", 2: "Fearful", 3: "Happy", 4: "Neutral", 5: "Sad", 6: "Surprised"}

# Path for emojis
cur_path = os.path.dirname(os.path.abspath(__file__))
emoji_dist = {
    0: cur_path + "/emojis/angry.jpg",
    1: cur_path + "/emojis/disgust.jpg",
    2: cur_path + "/emojis/fear.jpg",
    3: cur_path + "/emojis/happy.jpg",
    4: cur_path + "/emojis/neutral.jpg",
    5: cur_path + "/emojis/sad.jpg",
    6: cur_path + "/emojis/surprise.png"
}

# Global variables
show_text = [0]
use_webcam = True  # Set to True for webcam, False for video file
video_path = r'C:\Users\Hp\Downloads\Scorpio.mp4'  # Path to the video file

if use_webcam:
    cap = cv2.VideoCapture(0)
else:
    cap = cv2.VideoCapture(video_path)

if not cap.isOpened():
    print(f"Error: Couldn't open the video source")
else:
    print(f"Video source opened successfully")

def show_subject():
    global show_text, cap
    if not cap.isOpened():
        print("Can't open the video source")
        return
    
    ret, frame1 = cap.read()
    if not ret:
        print("End of video source or unable to read frame")
        cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
        return

    frame1 = cv2.resize(frame1, (600, 500))
    gray_frame = cv2.cvtColor(frame1, cv2.COLOR_BGR2GRAY)
    num_faces = facecasc.detectMultiScale(gray_frame, scaleFactor=1.3, minNeighbors=5)

    for (x, y, w, h) in num_faces:
        cv2.rectangle(frame1, (x, y-50), (x+w, y+h+10), (255, 0, 0), 2)
        roi_gray_frame = gray_frame[y:y+h, x:x+w]
        cropped_img = np.expand_dims(np.expand_dims(cv2.resize(roi_gray_frame, (48, 48)), -1), 0)
        prediction = emotion_model.predict(cropped_img)
        maxindex = int(np.argmax(prediction))
        cv2.putText(frame1, emotion_dict[maxindex], (x+20, y-60), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2, cv2.LINE_AA)
        show_text[0] = maxindex

    last_frame1 = frame1.copy()
    pic = cv2.cvtColor(last_frame1, cv2.COLOR_BGR2RGB)
    img = Image.fromarray(pic)
    imgtk = ImageTk.PhotoImage(image=img)

    lmain.imgtk = imgtk
    lmain.configure(image=imgtk)
    
    root.after(30, show_subject)  # Update every 30 ms

def show_avatar():
    global show_text
    frame2 = cv2.imread(emoji_dist[show_text[0]])
    frame2 = cv2.cvtColor(frame2, cv2.COLOR_BGR2RGB)
    img2 = Image.fromarray(frame2)
    imgtk2 = ImageTk.PhotoImage(image=img2)

    lmain2.imgtk2 = imgtk2
    lmain3.configure(text=emotion_dict[show_text[0]], font=('arial', 45, 'bold'))
    lmain2.configure(image=imgtk2)

    root.after(30, show_avatar)  # Update every 30 ms

if __name__ == '__main__':
    root = tk.Tk()
    lmain = Label(master=root, padx=50, bd=10)
    lmain2 = Label(master=root, bd=10)
    lmain3 = Label(master=root, bd=10, fg="#CDCDCD", bg='black')
    lmain.pack(side=LEFT)
    lmain.place(x=50, y=250)
    lmain3.pack()
    lmain3.place(x=960, y=250)
    lmain2.pack(side=RIGHT)
    lmain2.place(x=900, y=350)

    root.title("Photo To Emoji")
    root.geometry("1400x900+100+10")
    root['bg'] = 'black'
    exitButton = Button(root, text='Quit', fg="red", command=root.destroy, font=('arial', 25, 'bold')).pack(side=BOTTOM)

    root.after(0, show_subject)
    root.after(0, show_avatar)
    root.mainloop()

    cap.release()
    cv2.destroyAllWindows()