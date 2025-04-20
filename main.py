from flask import Flask, render_template, request, jsonify
from openai import OpenAI
import speech_recognition as sr
import subprocess, os, json, base64

recognizer = sr.Recognizer()

client = OpenAI()


#context

def load_context():
    with open("context.json", "r") as file:
        return json.load(file)
    
def save_context(context):
    with open("context.json", "w") as file:
        return json.dump(context, file, indent=4)


app = Flask(__name__)

speech = "Hello, this is a test speech."

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        print(request)
        return render_template("index.html")
    return render_template("index.html")

@app.route("/upload-user-speech", methods=["POST"])
def upload_speech():
    global speech
    if 'audio' not in request.files:
        return "No audio file provided", 400
    
    audio_file = request.files['audio']
    webm_path = "temp_audio.webm"
    wav_path = "speech.wav"
    audio_file.save(webm_path)
    subprocess.run(['ffmpeg', '-y', '-i', webm_path, '-ar', '16000', wav_path], check=True)
    with sr.AudioFile(wav_path) as source:
        audio_data = recognizer.record(source)
        speech = recognizer.recognize_google(audio_data)

    os.remove(webm_path)
    os.remove(wav_path)

    context = load_context()
    context.append({
        "role": "user",
        "content": speech,
    })
    save_context(context)

    print(speech)
    return speech

system_instructions = """You are a debate assistant. When the user talks to you about some educational topic, you have to debate against it. 
                        When they take one side of the topic, you take another. Make sure it's an educational topic, otherwise do not debate on it rather just tell them, 'Sorry, I cannot debate on that topic as it is not educational.' 
                        Always stick to debating only, do not answer any other questions. """

@app.route("/ask-ai", methods=["GET"])
def ask_ai():
    context = load_context()
    response = client.chat.completions.create(
        model="gpt-4o-audio-preview",
        messages=context,
        stream=False,
        modalities=["text", "audio"],
        audio={"voice": "alloy", "format": "wav"},
    )

    context.append({
        "role": "assistant",
        "content": response.choices[0].message.audio.transcript
    })
    save_context(context)

    return jsonify({
        "text": response.choices[0].message.audio.transcript,
        "audio": response.choices[0].message.audio.data
    })

@app.route("/reset-context", methods=["GET"])
def reset_context():
    initial_context = [
        {
            "role": "system",
            "content": system_instructions
        }
    ]
    save_context(initial_context)
    return "Context has been susccessfully reset!", 200

@app.route("/get-context", methods=["GET"])
def get_context():
    return load_context()

