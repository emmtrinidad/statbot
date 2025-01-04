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
    
# done on startup to add server and its permissions
def add_perms(serverId):
    global client
    db = client["Cluster0"]

    server = db["servers"]
    # adding default permissions
    perms = {"server-id": str(serverId), "settings": {"modify-values": "admin", "add-values": "admin", "start-polls": "admin"}}

    # add new server instance
    x = server.insert_one(perms)
    return x.inserted_id

def edit_perms(serverId, permission, scope):
    global client
    db = client["Cluster0"]

    server = db["servers"]

    # there is only one of each permission created per server
    # case of all params - all parameters are already initialized so can be set like this
    if permission == "all-perms":
        update = { "$set": {"settings." + field: scope for field in ["modify-values", "add-values", "start-polls"]}}

    # case of single param
    else:
        update = {"$set": {"settings." + permission: scope}}

    server.update_one({"server-id":str(serverId)}, update)

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
    new_users = [user.id for user in users if user.id != 1307154758397726830]

    x = server.update_one({"server-id": str(serverId)}, {"$push": {"users": {"$each": new_users}}})
    return x.upserted_id

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
