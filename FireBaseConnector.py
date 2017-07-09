from firebase import firebase
import json

class FireBaseConnector(object):
    def __init__(self):
        self.__FIREBASE_URL = 'https://weremind-afeb4.firebaseio.com/'
        self.__database = firebase.FirebaseApplication(self.__FIREBASE_URL, None)
        self.__WeChatUsers = 'WeChat_IDs'
        self.__Subscriptions = 'Subscriptions'
    # Public Functions
    def userExists(self, username):
        users = self.__getWeChatUsers()
        if users != None:
            for key in users:
                if users[key]['WeChat_ID'] == username:
                    return True
        return False
    def createUser(self, username, subscriptions):
        if not self.userExists(username):
            self.__database.post(self.__WeChatUsers, {'WeChat_ID': username,
                                                      'Subscription_IDs': json.dumps(subscriptions)})
            return True
        return False
    def getUserSubscriptions(self, username):
        users = self.__getWeChatUsers()
        if users != None:
            for key in users:
                if users[key]['WeChat_ID'] == username:
                    return json.loads(users[key]['Subscription_IDs'])
        return None
    def setUserSubscriptions(self, username, subscriptions):
        users = self.__getWeChatUsers()
        if users != None:
            for key in users:
                if users[key]['WeChat_ID'] == username:
                    self.__database.put(self.__WeChatUsers, data = {'WeChat_ID': username,
                                                                    'Subscription_IDs': json.dumps(subscriptions)},
                                        name = key)
            return True
        return False
    def subscriptionExists(self, sub_name):
        subscriptions = self.__getSubscriptions()
        if subscriptions != None:
            for key in subscriptions:
                if subscriptions[key]['sub_name'] == sub_name:
                    return True
        return False
    def createSubscription(self, sub_name, events):
        if not self.subscriptionExists(sub_name):
            self.__database.post(self.__Subscriptions, {'sub_name': sub_name,
                                                        'events': json.dumps(events)})
            return True
        return False
    def getEvents(self, sub_name):
        subscriptions = self.__getSubscriptions()
        if subscriptions != None:
            for key in subscriptions:
                if subscriptions[key]['sub_name'] == sub_name:
                    return json.loads(subscriptions[key]['events'])
        return None
    def setEvents(self, sub_name, events):
        subscriptions = self.__getSubscriptions()
        if subscriptions != None:
            for key in subscriptions:
                if subscriptions[key]['sub_name'] == sub_name:
                    self.__database.put(self.__Subscriptions, data = {'sub_name': sub_name,
                                                                  'events': json.dumps(events)},
                                      name = key)
                    return True
        return False
    # Private Functions
    def __getWeChatUsers(self):
        return self.__database.get(self.__WeChatUsers, None)
    def __getSubscriptions(self):
        return self.__database.get(self.__Subscriptions, None)

