# IMPORTS
from app.constants import booksCollection,borrowsCollection,tokenCollection # import required collections
from pymongo.errors import ConnectionFailure,DuplicateKeyError # Pymongo errors
from datetime import datetime,timedelta # Datetime handling functions
from re import compile,IGNORECASE # Regex handlers

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
		# find the required book and return the data
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
	# create a empty dict to store the final mongoDB filter generated
	finalFilter = {}
	# if the filter is passed we convert it into a mongodb thing else we dont
	if bookFilter:
		# if the filter passed has an entry for the title search we create a regex that matches the string passed 
		# with all the titles and with the string being anywhere in the title text
		# ie .*<str here>.*
		if bookFilter['titleSearchBox']:
			finalFilter['Name'] = {"$regex":compile(".*"+bookFilter['titleSearchBox']+".*",IGNORECASE)}
		# if the filter passed has an entry for the author search we create a regex that matches the string passed 
		# with all the authors and with the string being anywhere in the title text
		# ie .*<str here>.*
		if bookFilter['authorSearchBox']:
			finalFilter['Author'] = {"$regex":compile(".*"+bookFilter['authorSearchBox']+".*",IGNORECASE)}
		# If the filter passed has a value for the department ( ie anything exceptt --- , cuz --- is empty in our case) then we add that to the dict
		if bookFilter['deptSelect']!="---":
			finalFilter['Department'] = bookFilter['deptSelect']
		# If the filter passed has a value for the year ( ie anything exceptt --- , cuz --- is empty in our case) then we add that to the dict
		if bookFilter['yearSelect']!='---':
			finalFilter['Year'] = int(bookFilter['yearSelect'].split(" ")[1])
		# Check if the InStock filter is on when its being passed, if it is then we check if the stock is not equal to 0
		if "stockCheckBox" in bookFilter:
			finalFilter['Stock'] = {"$ne":0}

	try:
		# use the given filter and fetch the books in the collection
		bookDataList = list(booksCollection.find(finalFilter,{"Author":1,"ImageUrl":1,"Description":1,"Name":1}))
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
		"BookName":book_name,
		"BorrowedOn":datetime.now(),
		"DueDate":(datetime.now() + timedelta(days=10)),
		"ReturnedOn":None,
		"User":tokenObj['_id'],
		"BookID":book_id
	}
	# find if the book is in stock before inserting the borrow data into the database
	book_stock = booksCollection.find_one({"_id":book_id},{"Stock":1})
	# if not in stock throw an error
	if book_stock['Stock']<=0:
		return {'status':False,'message':"Book is out Stock"}
	# if in stock then update the count of that book and insert the borrow obj
	booksCollection.update_one({"_id":book_id},{"$inc":{"Stock":-1}})
	# insert the object
	try:
		borrowsCollection.insert_one(borrowObj)
	except ConnectionFailure:
		booksCollection.update_one({"_id":book_id},{"$inc":{"Stock":1}})
		return {'status':False,'message':"Unable to connect to database"}
	
	return {'status':True,'message':"Book reserved"}


# List all borrowed books
def listAllBorrowedBooks(bookFilter = {}):
	'''
		Function to list all the borrowed books by every student in the system
		accepts an optional filter to narrow down the results by different params
		params:
			bookFilter : <dict> The dict containing the fields and the values to filter the results by

		returns:
			<dict> {status:True,message:<List(dict) : List of the borrowed book objs>} if success
					{status:False,message:Error message} if failure
	'''
	# create a empty dict to store the final mongoDB filter generated
	finalFilter = {}
	# if the filter is passed we convert it into a mongodb thing else we dont
	if bookFilter:
		# if the filter passed has an entry for the title search we create a regex that matches the string passed 
		# with all the titles and with the string being anywhere in the title text
		# ie .*<str here>.*
		if bookFilter['titleSearchBox']:
			finalFilter['BookName'] = {"$regex":compile(".*"+bookFilter['titleSearchBox']+".*",IGNORECASE)}
		# if the filter passed has an entry for the author search we create a regex that matches the string passed 
		# with all the authors and with the string being anywhere in the title text
		# ie .*<str here>.*
		if bookFilter['usnSearchBox']:
			finalFilter['User'] = {"$regex":compile(".*"+bookFilter['usnSearchBox']+".*",IGNORECASE)}
		# If a value is selected for the borrow Date from field them we need to convert the borrow date from and borrow date to together 
		# into a mongodb filter with $lt and $gt based on timestamps
		# check if either one of the borrow dates are given
		if bookFilter['borrowDateFrom'] or bookFilter["borrowDateTo"]:
			finalFilter['BorrowedOn'] = {}
			# If both are present we combine them,
			# if only the from is there we get all the books from that date and untill today
			# if only the to is given we get all the books untill that date
			if bookFilter['borrowDateFrom']: 
				finalFilter['BorrowedOn']["$gte"]=datetime.strptime(bookFilter['borrowDateFrom'],"%Y-%m-%d")
			if bookFilter['borrowDateTo']:
				finalFilter['BorrowedOn']["$lte"]=datetime.strptime(bookFilter['borrowDateTo'],"%Y-%m-%d")
		# If a value is selected for the borrow Date from field them we need to convert the due date from and due date to together 
		# into a mongodb filter with $lt and $gt based on timestamps
		# check if either one of the due dates are given
		if bookFilter['dueDateFrom'] or bookFilter["dueDateTo"]:
			finalFilter['DueDate'] = {}
			# If both are present we combine them,
			# if only the from is there we get all the books from that date and untill today
			# if only the to is given we get all the books untill that date
			if bookFilter['dueDateFrom']: 
				finalFilter['DueDate']["$gte"]=datetime.strptime(bookFilter['dueDateFrom'],"%Y-%m-%d")
			if bookFilter['dueDateTo']:
				finalFilter['DueDate']["$lte"]=datetime.strptime(bookFilter['dueDateTo'],"%Y-%m-%d")

	try:
		# Lookup query to fetch the borrows
		# This query is simlar to the SQL JOINs , like:
		# select * from borrows,users where borrows.User = users._id;
		borrowDataList = borrowsCollection.aggregate([
			# lookup the user data from the user collection and store in the UserData field
			{
				"$lookup": {
					"from": "users",
					"localField": "User", 
					"foreignField": "_id",
					"as": "UserData"
				}
			},
			# If we just had only the lookup and nothing further would get an array with one element for the key of the field UserData
			# This is used to change that behavior , this will merge that one doc in the array into the main doc (except _id because it already exists)
			{
				"$replaceRoot": { "newRoot": { "$mergeObjects": [ { "$arrayElemAt": [ "$UserData", 0 ] }, "$$ROOT" ] } }
			},
			# The below will then remove the UserData field from being sent back
			{ "$project": { "UserData": 0 } },
			# At last this is used to filter the results based on the user filters
			{"$match":finalFilter}
		])
	except ConnectionFailure:
		return {'status':False,'message':"Unable to Connect to database"}
	return {'status':True,'message':borrowDataList}