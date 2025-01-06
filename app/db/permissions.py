from .init import get_client

def edit_perms(serverId, permission, scope):
    db = get_client()["Cluster0"]

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
    db = get_client()["Cluster0"]
    server = db["servers"]

    # all perms initialized, no worries about getting an error of not existing
    result = server.find_one({"server-id": str(serverId)})

    return result['settings'][perm]
