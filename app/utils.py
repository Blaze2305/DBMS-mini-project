from app import app
from app.constants import borrowsCollection,booksCollection,usersCollection,tokenCollection
from datetime import datetime,timedelta

@app.context_processor
def utility_processor():
	def format_price(amount, currency=u'₹'):
		return u'{0}{1:.2f}'.format(currency,amount)
	

	def calculateDues(book_id,token):
		print(book_id,token)
		tokenObj = tokenCollection.find_one({"token":token})
		borrowObj = borrowsCollection.find_one({"User":tokenObj['_id'],"BookID":book_id})
		daysDue = (datetime.now().replace(minute=0,second=0,hour=0,microsecond=0)-borrowObj['Due Date'].replace(minute=0,second=0,hour=0,microsecond=0)).days
		if daysDue<=0:
			return "nil"
		else:
			return 5*daysDue

	def getCurDueDate():
		return (datetime.now()+timedelta(days=10)).strftime("%Y-%m-%d")

	def checkIfReserved(token,book_id):
		tokenObj = tokenCollection.find_one({"token":token})
		borrowObj = borrowsCollection.find_one({"User":tokenObj['_id'],"BookID":book_id})
		if not borrowObj:
			return False
		else:
			return True

	def getDueDate(token,book_id):
		tokenObj = tokenCollection.find_one({"token":token})
		borrowObj = borrowsCollection.find_one({"User":tokenObj['_id'],"BookID":book_id})
		duedate = borrowObj['Due Date'].strftime("%Y-%m-%d")
		return duedate

	def bookdue(duedate):
		duedate = duedate.replace(minute=0,second=0,hour=0,microsecond=0)
		if duedate>datetime.now():
			return True
		return False

	def formatDate(date):
		return date.strftime("%Y-%m-%d")

	return dict(format_price=format_price,get_curr_due_date=getCurDueDate,check_if_reserved=checkIfReserved,format_date=formatDate,book_due=bookdue,calculate_dues=calculateDues,get_due_date=getDueDate)


def checkIfAdmin():
	# TO DO
	pass