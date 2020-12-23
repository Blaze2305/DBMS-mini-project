# ALL APP CONSTANTS GO HERE
# INCLUDES THE CONSTANT VALUES , DATABASE COLLECTIONS ETC 

# IMPORTS
from os import environ # Environment variables
from pymongo import MongoClient # pymongo MongoClient 


# Create a client to connect to the mongoDB instance
client = MongoClient(environ['DBMS'])
# connect to the library database	
libraryDatabase = client['library']
# books collection
usersCollection = libraryDatabase['users']
# auth collection
authCollection = libraryDatabase['authentication']
# token collection
tokenCollection = libraryDatabase['tokens']
# borrows collection
borrowsCollection = libraryDatabase['borrows']
# books collection
booksCollection = libraryDatabase['books']