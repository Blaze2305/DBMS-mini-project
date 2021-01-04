# ALL USER RELATED ROUTES GO HERE
# IMPORTS
from app import app
from flask import render_template, request,Response, url_for,session,redirect,flash
from app.db import user
from app.utils import validateLogin,validateAdmin

@app.route("/login",methods = ["GET","POST"])
def loginHandler():
	# Render the login page
	if request.method == "GET":
		if "from" in request.args:
			session['popUrl'] = request.args.get("from")

		return render_template("login.html",PageTitle="Login")
	# Route for the user to login
	if request.method == "POST":
		data = request.form
		loginStatus = user.userLogin(data)
		if not loginStatus['status']:
			flash(loginStatus['message'])
			return render_template("login.html",PageTitle="Login")
			# return Response(loginStatus['message'],400)
		else:
			session['token'] = loginStatus['token']
			if "popUrl" in session and session['popUrl']:
				route = session.pop('popUrl')
				return redirect(route)

			return redirect(url_for("index"))



@app.route("/logout",methods = ["GET"])
@validateLogin
def logoutHandler():
	# Route for logging out the user
	if request.method == "GET":
		token = session['token']
		logoutStatus = user.userLogout(token)
		if not logoutStatus['status']:
			return Response(logoutStatus['message'],400)
		else:
			session['token'] = ''
			return redirect(url_for("index"))



@app.route("/profile",methods = ['GET'])
@validateLogin
def profileHandler():
	if request.method == "GET":
		token = session['token']
		if not token:
			return Response("Token missing , please logout and log back in",400)
		
		userDataResponse = user.getUserFromToken(token)
		if not userDataResponse['status']:
			return Response(userDataResponse['message'],400)

		userData = userDataResponse['message']
		borrowData = userDataResponse['borrows']
		return render_template("profile.html",userData = userData, borrowData = borrowData,PageTitle="User")


#####################################################################################
# 							ADMIN ONLY ROUTES BELOW									#
#####################################################################################

@app.route("/users",methods=['GET'])
@validateAdmin
def userListHandler():
	if request.method == "GET":
		userData = user.getUsersList()
		if not userData['status']:
			return Response(userData['message'],400)
		return render_template("userListPage.html",PageTitle="Users",userDataList=userData['message'])

	
@app.route("/users/search",methods=['POST'])
@validateAdmin
def userFilterHandler():
	if request.method == "POST":
		data = request.form
		UserList = user.getUsersList(data)
		if not UserList['status']:
			return Response(UserList['status'],400)
		return render_template("userListPage.html",userDataList = UserList['message'],searchData=data,PageTitle="Users")


@app.route("/users/<id>",methods = ['GET'])
@validateAdmin
def userHandler(id):
	# Render out a users profile page as an admin
	if request.method == "GET":

		userDataResponse = user.getUserFromID(id)
		if not userDataResponse['status']:
			return Response(userDataResponse['message'],400)

		userData = userDataResponse['message']
		borrowData = userDataResponse['borrows']
		return render_template("profile.html",userData = userData, borrowData =  borrowData,PageTitle="User")