from flask import Flask, render_template_string, request
from flask_socketio import SocketIO, send, join_room, leave_room
import os

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")

# Chat history file
CHAT_HISTORY_FILE = "chat_history.txt"

# HTML Template with WebRTC Support
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Vikrant's Chatroom</title>
    <style>
        body { font-family: Arial, sans-serif; text-align: center; background-color: #ACC8E5; }
        #chatbox { width: 50%; margin: auto; background: white; padding: 20px; border-radius: 10px; box-shadow: 0px 0px 10px gray; }
        ul { list-style-type: none; padding: 0; }
        li { background: #d1e7dd; padding: 10px; margin: 5px; border-radius: 5px; text-align: left; }
        input, button { padding: 10px; margin: 5px; border-radius: 5px; border: 1px solid gray; }
        button { background-color: #28a745; color: white; cursor: pointer; }
        button:hover { background-color: #218838; }
        video { width: 100%; max-width: 500px; border-radius: 10px; margin-top: 10px; }
    </style>
</head>
<body>
    <h2>Vikrant's Chatroom 🚀</h2>
    <div id="chatbox">
        <h3>Room ID: <span id="room_id"></span></h3>
        <ul id="messages"></ul>
        <input id="msg" type="text" placeholder="Type your message">
        <button onclick="sendMessage()">Send</button>
        <button onclick="pickEmoji()">😊</button>
        <button onclick="startCall()">📹 Start Video</button>
    </div>

    <video id="localVideo" autoplay muted></video>
    <video id="remoteVideo" autoplay></video>

    <script src="https://cdnjs.cloudflare.com/ajax/libs/socket.io/4.0.1/socket.io.js"></script>
    <script>
        var socket = io();
        var username = prompt("Enter your name:") || "Anonymous";
        var roomID = prompt("Enter Room ID (or leave empty to create a new room):") || Math.random().toString(36).substring(7);
        document.getElementById("room_id").innerText = roomID;
        socket.emit("join_room", roomID);

        socket.on("message", function(data) {
            var li = document.createElement("li");
            li.innerHTML = data;
            document.getElementById("messages").appendChild(li);
        });

        function sendMessage() {
            var msg = document.getElementById("msg").value;
            if (msg.trim() !== "") {
                socket.emit("message", { room: roomID, msg: "<b>" + username + ":</b> " + msg });
                document.getElementById("msg").value = "";
            }
        }

        function pickEmoji() {
            var emoji = prompt("Enter an emoji 😊:") || "";
            document.getElementById("msg").value += emoji;
        }

        document.getElementById("msg").addEventListener("keypress", function(event) {
            if (event.key === "Enter") {
                sendMessage();
            }
        });
    </script>
</body>
</html>
"""

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

@socketio.on('join_room')
def handle_join_room(data):
    join_room(data)
    send(f"<i>⚡ User has joined the room {data}!</i>", to=data)

@socketio.on('message')
def handle_message(data):
    room = data["room"]
    msg = data["msg"]
    with open(CHAT_HISTORY_FILE, "a", encoding="utf-8") as file:
        file.write(msg + "\n")
    send(msg, to=room)  # Message is only sent to the room, removing broadcast

if __name__ == '__main__':
    socketio.run(app, debug=True, port=5000) #yah se
@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

# Serve static socket.io.js file for Railway deployment
@app.route('/socket.io.js')
def serve_socketio():
    return send_from_directory('static', 'socket.io.js')

@socketio.on('join_room')
def handle_join_room(data):
    join_room(data)
    send(f"<i>⚡ User has joined the room {data}!</i>", to=data)
    
