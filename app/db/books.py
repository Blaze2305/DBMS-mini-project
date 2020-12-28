# IMPORTS
from app.constants import booksCollection,borrowsCollection,tokenCollection # import required collections
from pymongo.errors import ConnectionFailure,DuplicateKeyError # Pymongo errors
from datetime import datetime,timedelta
from re import compile,IGNORECASE

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
def getAllBooks(bookFilter = {}):
	'''
		Function to get a list of all the available books in the database
		params:
			bookFilter : <dict> Items to filter the search by
		returns:
			<dict> {status:True,message:<List(dict): List of all the books>} if success
					{status:False,message:Error Message} if failure
	'''
	finalFilter = {}
	print(bookFilter)
	if bookFilter:
		if bookFilter['titleSearchBox']:
			finalFilter['Name'] = {"$regex":compile(".*"+bookFilter['titleSearchBox']+".*",IGNORECASE)}
		if bookFilter['deptSelect']!="---":
			finalFilter['Department'] = bookFilter['deptSelect']
		if bookFilter['yearSelect']!='---':
			finalFilter['Year'] = int(bookFilter['yearSelect'].split(" ")[1])
		print(finalFilter)
	# bookFilter={}

	try:
		bookDataList = list(booksCollection.find(finalFilter,{"Author":1,"ImageUrl":1,"Description":1,"Name":1}))
	except ConnectionFailure:
		return {'status':False,'message':"Unable to Connect to database"}
	print(len(bookDataList))
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
		"BorrowedOn":datetime.now(),
		"DueDate":(datetime.now() + timedelta(days=10)),
		"ReturnedOn":None,
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
