import os


class Server:
    def __init__(self, env):
        self.app = {
            "dev": os.environ.get("APP_URL", "http://127.0.0.1:8002"),
            "rc": os.environ.get("APP_URL", "http://127.0.0.1:8002"),
        }[env]
