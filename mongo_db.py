from pymongo import MongoClient
from bson import ObjectId

from model import *
import motor.motor_asyncio

DATABASE_URI = "mongodb+srv://admin:james@cluster0.ujzjm.mongodb.net/?retryWrites=true&w=majority"

client = motor.motor_asyncio.AsyncIOMotorClient(DATABASE_URI)

database = client.todoapp

user_collection = database.users
