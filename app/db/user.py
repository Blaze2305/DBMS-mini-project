# IMPORTS
from uuid import uuid4 # UUID gen lib
from hashlib import sha256  # Hashing library
from app.constants import tokenCollection,authCollection,borrowsCollection,usersCollection # import required collections 
from pymongo.errors import ConnectionFailure,DuplicateKeyError # Pymongo errors
from re import compile,IGNORECASE # Regex module

# login the user
def userLogin(userData):
	'''
		Function to check the users credentials and login.
		params:
			userData : <dict> Dict containing the user details ie password and usn
		
		returns:
			<dict> {status:True,message:True,token:<str:token string>} if success
					{status:False,message:Error Message} if failure
	'''
	# Check if USN and password fields are non-empty
	# if empty return the error
	if not userData['USN']:
		return {'status':False,'message':"Please Enter USN"}

	if not userData['password']:
		return {'status':False,'message':"Please Enter password"}


	# Check if the user token exists or not in the token collection
	# if it exists it means the user is already logged in
	userToken = tokenCollection.find_one({"_id":userData['USN']})
	if userToken:
		return {'status':True,'message':"User logged in","token":userToken['token']}

	try:
		# Fetch the users auth data
		userAuth = authCollection.find_one({"_id":userData['USN']})
	# handle connection failure
	except ConnectionFailure:
		return {'status':False,'message':"Could not connect to database"}
	# if the auth data does not exist , error out
	if not userAuth:
		return {'status':False,'message':"User does not exist"}
	# calculate the the hash of the given password + the salt
	passHash = sha256((userData['password']+userAuth['salt']).encode()).hexdigest()
	# if it matches , login successfully
	if passHash == userAuth['passHash']:
		token = str(uuid4())
		# insert the token and the id into the token collection
		try:
			tokenCollection.insert_one({
				"_id":userData['USN'],
				"token":token
			})
		except DuplicateKeyError:
			return {"status":True,'message':"User already logged in","token":token}
		return {"status":True,'message':"User Logged in","token":token}
	# if the hash does not match we error out
	else:
		return {'status':False,'message':"Incorrect USN or password"}


# logout the user
def userLogout(token):
	'''
		Function to logout the user and delete their tokens.
		params:
			token : <str> The user token
		
		returns:
			<dict> {status:True,message:True} if success
					{status:False,message:Error Message} if failure
	'''
	try:
		# Delete the token
		tokenCollection.delete_one({"token":token})
	except ConnectionFailure:
		return {'status':False,'message':"Unable to connect to database"}
	# return true
	return {'status':True,'message':"User logged out"}

# Get a single Users details
def getUserFromToken(token):
	'''
		Function to get the user data for a particular user based on the token
		params:
			token : <str> The Users token
		
		returns:
			<dict> {status:True,message:<dict: User data>,borrows:<List(dict): list of all borrowed books >} if success
					{status:False,message:Error Message} if failure
	'''
	try:
		# get the token object from the token collection
		tokenData = tokenCollection.find_one({"token":token})
	# handle connection failure
	except ConnectionFailure:
		return {'status':False,'message':"Unable to connnect to database"}	
	# if the token obj does not exist, then return an error
	if not tokenData:
		return {'status':False,'message':"Token does not exist, please refresh/logout and log back in"}
	# get the user associated with that token
	userId = tokenData['_id']
	try:
		# get the userdata based on that token
		userData = usersCollection.find_one({"_id":userId})
	# handle connection faliure
	except ConnectionFailure:
		return {'status':False,'message':"Unable to connnect to database"}
	# if user obj does not exist throw an error
	if not userData:
		return {'status':False,'message':"User data does not exist"}

	borrowData = getUsersBorrowedBooks(userId)
	if not borrowData['status']:
		return {'status':False,'message':"Unable to fetch user data"}
	borrowData = borrowData['message']

	# return the user object
	return {'status':True,'message':userData,'borrows':borrowData}


# Get a single Users details
def getUserFromID(uid):
	'''
		Function to get the user data for a particular user based on the user ID
		params:
			uid : <str> The Users ID
		
		returns:
			<dict> {status:True,message:<dict: User data>,borrows:<List(dict): list of all borrowed books >} if success
					{status:False,message:Error Message} if failure
	'''
	try:
		# get the userdata based on that token
		userData = usersCollection.find_one({"_id":uid})
	# handle connection faliure
	except ConnectionFailure:
		return {'status':False,'message':"Unable to connnect to database"}
	# if user obj does not exist throw an error
	if not userData:
		return {'status':False,'message':"User data does not exist"}

	borrowData = getUsersBorrowedBooks(uid)
	if not borrowData['status']:
		return {'status':False,'message':"Unable to fetch user data"}
	borrowData = borrowData['message']

	# return the user object
	return {'status':True,'message':userData,'borrows':borrowData}





# get users borrowed books
def getUsersBorrowedBooks(userId):
	'''
		Function to get the list of users borrowed books.
		params:
			userId : <str> The users ID ie their USN
		returns:
			<dict> {status:True,message:<List(dict):List of borrowed data>} if success
					{status:False,message:Error Message} if failure
	'''
	try:
		# Get the list of borrowed books and turn into a python list
		borrowList = list(borrowsCollection.find({"User" : userId}))
	# handle connection failure
	except ConnectionFailure:
		return {'status':False,'message':"Unable to connect to database"}
	# return the borrow list
	return {'status':True,'message':borrowList}



# Get list of all users
def getUsersList(userFilter={}):
	'''
		Function to get  list of all the users in the database
		params:
			userFilter : <dict> The pymongo filter to use, default is {} ie no filter

		returns:
			<dict> {status:True,message:<List(dict):List of user data>} if success
					{status:False,message:Error Message} if failure
	'''
	print(userFilter)
	# create a empty dict to store the final mongoDB filter generated
	finalFilter = {"Type":"Student"}
	# if the filter is passed we convert it into a mongodb thing else we dont
	if userFilter:
		# if the filter passed has an entry for the Name search we create a regex that matches the string passed with all 
		# the USN with the string being  anywhere in the Name
		# ie .*<str here>.*
		if userFilter['nameSearchBox']:
			finalFilter['Name'] = {"$regex":compile(".*"+userFilter['nameSearchBox']+".*",IGNORECASE)}
		# if the filter passed has an entry for the USN search we create a regex that matches the string passed
		#  with all the USN  with the string being anywhere in the USN
		# ie .*<str here>.*
		if userFilter['usnSearchBox']:
			finalFilter['_id'] = {"$regex":compile(".*"+userFilter['usnSearchBox']+".*",IGNORECASE)}
		# If the filter passed has a value for the department ( ie anything exceptt --- , cuz --- is empty in our case) then we add that to the dict
		if userFilter['deptSelect']!="---":
			finalFilter['Department'] = userFilter['deptSelect']
		# If the filter passed has a value for the year ( ie anything exceptt --- , cuz --- is empty in our case) then we add that to the dict
		if userFilter['yearSelect']!='---':
			finalFilter['Year'] = int(userFilter['yearSelect'].split(" ")[1])
		# If the filter passed has a value for the year ( ie anything exceptt --- , cuz --- is empty in our case) then we add that to the dict
		if userFilter['sectionSelect']!='---':
			finalFilter['Section'] = userFilter['sectionSelect']
	try:
		# use the given filter and fetch the users in the collection
		userDataList = list(usersCollection.find(finalFilter,{"PhotoUrl":0,"Contact":0,"DOB":0,"Type":0}))
	except ConnectionFailure:
		return {'status':False,'message':"Unable to Connect to database"}
	return {'status':True,'message':userDataList}