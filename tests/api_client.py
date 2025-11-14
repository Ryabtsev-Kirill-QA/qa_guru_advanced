from utils.base_session import BaseSession
from config import Server


class UsersApi:

    def __init__(self, env):
        self.session = BaseSession(base_url=Server(env).app)

    def get_user(self, user_id: int):
        response = self.session.get(f'/api/users/{user_id}')
        return response

    def get_users(self, **kwargs):
        response = self.session.get('/api/users/', params=kwargs)
        return response

    def create_user(self, json: dict):
        response = self.session.post('/api/users/', json=json)
        return response

    def update_user(self, user_id: int, json: dict):
        response = self.session.patch(f'/api/users/{user_id}', json=json)
        return response

    def delete_user(self, user_id: int):
        response = self.session.delete(f'/api/users/{user_id}')
        return response


class StatusApi:

    def __init__(self, env):
        self.session = BaseSession(base_url=Server(env).app)

    def get_status(self):
        response = self.session.get('/status', timeout=5)
        return response
