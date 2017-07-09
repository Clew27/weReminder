from flask import Flask, request, redirect, render_template
from flask_restful import Resource, Api
import xml.etree.ElementTree as ET # Parse XML files returned by WeChat
import json
import urllib.parse # For urlencode
from datetime import datetime

from FireBaseConnector import FireBaseConnector # Connects to Firebase Database
from WeChatAdmin import WeChatIntegration # Handles WeChat Admin operations

app = Flask(__name__)
api = Api(app)

conn = FireBaseConnector() # Firebase operationns handler
WeChatController = WeChatIntegration() # WeChat operations handler

# User Frontend
"""Registers user into database if they don't exist"""
@app.route('/register')
def register():
    if not conn.userExists(request.args['openID']):
        conn.createUser(request.args['openID'], {})
    return redirect("http://clew99.pythonanywhere.com/subscriptions?" + urllib.parse.urlencode({'openID': request.args['openID']}))

@app.route('/subscriptions')
def getSubscriptions():
    subscriptions = conn.getUserSubscriptions(request.args['openID'])
    return str(subscriptions)

"""GET request from WeChat to authenticate the server.
See: http://admin.wechat.com/wiki/index.php?title=Getting_Started
"""
@app.route('/wechat', methods=['GET'])
def getToken():
    args = request.args
    return WeChatController.verifyServer(args)

"""Formats XML messages that the Official Account will send"""
def formatMessage(originalMessage, content):
    return """<xml>
                 <ToUserName><![CDATA[{}]]></ToUserName>
                 <FromUserName><![CDATA[{}]]></FromUserName>
                 <CreateTime>{}</CreateTime>
                 <MsgType><![CDATA[text]]></MsgType>
                 <Content><![CDATA[{}]]></Content>
             </xml>""".format(originalMessage[1].text, originalMessage[0].text,
                              int(originalMessage[2].text)+1, content)

"""Receives messages sent by the user and processes it accordingly"""
@app.route('/wechat', methods=['POST'])
def getMessage():
    receivedMessage = ET.fromstring(request.data)
    if receivedMessage[5].tag == 'EventKey': # If the message sent is an event click
        print(receivedMessage[5].text)
        if receivedMessage[5].text == 'register_key':
            return formatMessage(receivedMessage, "http://clew99.pythonanywhere.com/register?" + urllib.parse.urlencode({'openID': receivedMessage[1].text}))
        if receivedMessage[5].text == 'schedule_key':
            todo_list = []
            subscriptions = conn.getUserSubscriptions(receivedMessage[1].text)
            for subscription in subscriptions:
                events = json.loads(conn.getEvents(subscription))
                events = events['events']
                for event in events:
                    print(str(datetime.strptime(event['date'], '%B %d %Y %H:%M').date()))
                    if datetime.strptime(event['date'], '%B %d %Y %H:%M').date() == datetime.today().date():
                        todo_list.append(event)
            tasks = []
            for event in todo_list:
                tasks.append('{}: {}'.format(event['title'], event['info']))
            return formatMessage(receivedMessage, "Today's Schedule\n{}".format('\n'.join(tasks)))
        return formatMessage(receivedMessage, "Invalid Key")
    # If it's a message sent by the user
    return formatMessage(receivedMessage,
                         "You sent: {}".format(receivedMessage[4].text))



# RESTful API
"""Handles requests for a particular subscription"""
class GetEvents(Resource):
    def get(self, subscription_name):
        if conn.subscriptionExists(subscription_name):
            return json.loads(conn.getEvents(subscription_name))['events']
        return {}

"""Handles the addition of events to a particular subscription"""
class AddEvents(Resource):
    def post(self, subscription_name):
        if conn.subscriptionExists(subscription_name):
            if request.get_json() == {}:
                return {'success': False}
            events = json.loads(conn.getEvents(subscription_name))
            events['events'].append(request.get_json())
            conn.setEvents(subscription_name, json.dumps(events))
        else:
            if request.get_json() == {}:
                conn.createSubscription(subscription_name, json.dumps({'events': []}))
            else:
                conn.createSubscription(subscription_name, json.dumps({'events': [request.get_json()]}))
        return {'success': True}

class RemoveEvents(Resource):
    def post(self, subscription_name):
        if conn.subscriptionExists(subscription_name):
            if request.get_json() == {}:
                return {'success': False}
        return {'success': False}

api.add_resource(GetEvents, '/<string:subscription_name>/events')
api.add_resource(AddEvents, '/<string:subscription_name>/add')