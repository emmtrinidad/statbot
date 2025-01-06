from pymongo import UpdateOne
from .init import get_client


def add_stat(serverId, statName, statValue, users, removeFlag):
    db = get_client()["Cluster0"]
    server = db["servers"]

    # if single user, convert to single instance
    if isinstance(users, int):
        users = [users]

    operations = []
    operator = "$set"

    # change to unset for removing stat so i don't have to do the same thing again
    if removeFlag: 
        statValue = ""
        operator = "$unset"


    for user in users:
        operation = UpdateOne(
            {"server-id": str(serverId), "users.user_id": user},
            {operator: {f"users.$.stats.{statName}": statValue}},
        )
        operations.append(operation)

    server.bulk_write(operations)

def get_stats(serverId, userIds):
    db = get_client()["Cluster0"]
    server = db["servers"]

    result = server.aggregate([{"$match": {"server-id": str(serverId), "users.user_id": {"$in": userIds}}}, {"$project": {"_id": 0, "users": 1}}]).next()
    print(result)
    return result
