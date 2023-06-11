import json
import requests
import datetime

import os
import uuid
from gradio_client import Client
from dotenv import load_dotenv
load_dotenv()


class ultraChatBot():    
    def __init__(self, json):
        self.json = json
        self.dict_messages = json['data']
        self.ultraAPIUrl = os.getenv('ULTRA_API_URL')
        self.token = os.getenv('TOKEN')
        self.text_api_url = os.getenv('TEXT_API_URL')
        self.image_api_url = os.getenv('IMAGE_API_URL')

        bearer = os.getenv('BEARER')
        self.headers = {"Authorization": f"Bearer {bearer}"}

        self.video_api_url = os.getenv('VIDEO_API_URL')
        self.video_client = Client(self.video_api_url)

   
    def send_requests(self, type, data):
        url = f"{self.ultraAPIUrl}{type}?token={self.token}"
        headers = {'Content-type': 'application/json'}
        answer = requests.post(url, data=json.dumps(data), headers=headers)
        return answer.json()

    def send_message(self, chatID, text):
        data = {"to" : chatID,
                "body" : text}  
        answer = self.send_requests('messages/chat', data)
        return answer

    def send_image(self, chatID):
        data = {"to" : chatID,
                "image" : "https://file-example.s3-accelerate.amazonaws.com/images/test.jpeg"}  
        answer = self.send_requests('messages/image', data)
        return answer

    def send_video(self, chatID):
        data = {"to" : chatID,
                "video" : "https://file-example.s3-accelerate.amazonaws.com/video/test.mp4"}  
        answer = self.send_requests('messages/video', data)
        return answer

    def send_audio(self, chatID):
        data = {"to" : chatID,
                "audio" : "https://file-example.s3-accelerate.amazonaws.com/audio/2.mp3"}  
        answer = self.send_requests('messages/audio', data)
        return answer


    def send_voice(self, chatID):
        data = {"to" : chatID,
                "audio" : "https://file-example.s3-accelerate.amazonaws.com/voice/oog_example.ogg"}  
        answer = self.send_requests('messages/voice', data)
        return answer

    def send_contact(self, chatID):
        data = {"to" : chatID,
                "contact" : "14000000001@c.us"}  
        answer = self.send_requests('messages/contact', data)
        return answer


    def time(self, chatID):
        t = datetime.datetime.now()
        time = t.strftime('%Y-%m-%d %H:%M:%S')
        return self.send_message(chatID, time)


    def welcome(self,chatID, noWelcome = False):
        welcome_string = ''
        if (noWelcome == False):
            welcome_string = """Hello there! 👋 

Welcome to *Fact Guard* — An AI-Powered Reality Check for Social Media. 🕵️‍♀️

I'm here to help you distinguish between *real* and *fake* information. 🧐

You can send me any 📰 news articles or 📝 WhatsApp messages, and I'll check them for you, letting you know if they are genuine or not. 🤓

Got an image 🖼️ or video? 🎥 Share it with me! I can tell if it's an AI-generated image or a real one. 🤖 vs 🌍

Let's ensure we spread only the *truth*. 💪
"""
        else:
            welcome_string = """📢 *Please note!* 📢 
Currently, we only support *text*, 📷 *images*, and 🎥 *videos*. 
Share these media types for checking with your SnS AI Fact Checker bot. 
Thanks! 🙌"""
        return self.send_message(chatID, welcome_string)

    def query_text(self, chatID, payload):
        print('payload', payload)
        response = requests.post(self.text_api_url, headers=self.headers, json=payload)
        output = response.json()
        print('output: ', output)
         try:
            error = output['error']
            wait_msg = """⏰ *Hang on!* ⏰ 
Model was sleeping 💤. 
Ready in *20 seconds*. Please resend then. 
Thanks! 😊"""
            return self.send_message(chatID, wait_msg)  
        except:
            pass
            
        label = output[0][0]['label']
        score = output[0][0]['score']

        if score < 0.6:
            label = "NOT SURE"

        res_msg = ""

        if label == "Fake":
            res_msg = """⚠️ *Attention!* ⚠️ 
Likely 🚫 *fake* 🚫 info. 
Always 🕵️‍♀️ verify before sharing. 
Stay safe!"""

        if label == "Real":
            res_msg = """🟢 *Good news!* 🟢 
The info you sent is likely *real* ✅. 
Keep sharing verified content! 📚"""

        if label == "NOT SURE":
            res_msg = """🟡 *Heads up!* 🟡 
Info you sent is **unclear** ⚖️. 
Always double-check 🕵️‍♀️ from other sources."""
            
        self.send_message(chatID, res_msg)


    def download_image(self, url, save_dir='images', video=False):
        response = requests.get(url, stream=True)

        # Check if the request was successful
        if response.status_code == 200:
            # Create the directory if it doesn't exist
            if not os.path.exists(save_dir):
                os.makedirs(save_dir)

            # Generate a unique filename
            filename = str(uuid.uuid4()) 
            if video:
                filename = filename + '.mp4'
            else:
                filename = filename + '.jpg'

            save_path = os.path.join(save_dir, filename)

            # Open the file in write and binary mode and write the content to it
            with open(save_path, 'wb') as file:
                for chunk in response.iter_content(1024):
                    file.write(chunk)
        else:
            print(f'Error retrieving the URL: {url}')
            return None

        # Return the location of the saved file
        return save_path

    def query_image(self, chatID, url):
        print('file url: ', url)
        filename = self.download_image(url)
        print('filename: ', filename)
        with open(filename, "rb") as f:
            data = f.read()
        response = requests.post(self.image_api_url, headers=self.headers, data=data)
        output = response.json()
        try:
            error = output['error']
            wait_msg = """⏰ *Hang on!* ⏰ 
Model was sleeping 💤. 
Ready in *20 seconds*. Please resend then. 
Thanks! 😊"""
            return self.send_message(chatID, wait_msg)  
        except:
            pass

        print('output: ', output)
        label = output[0]['label']
        score = output[0]['score']

        if score < 0.6:
            label = "NOT SURE"

        res_msg = ""
        
        if label == "artificial":
            res_msg = """⚠️ *Attention!* ⚠️ 
The image you sent appears to be 🤖 *AI-generated* 🤖 and not a real photo. 
Be aware! 🔍"""

        if label == "human":
            res_msg = """🟢 *Good news!* 🟢 
The image you sent seems to be a *real* 📷 photo. 
Keep sharing authentic content! 📚"""

        if label == "NOT SURE":
            res_msg = """🟡 *Heads up!* 🟡 
Not certain if the image you sent is *AI-generated* 🤖 or *real* 📷. 
It's always good to double-check. 🔍"""
            
        self.send_message(chatID, res_msg)  


    def query_video(self, chatID, url):
        print('url: ', url)
        filename = self.download_image(url, video=True)
        print('filename: ', filename)
        output = self.video_client.predict(filename, api_name="/predict")
        result = output[0]
        res_msg = ""
        if 'FAKE' in result:
            res_msg = """⚠️ Alert! ⚠️ 
The video 🎥 you sent appears to be a *deep fake* 🎭 and not real footage. 
Be cautious! 🔍"""

        else:
            res_msg = """🟢 Good news! 🟢
 The video 🎥 you sent seems to be *real* footage 🎬. 
 Keep sharing authentic content! 📚"""

        return self.send_message(chatID, res_msg)  


    def Processingـincomingـmessages(self):
        if self.dict_messages != []:
            message =self.dict_messages

            print('-----msg start----------')
            print(message)
            print('*****msg end************')

            if message['type'] == 'chat':

                text = message['body'].split()
                if not message['fromMe']:
                    chatID  = message['from'] 
                    if text[0].lower() == 'hi':
                        return self.welcome(chatID)
                    else:
                        query_json = {"inputs": message['body']}
                        return self.query_text(chatID, payload=query_json)

            elif message['type'] == 'image':
                chatID  = message['from'] 
                media_url = message['media']
                return self.query_image(chatID, media_url)

            elif message['type'] == 'video':
                chatID  = message['from'] 
                media_url = message['media']
                return self.query_video(chatID, media_url)

            else:
                return self.welcome(chatID, True)
