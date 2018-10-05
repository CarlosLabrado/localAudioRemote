import zerorpc


class ZeroClient:
    # Here will be the instance stored.
    __instance = None

    c = None

    @staticmethod
    def get_instance():
        """ Static access method. """
        if ZeroClient.__instance is None:
            ZeroClient()
        return ZeroClient.__instance

    def __init__(self):
        """ Virtually private constructor. """
        if ZeroClient.__instance is None:
            ZeroClient.__instance = self
            self.c = zerorpc.Client()
            # self.c.connect("tcp://data:4242")  # "data" is the containers name
            # self.c.connect("tcp://0.0.0.0:4242")  # Test only
            self.c.connect("tcp://192.168.1.114:4242")  # Test only

    def get_client(self):
        return self.c
