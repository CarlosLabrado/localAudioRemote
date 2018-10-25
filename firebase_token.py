import os
import pyrebase


class FirebaseToken:
    """
    Full firebase initialization, passes the user and database with getters.
    """
    # Here will be the instance stored.
    __instance = None

    m_auth = None
    m_user = None
    m_db = None

    @staticmethod
    def get_instance():
        """ Static access method. """
        if FirebaseToken.__instance is None:
            FirebaseToken()
        return FirebaseToken.__instance

    def __init__(self):
        """ Virtually private constructor. """
        if FirebaseToken.__instance is None:
            FirebaseToken.__instance = self

            email = os.environ['email']
            password = os.environ['password']

            config = {
                "apiKey": os.environ['apiKey'],
                "authDomain": os.environ['authDomain'],
                "databaseURL": os.environ['databaseURL'],
                "projectId": os.environ['projectId'],
                "storageBucket": os.environ['storageBucket'],
                "messagingSenderId": os.environ['messagingSenderId']
            }

            firebase = pyrebase.initialize_app(config)

            # Get a reference to the auth service
            self.m_auth = firebase.auth()

            # Log the user in
            self.m_user = self.m_auth.sign_in_with_email_and_password(email, password)

            self.m_db = firebase.database()

    def get_user(self):
        return self.m_user

    def get_db(self):
        return self.m_db

    def refresh_token(self):
        self.m_user = self.m_auth.refresh(self.m_user['refreshToken'])
        return self.get_user()

