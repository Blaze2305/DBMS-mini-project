# ALL STUDENT RELATED ROUTES GO HERE
# IMPORTS
from app import app
from flask import render_template, request,session,Response,flash
from app.db import books
from app.utils import validateLogin,validateAdmin

@app.before_request
def before():
	print(f"CURRENT ROUTE => {request.url_rule}")


@app.errorhandler(404)
def notFound(e):
	return render_template("404.html",PageTitle="Page Not Found")


@app.route("/")
def index():
	print(app.url_map)
	print(session)
	return render_template("home.html",PageTitle="Home")


@app.route("/books/<id>",methods = ['GET'])
def bookHandler(id):
	if request.method == "GET":
		bookData = books.getBook(id)
		if not bookData['status']:
			return Response(bookData['message'],400)
		bookData = bookData['message']
		return render_template("bookPage.html",bookData = bookData,PageTitle = "Book page")


@app.route("/books")
def bookCatalogueHandler():
	bookList = books.getAllBooks()
	if not bookList['status']:
		return Response(bookList['status'],400)
	return render_template("bookCatalouge.html",bookList= bookList['message'])


@app.route("/search",methods=['POST'])
def filteredCatalouge():
	if request.method == "POST":
		data = request.form
		bookList = books.getAllBooks(data)
		if not bookList['status']:
			return Response(bookList['status'],400)
		return render_template("bookCatalouge.html",bookList = bookList['message'],searchData=data)


@app.route("/reserve",methods=["POST"])
@validateLogin
def reserveHandler():
	if request.method == "POST":
		data = request.json
		reserveStatus = books.reserveBook(data['_id'],data['name'],session['token'])
		if not reserveStatus['status']:
			flash(reserveStatus['message'])
			return "false"
		return "true"


#####################################################################################
# 							ADMIN ONLY ROUTES BELOW									#
#####################################################################################

@app.route("/returns",methods=['GET','POST'])
@validateAdmin
def returnHandler():
	if request.method == "GET":
		returnStatus = books.listAllBorrowedBooks()
		if not returnStatus['status']:
			return Response(returnStatus['message'],400)
		return render_template("bookReturnsPage.html",bookDataList=returnStatus['message'],PageTitle="Book Returns")
	if request.method == "POST":
		returnBookData = request.get_json()
		print(returnBookData)
		return True


@app.route("/returns/search",methods=['POST'])
@validateAdmin
def returnSearchHandler():
	if request.method == "POST":
		data = request.form
		returnStatus = books.listAllBorrowedBooks(data)
		if not returnStatus['status']:
			return Response(returnStatus['message'],400)
		return render_template("bookReturnsPage.html",bookDataList=returnStatus['message'],searchData=data,PageTitle="Book Returns")

	