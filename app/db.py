from pymongo import MongoClient, UpdateOne
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
    perms = {"server-id": str(serverId), "settings": {"add-values": "admin", "start-polls": "admin"}}

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

# authentication for certain commands
def get_perm(serverId, perm):
    global client
    db = client["Cluster0"]
    server = db["servers"]

    # all perms initialized, no worries about getting an error of not existing
    result = server.find_one({"server-id": str(serverId)})

    return result['settings'][perm]


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

def add_stat(serverId, statName, statValue, users):
    global client
    db = client["Cluster0"]
    server = db["servers"]

    # if single user, convert to single instance
    if isinstance(users, int):
        users = [users]

    operations = []

    for user in users:
        operation = UpdateOne(
            {"server-id": str(serverId), "users.user_id": user},
            {"$set": {f"users.$.stats.{statName}": statValue}},
        )
        operations.append(operation)

    print(operations)
    x = server.bulk_write(operations)
    print(x)

def get_stats(serverId, userIds):
    global client
    db = client["Cluster0"]
    server = db["servers"]

    result = server.find_one({"server-id": str(serverId), "users.user_id": {"$in": userIds}}, {"_id": 0, "users.$": 1})
    return result

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
