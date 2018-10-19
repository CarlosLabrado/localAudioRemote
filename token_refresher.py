from time import time, sleep
from firebasetoken import FirebaseToken


class TokenRefresher:
    start_time = time()

    def main(self):
        user = FirebaseToken.get_instance().get_user()

        while True:
            FirebaseToken.get_instance().refresh_token()
            sleep(30.0 - ((time() - self.start_time) % 30.0))
