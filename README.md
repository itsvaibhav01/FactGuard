# FactGuard: An AI-Powered Reality Check for Social Media

FactGuard is a cutting-edge AI solution designed to identify and expose fake news, deep fake videos, and AI-generated content on various social media platforms. It aims to serve as a reliable gatekeeper, protecting social media users from misleading and deceptive content.

## Features
- Text Analysis: Determines if a given piece of text content is real or fake.
- Image Analysis: Detects whether an image is AI-generated or authentic.
- Video Analysis: Identifies if a video is real or a deep fake.

## How to Get Started
To run FactGuard locally and create a webhook for the application, you will need to follow these steps:

### Prerequisites
- Python 3.6 or higher
- ngrok
- Flask

### Steps
1. Clone the repository and navigate to the project directory.
2. Install the required Python packages: 
    ```
    pip install -r requirements.txt
    ```
3. Run the Flask application:
    ```
    flask run
    ```
    By default, the Flask application runs on port 5000.

4. Open a new terminal window and start ngrok on the same port as your Flask application:
    ```
    ngrok http 5000
    ```
    This will expose your local server to the public internet over the port that your Flask application is running on (port 5000). 

5. Copy the HTTPS Forwarding URL from the ngrok output and use it as your webhook URL. It should look something like this: `https://<your-subdomain>.ngrok.io`.

6. Keep both the Flask and ngrok terminals running. Any incoming requests to your ngrok URL will now be forwarded to your local Flask server.

Congratulations! Your FactGuard application is up and running, and your webhook is active.
