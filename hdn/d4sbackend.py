from django.contrib.auth.backends import ModelBackend
from django.contrib.auth.models import User
from urllib.error import HTTPError
import urllib.request
import json as j

class D4Sbackend(object):

    def authenticate(self, token=None):
        if  token==None:
            return None
    
        print ("b-e got token")
        vreuser=""
    
        d4url = f'https://api.d4science.org/rest/2/people/profile?gcube-token={token}'
        try:
            with urllib.request.urlopen(d4url) as response:
                d4json = j.loads(response.read())
                if 'success' in d4json and d4json['success'] is True:
                    print('Token is valid')
                    vreuser=d4json['result']['username']
                    usr = User.objects.get(username= vreuser)
                    return usr
                else:
                    print('b-e User error in calling D4Science API')
                    return None

        except HTTPError:
            print('Token is not valid')
            return None
        
        def get_user(self, user_id):
            try:
                return User.objects.get(pk=user_id)
            except User.DoesNotExist:
                return None