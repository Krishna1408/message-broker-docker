#!/usr/bin/python3

import pika
import os
from flask import Flask, jsonify, request, abort

rapp = Flask(__name__)


# Welcome Page
@rapp.route('/')
def welcome():
    return "\n To get the messages sent by producer use path '/receive' \n "


# Rabbitmq
@rapp.route('/receive')
def subscriber():
    credentials = pika.PlainCredentials(username=os.environ['USER'], password=os.environ['PASS'])
    connection = pika.BlockingConnection(pika.ConnectionParameters('mq-server', credentials=credentials))
    channel = connection.channel()
    channel.queue_declare(queue='takeaway')
    method_frame, header_frame, body = channel.basic_get(queue='takeaway')
    if method_frame:
        channel.basic_ack(delivery_tag=method_frame.delivery_tag)
        ## If you message is required
        #return body.decode()
        return "{}\n".format(body.decode())
    else:
        connection.close()
        return "No message available\n"


if __name__ == '__main__':
    rapp.run(host='0.0.0.0', port=5001)
    rapp.debug = True
