import pymongo

mongo_uri = 'mongodb://mongodb:27017/'
client = pymongo.MongoClient(mongo_uri)
users_db = client['users_db']
users = users_db['users']
