# IMPORTS
from app.constants import booksCollection,borrowsCollection,tokenCollection # import required collections
from pymongo.errors import ConnectionFailure,DuplicateKeyError # Pymongo errors
from datetime import datetime,timedelta

# Get a specific book
def getBook(id):
	'''
		Function to get a specific book from the database and return it
		params:
			id : <str> The ID of the book to be fetched
		returns:
			<dict> {status:True,message:<dict: The book data>} if success
					{status:False,message:Error Message} if false
	'''
	try:
		bookData = booksCollection.find_one({"_id":id})
	except ConnectionFailure:
		return {'status':False,'message':"Unable to connect to database"}
	if not bookData:
		return {'status':False,'message':"Book Unavailable"}
	return {'status':True,'message':bookData}

# Get all available books
# TO DO : sorting 
def getAllBooks():
	'''
		Function to get a list of all the available books in the database
		params:
			None
		returns:
			<dict> {status:True,message:<List(dict): List of all the books>} if success
					{status:False,message:Error Message} if failure
	'''
	try:
		bookDataList = list(booksCollection.find({},{"Author":1,"ImageUrl":1,"Description":1,"Name":1}))
	except ConnectionFailure:
		return {'status':False,'message':"Unable to Connect to database"}

	return {'status':True,'message':bookDataList}

# Reserve a book
def reserveBook(book_id,book_name,token):
	'''
		Function to reserve a book 
		params:
			book_id : <str> The book id for the book being borrowed
			book_name : <str> The book Name
			token : <str> The token of the user making the request
	'''
	tokenObj = tokenCollection.find_one({"token":token})
	if not tokenObj:
		return {'status':False,'message':"Unable to find token, please logout and log back in"}

	# generate the book borrow object
	borrowObj = {
		"Name":book_name,
		"Borrowed On":datetime.now(),
		"Due Date":(datetime.now() + timedelta(days=10)),
		"Returned On":None,
		"User":tokenObj['_id'],
		"BookID":book_id
	}
	book_stock = booksCollection.find_one({"_id":book_id},{"Stock":1})
	if book_stock['Stock']<=0:
		return {'status':False,'message':"Book is out Stock"}
	booksCollection.update_one({"_id":book_id},{"$inc":{"Stock":-1}})
	# insert the object
	try:
		borrowsCollection.insert_one(borrowObj)
	except ConnectionFailure:
		return {'status':False,'message':"Unable to connect to database"}
	
	return {'status':True,'message':"Book reserved"}