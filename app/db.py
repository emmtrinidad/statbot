from pymongo import MongoClient
from dotenv import load_dotenv
import os

load_dotenv()

#keep this for now, try to find better way to deal with this later - is one client across multiple servers the best idea?
client = None

# starts up database, returns instance of client
def startup_db():
    global client
    connectionString = os.getenv('CONNECTION_STRING')
    client = MongoClient(connectionString)
    print('connected!')

# disconnects client
def disconnect_db():
    global client
    client.close()
    print("successfully disconnected")

