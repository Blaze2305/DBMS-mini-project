# ALL STUDENT RELATED ROUTES GO HERE
from app import app
from flask import render_template, request

@app.route("/")
def index():
	return "HELLO WORLD"


# Create the route for a single book
@app.route("/books/<id>",methods = ['GET'])
def bookHandler(id):
	if request.method == "GET":
		bookData = {
			"_id":"e93ff411-2f27-483f-8775-d7b97e1eb42c",
			"Name" : "Book Name",
			"Author" : "Author A",
			"Book Image" : "https://edit.org/images/cat/book-covers-big-2019101610.jpg",
			"Description" : "Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.",
			"Department" : "CSE",
			"Year" : 1,
			"InStock":True,
			"Stock":10
		}
		return render_template("bookPage.html",bookData = bookData)


# Route handling a singler user
@app.route("/users/<id>",methods = ['GET'])
def userHandler(id):
	if request.method == "GET":
		userData = {
			"_id":"4NI18CS122",
			"Name":"Random Name",
			"Department": "CSE",
			"Year" : 3,
			"Section" : "B",
			"Date of Birth" : "2020-10-19",
			"Contact":9481591999,
			"PhotoUrl":"https://avataaars.io/?avatarStyle=Circle&topType=LongHairStraight&accessoriesType=Blank&hairColor=BrownDark&facialHairType=Blank&clotheType=BlazerShirt&eyeType=Default&eyebrowType=Default&mouthType=Default&skinColor=Light"
		}

		borrowData = [
			{
				"Name":"BOOK 1",
				"Borrowed On": "2020-10-10",
				"Due Date":"2020-11-10",
				"Returned On":None,
				"Dues":120,
			},
						{
				"Name":"BOOK 2",
				"Borrowed On": "2020-10-10",
				"Due Date":"2020-12-4",
				"Returned On":"2020-10-30",
				"Dues":0,
			},
			{
				"Name":"BOOK 3",
				"Borrowed On": "2020-1-1",
				"Due Date":"2020-3-4",
				"Returned On":None,
				"Dues":140,
			},
			
		]

		return render_template("profile.html",userData = userData, borrowData =  borrowData)