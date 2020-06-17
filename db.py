import os
import pymongo


MONGO_HOST = os.environ.get('MONGO_HOST', 'localhost')
MONGO_PORT = int(os.environ.get('MONGO_PORT', 27017))


class Database(object):
    def __init__(self, host=None, port=None):
        if not host:
            host = MONGO_HOST
        if not port:
            port = MONGO_PORT

        self.client = pymongo.MongoClient(host, port, 
                username='root',
                password='example',
                )

    def get_client(self):
        return self.client

    def get_database(self, name):
        return self.get_client()[name]
