class Error(Exception):
    """Base class for exceptions in this module
    """
    pass

class MissingConfigError(Error):
    """Exception raised for missing config file error
    """
    def __init__(self):
        self.message = "config.json has not been configured properly in the root directory"
        super(MissingConfigError, self).__init__(self.message)

class FailedAccessTokenRetrievalError(Error):
    """When the access token's retrieval failed
    """
    def __init__(self, param):
        medium = ""
        if param == 'wechat':
            medium = 'WeChat'
        elif param == 'moodle':
            medium = 'Moodle'
        self.message = "{} access token retrieval failed".format(medium)
        super(FailedAccessTokenRetrievalError, self).__init__(self.message)

class CreateCustomMenuError(Error):
    """When setting the WeChat Official Account UI fails
    """
    def __init__(self):
        self.message = "WeChat Custom Menu setup failed"
        super(CreateCustomMenuError, self).__init__(self.message)
