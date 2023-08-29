import certifi
from datetime import datetime
from os import getenv

from pymongo import MongoClient
from dotenv import load_dotenv
from nextcord import Member

ca = certifi.where()
load_dotenv()

CLUSTER = MongoClient(getenv("DB_LOCAL_TOKEN"), tlsCAFile=ca)
# CLUSTER = MongoClient(getenv("DB_USA_TOKEN"), tlsCAFile=ca)

DB = CLUSTER["samperium"]
user_collection = DB["user_collection"]


def save_data(
    user: Member,
    bot_name: str,
    rate: float,
    correct: int,
    wrong: int,
    time_now: datetime,
):
    """Save the bot related data for a user

    Args:
        user (Member): The counter details
        bot_name (str): The bot name
    """

    result = user_collection.update_one(
        {"_id": f"{user.id}"},
        {
            "$set": {
                "name": user.name,
                f"{bot_name}.correct": correct,
                f"{bot_name}.wrong": wrong,
                f"{bot_name}.rate": rate,
                f"{bot_name}.time": time_now,
            }
        },
        upsert=True,
    )
    return result.modified_count


def get_data(user: Member):
    """Get the users data

    Args:
        user (Member): The user who requested the data
    """

    result = user_collection.find_one({"_id": f"{user.id}"})
    return result


def get_prime(user: Member):
    """Get the count of the user for prime channel

    Args:
        user (Member): The user who clicked the button
    """

    result = user_collection.find_one({"_id": f"{user.id}"})
    if not isinstance(result, dict):
        return 5
    if "prime" not in result:
        return 5
    return result.get("prime", 5)


def set_prime(user: Member, count: int = 5):
    """Set the prime count of the user

    Args:
        user (Member): The user who called the interaction
    """

    result = user_collection.update_one(
        {"_id": f"{user.id}"},
        {"$set": {"prime": count}},
        True,
    )
    return result.modified_count
