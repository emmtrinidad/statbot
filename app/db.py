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

def add_perms(serverId):
    global client
    db = client["Cluster0"]

    server = db[str(serverId)]
    perms = [{"modify-values": "admin"}, {"add-values": "admin"}, {"start-polls": "admin"}]

    x = server.insert_many(perms)
    return x.inserted_ids

def add_user(serverId, users):
    """
    adds a single user or a list of users to the assigned server in MongoDB.

    Args:
        server_id (str): The ID of the server.
        users (int | list[int]): A single user ID or a list of user IDs to add.

    Returns:
        list[ObjectId]: List of inserted document IDs.
    """

    global client
    db = client["Cluster0"]

    server = db[str(serverId)]

    # if single user, convert to single instance
    if isinstance(users, int):
        users = [users]

    # format all users for insertion, except for the bot
    new_users = [{"userId": user.id} for user in users if user.id != 1307154758397726830]

    x = server.insert_many(new_users)
    return x.inserted_ids

def delete_after_kick(serverId):
    global client
    db = client["Cluster0"]

    # drop server collection from db
    server = db[str(serverId)]
    server.drop()
    print("kicked from server, deleted collection " + str(serverId))


def add_poll_channel(serverId, channelId):

    global client

    db = client["Cluster0"]
    server = db[str(serverId)]

    # create a new document with "pollChannelId" name
    poll = {"poll_channel": channelId}

    x = server.insert_one(poll)
    return x.inserted_id
