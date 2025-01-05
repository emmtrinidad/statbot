from pymongo import MongoClient
from .init import client

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
