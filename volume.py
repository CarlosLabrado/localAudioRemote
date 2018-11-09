import os
from subprocess import check_output
import pyrebase
from requests.exceptions import HTTPError
import yaml


class Volume:
    """
    For the windows version we will use: https://www.rlatour.com/setvol/ Copyright Rob Latour 2018 - All Rights Reserved
    which is an standalone command line utility.
    """
    is_windows = True
    m_user = None
    m_user_token = None
    m_db = None
    m_clients_id_array = []
    m_client_array_index = 0

    m_clients_info_array = []
    m_current_client_id = None
    m_total_clients = 0
    m_credentials = {"email": None,
                     "password": None}

    def __init__(self):
        """
        The firebase initialization takes place in the firebase_token.py
        """

        self.get_yaml()

        config = {
            "apiKey": "AIzaSyAot3cz0QtgUFcsJm7bS9yZwlLGOdnRB4I",
            "authDomain": "audioremote-1bb18.firebaseapp.com",
            "databaseURL": "https://audioremote-1bb18.firebaseio.com",
            "projectId": "audioremote-1bb18",
            "storageBucket": "audioremote-1bb18.appspot.com",
            "messagingSenderId": "1071578356619"
        }

        firebase = pyrebase.initialize_app(config)

        # Get a reference to the auth service
        self.m_auth = firebase.auth()

        # Log the user in
        self.m_user = self.m_auth.sign_in_with_email_and_password(self.m_credentials['email'],
                                                                  self.m_credentials['password'])
        # Get the token because we need to send it on every call
        self.m_user_token = self.m_user['idToken']

        self.m_db = firebase.database()

        email = self.m_credentials['email']
        email_formatted = email.replace('.', ',')  # The firebase user can't have dots so we replace them with commas.

        val = self.m_db.child("users").child(email_formatted).get(self.m_user_token)
        device_id = val.val()['deviceUUID']

    def get_yaml(self):
        """
        Securing the credentials in a non versioned yaml.
        :return:
        """
        try:
            file_name = "credentials.yaml"

            yaml_stream = open(file_name, 'r')
            settings = yaml.load(yaml_stream)
            self.m_credentials["email"] = settings['email']
            self.m_credentials["password"] = settings['password']
        except Exception as e:
            print(e)

    def main(self):
        self.stream_listener()

    def stream_listener(self):
        def stream_handler(message):
            print(message["event"])  # put
            print(message["path"])  # /-K7yGTTEp7O549EzTYtI
            print(message["data"])  # {'title': 'Pyrebase', "body": "etc..."}
            if message["event"] == 'put':
                data = message["data"]
                self.init_device(data)
            if message["event"] == 'patch':
                data = message["data"]
                if 'volume' in data:
                    self.set_volume(new_volume=int(data['volume']))
                if 'muted' in data:
                    if data["muted"] == 'True':
                        self.mute()
                    else:
                        self.un_mute()

        try:
            my_stream = self.m_db.child("clients").child("UUID2").stream(stream_handler, self.m_user_token)
            print(my_stream)
            # print(my_stream['volume'])
        except HTTPError as e:
            print(e)
            # try to refresh token
            self.on_demand_refresher()

    def init_device(self, data):
        try:
            if data["type"] == 'win':
                self.is_windows = True
            else:
                self.is_windows = False
            if data["muted"] == 'True':
                self.mute()
            else:
                self.un_mute()
            vol = data["volume"]
            self.set_volume(new_volume=vol)
        except Exception as e:
            print(e)

    def on_demand_refresher(self):
        """
        Basically gets called when ever a token expires and fails to do an operation.
        Renews the user and the global token variable.
        :return:
        """
        self.m_user = self.m_auth.refresh(self.m_user['refreshToken'])
        self.m_user_token = self.m_user['idToken']

    def get_volume(self):
        output_volume_bytes = check_output(['osascript', '-e', 'output volume of (get volume settings)'])
        current_volume = output_volume_bytes.decode().rstrip()
        print(current_volume)
        return current_volume

    def set_volume(self, new_volume=0):
        if self.is_windows:
            os.system("setvol {0}".format(new_volume))
        else:
            os.system("osascript -e 'set volume output volume {0}'".format(new_volume))

    def volume_up(self):
        if self.is_windows:
            os.system("setvol {0}".format("+5"))
        else:
            os.system("osascript -e 'set volume output volume (output volume of (get volume settings)+5)'")

    def volume_down(self):
        if self.is_windows:
            os.system("setvol {0}".format("-5"))
        else:
            os.system("osascript -e 'set volume output volume (output volume of (get volume settings)-5)'")

    def mute(self):
        if self.is_windows:
            os.system("setvol mute")
        else:
            os.system("osascript -e 'set volume output muted TRUE'")

    def un_mute(self):
        if self.is_windows:
            os.system("setvol unmute")
        else:
            os.system("osascript -e 'set volume output muted FALSE'")


volume = Volume()
volume.main()
