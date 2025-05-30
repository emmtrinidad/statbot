from pymongo import MongoClient, UpdateOne
from dotenv import load_dotenv
import os

load_dotenv()

#instantiate client
client = None

# starts up database, returns instance of client
def startup_db():
    global client
    connectionString = os.getenv('CONNECTION_STRING')
    client = MongoClient(connectionString)
    print('connected!', flush=True)

# disconnects client
def disconnect_db():
    global client
    client.close()
    print("successfully disconnected")

# allows for other modules to get client after connected to database
def get_client():
    global client
    return client

# done on startup to add server and its permissions
def add_perms(serverId):
    global client
    db = client["Cluster0"]

    server = db["servers"]
    # adding default permissions
    perms = {"server-id": str(serverId), "settings": {"add-values": "admin", "start-polls": "admin"}}

    # add new server instance
    x = server.insert_one(perms)
    return x.inserted_id

    

def add_user(serverId, users):
    """
    adds list of users to the assigned server in MongoDB.

    Args:
        server_id (str): The ID of the server.
        users (int | list[int]): A single user ID or a list of user IDs to add.

    Returns:
        list[ObjectId]: List of inserted document IDs.
    """

    global client
    db = client["Cluster0"]

    server = db["servers"]

    # if single user, convert to single instance
    if isinstance(users, int):
        users = [users]

    # format all users for list update, except for the bot into an array
    # user ids are formatted to string due to stat modifying arguments taking multiple users as string ids
    new_users = [{"user_id": str(user.id), "stats": {}} for user in users if user.id != 1307154758397726830]

    x = server.update_one({"server-id": str(serverId)}, {"$push": {"users": {"$each": new_users}}})
    return x.upserted_id

def remove_user(serverId, user):
    global client
    db = client["Cluster0"]
    server = db["servers"]

    #delete instance of user from database
    server.update_one({"server-id": str(serverId)}, {"$pull": {"users": {"user_id": user}}})


def delete_after_kick(serverId):
    global client
    db = client["Cluster0"]

    # drop server from db
    server = db["servers"]
    server.delete_one({"server-id": str(serverId)})
    print("kicked from server, deleted document " + str(serverId))


def add_poll_channel(serverId, channelId):

    global client

    db = client["Cluster0"]
    server = db["servers"]

    # create a new document with "pollChannelId" name - will only be using a poll channel
    x = server.update_one({"server-id": str(serverId)}, {"$set": {"settings.poll_channel_id": str(channelId)}})
    return x.upserted_id

def get_poll_channel(serverId):
    
    global client

    db = client["Cluster0"]
    server = db["servers"]

    return server.find_one({"server-id": str(serverId)}, {"settings.poll-channel-id": 1})
