import requests as req
class Authorize:
    token=''
    #Initialize connectio with rest api by username and password and then receive token for future app connections
    def __init__(self,username="none",password="none"):
        self.url = "https://<site>/webapi/rest/auth"
        self.header = ("User","Password")
        self.response = req.request(method="POST",url=self.url,auth=self.header)
        self.jsonResponse = self.response.json()
        self.token = "Bearer {}".format(self.jsonResponse["access_token"])
    
    def get_token(self):
        return self.token