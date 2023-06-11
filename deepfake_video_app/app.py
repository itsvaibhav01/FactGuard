import gradio as gr
import cv2
import numpy as np
import tensorflow as tf
import tensorflow_addons

from facenet_pytorch import MTCNN
from PIL import Image
import moviepy.editor as mp
import os
import zipfile

local_zip = "FINAL-EFFICIENTNETV2-B0.zip"
zip_ref = zipfile.ZipFile(local_zip, 'r')
zip_ref.extractall('FINAL-EFFICIENTNETV2-B0')
zip_ref.close()

# Load face detector
mtcnn = MTCNN(margin=14, keep_all=True, factor=0.7, device='cpu')

#Face Detection function, Reference: (Timesler, 2020); Source link: https://www.kaggle.com/timesler/facial-recognition-model-in-pytorch
class DetectionPipeline:
    """Pipeline class for detecting faces in the frames of a video file."""

    def __init__(self, detector, n_frames=None, batch_size=60, resize=None):
        """Constructor for DetectionPipeline class.

        Keyword Arguments:
            n_frames {int} -- Total number of frames to load. These will be evenly spaced
                throughout the video. If not specified (i.e., None), all frames will be loaded.
                (default: {None})
            batch_size {int} -- Batch size to use with MTCNN face detector. (default: {32})
            resize {float} -- Fraction by which to resize frames from original prior to face
                detection. A value less than 1 results in downsampling and a value greater than
                1 result in upsampling. (default: {None})
        """
        self.detector = detector
        self.n_frames = n_frames
        self.batch_size = batch_size
        self.resize = resize

    def __call__(self, filename):
        """Load frames from an MP4 video and detect faces.

        Arguments:
            filename {str} -- Path to video.
        """
        # Create video reader and find length
        v_cap = cv2.VideoCapture(filename)
        v_len = int(v_cap.get(cv2.CAP_PROP_FRAME_COUNT))

        # Pick 'n_frames' evenly spaced frames to sample
        if self.n_frames is None:
            sample = np.arange(0, v_len)
        else:
            sample = np.linspace(0, v_len - 1, self.n_frames).astype(int)

        # Loop through frames
        faces = []
        frames = []
        for j in range(v_len):
            success = v_cap.grab()
            if j in sample:
                # Load frame
                success, frame = v_cap.retrieve()
                if not success:
                    continue
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                # frame = Image.fromarray(frame)

                # Resize frame to desired size
                if self.resize is not None:
                    frame = frame.resize([int(d * self.resize) for d in frame.size])
                frames.append(frame)

                # When batch is full, detect faces and reset frame list
                if len(frames) % self.batch_size == 0 or j == sample[-1]:

                    boxes, probs = self.detector.detect(frames)

                    for i in range(len(frames)):

                        if boxes[i] is None:
                            faces.append(face2)     #append previous face frame if no face is detected
                            continue

                        box = boxes[i][0].astype(int)
                        frame = frames[i]
                        face = frame[box[1]:box[3], box[0]:box[2]]

                        if not face.any():
                            faces.append(face2)     #append previous face frame if no face is detected
                            continue

                        face2 = cv2.resize(face, (224, 224))

                        faces.append(face2)

                    frames = []

        v_cap.release()

        return faces


detection_pipeline = DetectionPipeline(detector=mtcnn,n_frames=20, batch_size=60)

model = tf.keras.models.load_model("FINAL-EFFICIENTNETV2-B0")


def deepfakespredict(input_video):

    faces = detection_pipeline(input_video)

    total = 0
    real = 0
    fake = 0

    for face in faces:

        face2 = face/255
        pred = model.predict(np.expand_dims(face2, axis=0))[0]
        total+=1

        pred2 = pred[1]

        if pred2 > 0.5:
          fake+=1
        else:
          real+=1

    fake_ratio = fake/total

    text =""
    text2 = "Deepfakes Confidence: " + str(fake_ratio*100) + "%"

    if fake_ratio >= 0.5:
        text = "The video is FAKE."
    else:
        text = "The video is REAL."

    face_frames = []
    
    for face in faces:
        face_frame = Image.fromarray(face.astype('uint8'), 'RGB')
        face_frames.append(face_frame)
        
    face_frames[0].save('results.gif', save_all=True, append_images=face_frames[1:], duration = 250, loop = 100 )
    clip = mp.VideoFileClip("results.gif")
    clip.write_videofile("video.mp4")

    return text, text2, "video.mp4"



title="EfficientNetV2 Deepfakes Video Detector"
description="This is a demo implementation of EfficientNetV2 Deepfakes Image Detector by using frame-by-frame detection. \
            To use it, simply upload your video, or click one of the examples to load them.\
            This demo and model represent the Final Year Project titled \"Achieving Face Swapped Deepfakes Detection Using EfficientNetV2\" by a CS undergraduate Lee Sheng Yeh. \
            The examples were extracted from Celeb-DF(V2)(Li et al, 2020) and FaceForensics++(Rossler et al., 2019). Full reference details is available in \"references.txt.\" \
            The examples are used under fair use to demo the working of the model only. If any copyright is infringed, please contact the researcher via this email: tp054565@mail.apu.edu.my.\
            "
            
examples = [              
                ['Video1-fake-1-ff.mp4'],
                ['Video6-real-1-ff.mp4'],
                ['Video3-fake-3-ff.mp4'],
                ['Video8-real-3-ff.mp4'],
                ['real-1.mp4'],
                ['fake-1.mp4'],
           ]
           
gr.Interface(deepfakespredict,
                     inputs = ["video"],
                     outputs=["text","text", gr.outputs.Video(label="Detected face sequence")],
                     title=title,
                     description=description,
                     examples=examples
                     ).launch()