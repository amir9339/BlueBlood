from flask import Flask, render_template, request, redirect, make_response, request, abort, send_file
from flask_socketio import SocketIO, send, emit, join_room, leave_room
import random
import time
import os
import glob

app = Flask(__name__)
socketio = SocketIO(app)

js_version = 2 # Force client to download new JS when version changed


@app.route('/')
def index():
    return render_template('index.html', title="BlueBlood")


@app.route("/api/", methods=["POST"])
def api():
    if request.method == "POST":
        text = request.form.get('text')
        socketio.emit("change_text", {"text": text}, broadcast=True)
        return "OK"


## Socket.io Config
@socketio.on('connect')
def connect():
    print("New connection")


if __name__ == "__main__":
    app.run(host="0.0.0.0", port = 8000, debug=True)
