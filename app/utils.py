# IMPORTS
from app import app # The flask app instance
from flask import request,session,render_template,redirect,url_for # Flask utility functions
from datetime import datetime,timedelta # Time handling functions
from functools import wraps # Wrapper for writing decorators
from app.constants import borrowsCollection,booksCollection,usersCollection,tokenCollection # Application constants


# Jinja functions 
# This holds all the global functions used in the jinja rendering engine
# all the functions are exported as a dict at the end of the function
@app.context_processor
def utility_processor():
	# Function to format currency 
	def format_price(amount, currency=u'₹'):
		'''
			Function to format the given number into two decimals with the given currency value
			params:
				amount : <int> The amount of currency
				currency : <unicode str> The unicode repr of the currencys symbol, default is rupee
			returns:
				<str> The formatted currency
		'''
		return u'{0}{1:.2f}'.format(currency,amount)
	
	# Function to calculate the dues 
	def calculateDues(book_id,token=None,uid=None):
		'''
			Function to calculate the dues for a student given the student token/ USN and the book id
			We take both token and USN because if the admin makes the request when viewing a students page then we need to be able to 
			handle that as well
			params:
				book_id : <str> The books ID
				token : <str> Default None , The token of the user making the request
				uid : <str> The USN of the student to calculate the due for
			returns:
				<str> ---  if theres no due
				<int> The amount due if books are due
		'''
		# get the token from the tokencollection
		userData = tokenCollection.find_one({"token":token})
		# if the token belongs to an admin then the borrow data needs to come from the student ie students user id
		if userData['_id'] == "Admin":
			userData = {"_id":uid}
		# get the borrow object
		borrowObj = borrowsCollection.find_one({"User":userData['_id'],"BookID":book_id})
		# get the number of days overdue
		daysDue = (datetime.now().replace(minute=0,second=0,hour=0,microsecond=0)-borrowObj['DueDate'].replace(minute=0,second=0,hour=0,microsecond=0)).days
		if daysDue<=0:
			return "--"
		else:
			return format_price(5*daysDue)

	# Get the duedate from now
	def getCurDueDate():
		'''
			Function to get the future due date ie 10 days from now when borrowing now
			params:
				None
			returns:
				<str> date in yyyy-mm-dd format
		'''
		return (datetime.now()+timedelta(days=10)).strftime("%Y-%m-%d")

	# Check if the book has been reserved
	def checkIfReserved(token,book_id):
		'''
			Function to check if the book has been reserved by the current user
			params:
				token: <str> The token of the current user
				book_id : <str> The ID of the book

			returns:
				<bool> True, if reserved
						False if not reserved
		'''
		tokenObj = tokenCollection.find_one({"token":token})
		borrowObj = borrowsCollection.find_one({"User":tokenObj['_id'],"BookID":book_id})
		if not borrowObj:
			return False
		else:
			return True

	# Get the due date of the book
	def getDueDate(token,book_id,uid=None):
		'''
			Function to get the due date for the given book for the given user
			params:
				token : <str> The token of the user making the request
				book_id : <str> The ID of the book

			returns:
				<str> Date in yyyy-mm-dd format

		'''
		# get the token from the tokencollection
		tokenObj = tokenCollection.find_one({"token":token})
		# if the token belongs to an admin then the borrow data needs to come from the student ie students user id
		if tokenObj['_id'] == "Admin":
			tokenObj = {"_id":uid}
		borrowObj = borrowsCollection.find_one({"User":tokenObj['_id'],"BookID":book_id})
		duedate = borrowObj['DueDate'].strftime("%Y-%m-%d")
		return duedate


	# Checks if the book is due
	def bookdue(duedate):
		'''
			Function checks if the duedate is over
			params:
				duedate = <datetime.datetime> The datetime object of when the book was due
			params:
				<bool> True if due 
						False if not due
		'''
		duedate = duedate.replace(minute=0,second=0,hour=0,microsecond=0)
		if duedate>datetime.now():
			return True
		return False

	# Format date
	def formatDate(date):
		'''
			Function to format a date 
			params:	
				date : <datetime.datetime> Datetime object
			returns:
				<str> Date in YYYY-MM-DD format
		'''
		return date.strftime("%Y-%m-%d")

	# Check if admin
	def isAdmin(token):

		'''
			Function to check if the token of the user is an admin token or not
			params:
				token :<str> The token of the user making the request

			returns:
				<bool> True if admin
						False if not admin
		'''
		tokenData = tokenCollection.find_one({"token":token},{"token":0})
		if not tokenData:
			return False
		
		userData = usersCollection.find_one({"_id":tokenData['_id']},{"Type":1})
		if not userData:
			return False
		
		if userData['Type'] == "Student":
			return False
		else:
			return True

	# Get the number of borrowed books
	def getNumberOfBorrowedBooks(uid):
		'''
			Function to get the number of borrowed books for a particular user
			params:
				uid : <str> The User ID 
			returns:
				<int> The number of borrowed books
		'''
		borrowCount = borrowsCollection.find({"User":uid,"ReturnedOn":None}).count()
		return borrowCount

	return dict(
		is_admin=isAdmin,
		format_price=format_price,
		get_curr_due_date=getCurDueDate,
		check_if_reserved=checkIfReserved,
		format_date=formatDate,
		book_due=bookdue,
		calculate_dues=calculateDues,
		get_due_date=getDueDate,
		get_number_of_borrowed_books=getNumberOfBorrowedBooks
	)


# BELOW ARE THE CUSTOM DECORATORS WE USED TO VERIFY STUFF

# Validate if the request was made by an admin
def validateAdmin(f):
	'''
		Function to check if the request was made by an admin or not. If not admin then we reroute to the proper page
		params:
			f : <function> The function we'll wrap

		returns:
			<function> The wrapped function
	'''
	@wraps(f)
	# The inner wrapped function
	def decorated_function(*args, **kwargs):
		'''
			Function to wrap the passed function
			params:
				*args: <args> The arguments
				**kwargs : <kwargs> The Kwargs

			returns:
				<f::returnType> The Return of the passed function
		'''
		
		# If the token isnt available, redirect to login
		if "token" not in session or not session['token']:
			return redirect(url_for("loginHandler"))
		
		token = session['token']
		# If the tokendata is not present redirect to login
		tokenData = tokenCollection.find_one({"token":token},{"token":0})
		if not tokenData:
			return redirect(url_for("loginHandler"))
		
		# If the user data does not exist, redirect to login
		userData = usersCollection.find_one({"_id":tokenData['_id']},{"Type":1})
		if not userData:
			return redirect(url_for("index"))
		

		# If the type is Stuent we redirect to index ie home page
		if userData['Type'] == "Student":
			return redirect(url_for("index"))

		return f(*args, **kwargs)
	return decorated_function


# Check if the user is logged in or not
def validateLogin(f):
	'''
		Function to check if the user is logged in or not.if not logged in redirect to login
		params:
			f : <function> The function we'll wrap

		returns:
			<function> The wrapped function
	'''
	@wraps(f)
	# The inner wrapped function
	def decorated_function(*args, **kwargs):
		'''
			Function to wrap the passed function
			params:
				*args: <args> The arguments
				**kwargs : <kwargs> The Kwargs

			returns:
				<f::returnType> The Return of the passed function
		'''
		# check if the token var is in the session and if it is non null/empty
		if 'token' not in session or not session['token']:
			return redirect(url_for("loginHandler"))
		return f(*args, **kwargs)
	return decorated_function
