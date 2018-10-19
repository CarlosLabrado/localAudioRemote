from time import time, sleep
from firebasetoken import FirebaseToken


class TokenRefresher:
    start_time = time()

    def main(self):
        while True:
            print("tick")
            user = FirebaseToken.get_instance().get_user()
            user.refresh_token()
            sleep(30.0 - ((time() - self.start_time) % 30.0))
