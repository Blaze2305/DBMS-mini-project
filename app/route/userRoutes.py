# ALL USER RELATED ROUTES GO HERE
# IMPORTS
from app import app
from flask import render_template, request,Response, url_for,session,redirect,flash
from app.db import user


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



@app.route("/users/<id>",methods = ['GET'])
def userHandler(id):
	# Render out a users profile page as an admin
	if request.method == "GET":

		userDataResponse = user.getUserFromID(id)
		if not userDataResponse['status']:
			return Response(userDataResponse['message'],400)

		userData = userDataResponse['message']
		borrowData = userDataResponse['borrows']
		return render_template("profile.html",userData = userData, borrowData =  borrowData,PageTitle="User")



@app.route("/profile",methods = ['GET'])
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
		return render_template("profile.html",userData = userData, borrowData =  borrowData,PageTitle="User")