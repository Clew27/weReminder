import urllib.request
import json
import hashlib
import os
import datetime
from ErrorModules import MissingConfigError, FailedAccessTokenRetrievalError, CreateCustomMenuError

class WeChatIntegration(object):
    """Runs WeChat offficial account tasks
    Supported functions:
     - verifyServer(self, args) Verifies the authenticity of the WeChat server
                                with the correct procedures. Check
                                http://admin.wechat.com/wiki/index.php?title=Getting_Started#Step_2._Verify_validity_of_the_URL

     - broadcastMessage(self, message)
    """

    def __init__(self):
        # WeChat Official Account Admin Platform urls
        self.getAccessTokenUrl = "https://api.wechat.com/cgi-bin/token?grant_type=client_credential&appid={}&secret={}" # AppID and AppSecret
        self.createCustomFormUrl = "https://api.wechat.com/cgi-bin/menu/create?access_token={}" # Access Token

        # Get WeChatAPI Information
        self.WeChatConfig = self.__getConfig()
        self.appID, self.appSecret, self.token = self.__getTokenInformation()
        self.accessToken = None
        self.__getAccessToken() # Retrieves a new access token for immediate use
        self.__setCustomMenu() # Sets custom menu stored in config.json


    # Public
    def verifyServer(self, args):
        """Verifies the authenticity of the Wechat server
        args: JSON array with signature, timestamp, nonce, and echostr
        return: echostr or "Failed"
        """
        hashParams = [ args['timestamp'], args['nonce'], self.token ]
        hashParams.sort()
        hashString = "".join(hashParams).encode()
        generatedSHA1 = hashlib.sha1(hashString).hexdigest()
        if args['signature'] == generatedSHA1:
            return args['echostr']
        return "Failed"

    def getToken(self):
        return self.accessToken


    # Private
    def __getConfig(self):
        """Returns WeChat Configuration
        return: WeChat configuration from config.json
        """
        configPath = os.getcwd() # Edit this later
        configPath += '/WeMinder/config.json'
        print(configPath)
        try:
            with open(configPath) as file:
                wechatConfig = json.loads(file.read())['WeChat'] # Should be in the root directory of the server
                return wechatConfig
        except:
            raise MissingConfigError()


    def __getTokenInformation(self):
        """Returns WeChat Official Account Admin Platform information
        config.json has appID, appSecret, and token
        return: appID, appSecret, token
        """
        return (self.WeChatConfig['appID'], self.WeChatConfig['appSecret'],
                self.WeChatConfig['token'])

    def __getAccessToken(self):
        """Retrieves Access Token from the WeChat Official Account Admin Platform
        """
        accessTokenUrl = self.getAccessTokenUrl.format(self.appID, self.appSecret)
        try:
            with urllib.request.urlopen(accessTokenUrl) as resp:
                self.accessToken = json.loads(resp.read().decode())
                # Set 'expires_in' variable to future date in which the token expires
                self.accessToken['expires_in'] = (datetime.datetime.now() +
                                                  datetime.timedelta(seconds=self.accessToken['expires_in']))
        except:
            raise FailedAccessTokenRetrievalError()

    def __setCustomMenu(self):
        """Sends custom menu json to the WeChat Official Account Admin Platform
        """
        try:
            if not self.__isAccessTokenExpired():
                customMenu = json.loads(self.WeChatConfig['custom-menu'])
                createCustomFormUrl = self.createCustomFormUrl.format(self.accessToken['access_token'])
                req = urllib.request.Request(createCustomFormUrl, headers={'content-type': 'application/json'},
                                             data=json.dumps(customMenu).encode())
                with urllib.request.urlopen(req) as resp:
                    errMSG = json.loads(resp.read().decode())
                    if errMSG['errmsg'] != "ok":
                        raise Exception
            else:
                raise Exception
        except:
            raise CreateCustomMenuError()

    def __isAccessTokenExpired(self):
        """Checks if the current accessToken is expired
        return: False since the token should always be valid
        """
        if datetime.datetime.now() > self.accessToken['expires_in']:
            self.__getAccessToken()
        return False
