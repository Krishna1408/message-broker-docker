#!/usr/bin/python3
import pika
import os
from flask import Flask, jsonify, request, abort

class InvalidUsage(Exception):
    status_code = 400

    def __init__(self, message, status_code=None, payload=None):
        Exception.__init__(self)
        self.message = message
        if status_code is not None:
            self.status_code = status_code
        self.payload = payload

    def to_dict(self):
        rv = dict(self.payload or ())
        rv['message'] = self.message
        return rv

app = Flask(__name__)

#errorhandler if message is not sent in correct way
@app.errorhandler(InvalidUsage)
def handle_invalid_usage(error):
    response = jsonify(error.to_dict())
    response.status_code = error.status_code
    return response

#Welcome Page
@app.route('/')
def welcome():
    return "\n To send a message use path '/data'. \n Format to send data is 'message=test' \n "

#Rabbitmq publisher
@app.route('/data', methods=['POST'])
def sender():
    if  request.form.get('message') is None:
        raise InvalidUsage("Payload is missing parameter 'message'.", status_code=400)
    credentials = pika.PlainCredentials(username=os.environ['USER'], password=os.environ['PASS'])
    msg_rcv = request.form['message']
    connection = pika.BlockingConnection(pika.ConnectionParameters('mq-server', credentials=credentials))
    channel = connection.channel()
    #Creating Takeaway Queue and then publishing it
    channel.queue_declare(queue='takeaway')
    channel.basic_publish(exchange='',routing_key='takeaway',body=msg_rcv)
    connection.close()
    return jsonify({'Message sent': msg_rcv}), 201

if __name__ == '__main__':
    app.run(host = '0.0.0.0')
    app.debug = True
