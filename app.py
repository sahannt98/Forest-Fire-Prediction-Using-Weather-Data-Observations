from flask_socketio import SocketIO
from flask import Flask, jsonify,render_template
from flask_mqtt import Mqtt
from flask_mail import Mail, Message
import json
from model import get_prediction
import datetime
import numpy as np
import pandas as pd 
import os

app = Flask(__name__)

# MQTT Configuration
app.config['MQTT_BROKER_URL'] = 'broker.hivemq.com'
app.config['MQTT_BROKER_PORT'] = 1883
app.config['MQTT_USERNAME'] = ''
app.config['MQTT_PASSWORD'] = ''
app.config['MQTT_REFRESH_TIME'] = 1.0  # refresh time in seconds
mqtt = Mqtt(app)

# SocketIO1
socketio = SocketIO(app)

#  Mail Configuration
app.config['MAIL_SERVER']='smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USERNAME'] = ''
app.config['MAIL_PASSWORD'] = ''
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True
mail = Mail(app)

mqtt_data = ""

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/current_datetime')
def current_datetime():
    current_datetime = datetime.datetime.now()
    formatted_datetime = current_datetime.strftime('%Y-%m-%d %I:%M %p')
    
    return jsonify(current_datetime=formatted_datetime)

@mqtt.on_connect()
def handle_connect(client, userdata, flags, rc):
    mqtt.subscribe('sahan1')

@mqtt.on_message()
def handle_mqtt_message(client, userdata, message):
    global mqtt_data
    mqtt_data = message.payload.decode()
    mqtt_data = json.loads(mqtt_data) 
    mean = np.array([32.19072165, 61.80412371,  0.79175258])
    std = np.array([ 3.643907, 14.98875123, 2.08270592])
    scaled_data = np.divide(np.subtract(mqtt_data, mean), std)
    prediction = predict_fire(scaled_data)
    if(prediction == 'Fire Detected'):    
        mqtt_data.append("You're in Danger")
        with app.app_context():
            print(send_mail())     
    else:
        mqtt_data.append("You're Safe")
    print(mqtt_data)
    print(scaled_data)
    print(prediction)
    socketio.emit('mqtt_data_update', mqtt_data)

def predict_fire(array):
    new_data = pd.DataFrame({'Temperature': [array[0]], 'RH': [array[1]], 'Rain': [array[2]]})
    prediction = get_prediction().predict(new_data)
    if prediction[0] == 1:
        return "Fire Detected"
    else:
        return "No Fire Detected"

def send_mail():
    msg = Message("Fire Warning", 
                  sender='noreply@demo.com', 
                  recipients=['sahantm0@gmail.com'])
    msg.body="You are in danger. Fire condition detected."
    mail.send(msg)
    return "Email sent"
                  

if __name__ == "__main__":
    socketio.run(app, debug=True, port=5000)