# ALL STUDENT RELATED ROUTES GO HERE
from app import app
from flask import render_template, request,session,Response,flash
from app.db import books

@app.route("/")
def index():
	print(app.url_map)
	print(session)
	# Render the home page
	return render_template("home.html",PageTitle="Home")


# Create the route for a single book
@app.route("/books/<id>",methods = ['GET'])
def bookHandler(id):
	if request.method == "GET":
		bookData = books.getBook(id)
		if not bookData['status']:
			return Response(bookData['message'],400)
		bookData = bookData['message']
		return render_template("bookPage.html",bookData = bookData,PageTitle = "Book page")


@app.route("/books",methods = ['GET'])
def bookCatalogueHandler():
	if request.method == "GET":
		bookList = books.getAllBooks()
		if not bookList['status']:
			return Response(bookList['status'],400)
		return render_template("bookCatalouge.html",bookList= bookList['message'])

@app.route("/reserve",methods=["POST"])
def reserveHandler():
	if request.method == "POST":
		data = request.json
		print(data)
		reserveStatus = books.reserveBook(data['_id'],data['name'],session['token'])
		if not reserveStatus['status']:
			flash(reserveStatus['message'])
			return "false"
		return "true"