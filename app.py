from Linked_List import LinkedList
from sqlalchemy import exc
from config_files import keys
import os
import random
from flask import Flask, json, request,render_template,redirect,flash,session,flash,g,jsonify
from flask_mail import Mail, Message
from urllib.parse import urlparse, parse_qsl
from urllib.parse import urlencode
import requests
import secrets 
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import IntegrityError
from sqlalchemy import desc
from models import db, connect_db,User,Trip
from flask_bcrypt import Bcrypt
from map_client import get_top_rated_places,get_directions,get_path_points,get_total_distance
from flask_cors import CORS
from helpers import is_correctuser_or_admin,authenticate_jwt,get_random_photo
from UnsplashPhotoApi import randomWaypointPhoto

CURR_USER_KEY = "curr_user"
MEMBER_STATUS = "member_status"
CSRF_TOKEN_KEY = None
USER_SESSION_TOKEN = None


app = Flask(__name__)
CORS(app)
app.run(debug=True)

app.config["SESSION_PERMANENT"] = False
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL','postgresql:///dtri')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = True
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY',"SUPERSECRETKEY")
app.config['SENDGRID_API_KEY'] = os.environ.get('SENDGRID_API_KEY',"DefaultValue")  
app.config['MAIL_SERVER'] = os.environ.get('MAIL_SERVER','smtp.gmail.com')
app.config['MAIL_PORT'] = os.environ.get('MAIL_PORT',587)
app.config['MAIL_USERNAME'] = os.environ.get('MAIL_USERNAME')
app.config['MAIL_PASSWORD'] = os.environ.get('MAIL_PASSWORD')
app.config['MAIL_USE_TLS'] = os.environ.get('MAIL_USE_TLS', True)
app.config['MAIL_USE_SSL'] = os.environ.get('MAIL_USE_SSL', False)
# app.config['MAIL_SUPPRESS_SEND'] = os.environ.get('MAIL_SUPPRESS_SEND')
app.config['MAIL_DEBUG'] = True
app.config['MAIL_DEFAULT_SENDER'] = os.environ.get('MAIL_USERNAME')

mail = Mail(app)
connect_db(app)
# db.create_all()  
 

######################################################################
# TODO -- ADD IN LOGOUT 
# TODO -- ADD ABILITY TO DELETE ACCOUNT
# TODO -- FINALIZE PASSWORD RESET ROUTE
###############################################################################

@app.route('/',methods=["GET"]) 
def welcome_message():
    return (
        jsonify({"message":"Welcome To The Homepage of DTRI API"})
    )

###################################################################################
# User routes

@app.route('/register', methods=["POST"])
def signup_user():
    """Handles signing up a user. 
     Data in => {username, email, password}
     
     RETURNS => {user_data:{user_id,username,bio,member_status,avatar_pic_url,following,followers,saved_trips,liked_trips},
                 token:some jwt payload token
                }
    """
    formData = request.json
    try:
        user = User.register(
            username=formData["username"].lower(),
            password=formData["password"],
            email=formData["email"].lower()
        )  
        db.session.commit()
    except IntegrityError:
        return jsonify({"Error Message":"Username already taken"})
    token = user.create_auth_token(user.id,user.is_admin)
    
    return (jsonify({'user_data':
            {
            "user_id":user.id,
            "username":user.username,
            "bio":user.bio, 
            "member_status":user.member_status,
            "avatar_pic_url":user.avatar_pic_url,
            "following":[User.serialize_user(following) for following in user.following],
            "followers":[User.serialize_user(follower) for follower in user.followers],
            "trip_count":user.trip_count,
            "saved_trips":[Trip.serialize_trip(trip) for trip in user.trips],
            "liked_trips":[] if user.liked_trips == None else user.liked_trips
            },
            "token":token.decode()
            }))
    
@app.route('/login', methods=["POST"])
def login_user():
    """Handle logging in a user
     
      Data in => {username,password}
      
      Returns => {user_data:{user_id,username,bio,member_status,avatar_pic_url,following,followers,
                            follow_count,follower_count,saved_trips,liked_trips},
                 token:some jwt payload token
                 }
    """ 
    formData = request.json 
    user = User.authenticate(formData["username"].lower(),formData["password"])
    if user:
        token = user.create_auth_token(user.id,user.is_admin)
        return (jsonify({'user_data':
            {
            "user_id":user.id, 
            "username":user.username,
            "bio":user.bio,
            "member_status":user.member_status,
            "avatar_pic_url":user.avatar_pic_url,
            "following":[User.serialize_user(following) for following in user.following],
            "followers":[User.serialize_user(follower) for follower in user.followers],
            "follow_count":user.follow_count,
            "follower_count":user.follower_count,
            "trip_count":user.trip_count,
            "saved_trips":[Trip.serialize_trip(trip) for trip in user.trips],
            "liked_trips":[] if user.liked_trips == None else user.liked_trips
            },
            'token':token.decode()
            }))
    else:
        return jsonify({"Error Message":"Could not get user data, please try logging in again"})


@app.route('/users/<int:user_id>/trips/saved',methods=["GET"])
def get_users_trips(user_id):
    """ Gets all the trips the user has saved
    
    RETURNS =>  {id,start_point,end_point,waypoint_names,waypoint_addresses,waypoint_coords,marker_data,photo,user_id}
                    
    authorization required: logged in, correct user or admin
    """ 
    token = authenticate_jwt(request)
    if(token):
        # token = jwt_header.split(" ")[1]
        jwt_payload = User.decode_auth_token(token)
        if(is_correctuser_or_admin(jwt_payload,user_id)): 
            user = User.query.get_or_404(user_id)
            trips = user.trips
            saved_trips = [Trip.serialize_trip(trip) for trip in trips]
            return jsonify({"saved_trips":saved_trips})
        return jsonify({"Message":jwt_payload}) 
    else:
        token = ''
        return jsonify({"Message":"Not Authorized. Must Provide Valid JWT"})
    

# @app.route('/users/<int:user_id>/profile',methods=["PATCH","DELETE"])
# def update_or_delete_user(user_id):
#     """ Handles either updating a user's username or deleting the user
#     """

#     if not g.user:
#         flash("Unauthorized Access. This Is Not Your Account", "alert-primary")
#         redirect("/login")
#     if validate_client_side_data(request.headers):
#         if request.method == "DELETE":
#             User.query.filter_by(id=user_id).delete()
#             db.session.commit()
#             do_logout()
#             response = {
#                 "alert":"Account Successfully Deleted. You're Welcome Back Anytime!"
#             }
#             return jsonify(response=response)
#         if request.method == "PATCH":
#             user = User.query.get_or_404(user_id)
#             user.username = request.json.get('new_username',user.username)
#             try:
#                 db.session.commit()
#             except IntegrityError:
#                 return jsonify(response={"error":"Username Already Exists. Try Another"})
#             response = {
#                 "ok":'OK'
#             }
#             return jsonify(response=response)
#     else:
#         flash("You Cannot Do That","alert-primary")
#         return redirect("/main")

###################################################################################
# Map Interaction Routes   
    
@app.route('/users/<int:user_id>/trip',methods=["POST"])
def create_trip(user_id):
    """ Handles Creating and Displaying New Trip On A Map
    
        Data in => {startLocation,endLocation,region,waypoints}
    
        RETURNS [array of objects] => {marker_data:[{name,icon,place_id,address,web_url,position,photo},etc.]}
    """
    token = authenticate_jwt(request)
    if(token): 
        # token = jwt_header.split(" ")[1]
        jwt_payload = User.decode_auth_token(token)
        if(is_correctuser_or_admin(jwt_payload,user_id)):
            user = User.query.get_or_404(user_id)
            if user.trip_count >= 4:
                return jsonify({"Message":"Currently, Users Are Only Allowed To Create 4 Trips. Go To The 'About Page' To Learn More"})
            response = {     
                "member_status":user.member_status, 
                "saved_trips":user.trip_count
            }
            trip_data = handle_trip_request_data(request.json)
            # marker_data = createMarkerDataArray(trip_data)
            response["marker_data"] = trip_data
            return jsonify({"data":response})
    else:
        token = ''
        return jsonify({"Message":"Not Authorized. Must Provide Valid JWT"})
    
@app.route("/users/<int:user_id>/trip/save",methods=["POST"])
def save_trip_for_user(user_id):
    """ Handles Saving a Created Trip to the Database
    
        Data in => {startLocation,endLocation,waypoinData}
        
        Returns => {Response:{Message:Your Trip Has Been Saved! Go Take A Look At It On Your Travel Journal Page!}}
    """
    token = authenticate_jwt(request)
    if(token):
        # token = jwt_header.split(" ")[1]
        jwt_payload = User.decode_auth_token(token)
        if(is_correctuser_or_admin(jwt_payload,user_id)):
            user = User.query.get_or_404(user_id)
            response = {
                "Message":"Your Trip Has Been Saved! Go Take A Look At It On Your Travel Journal Page!"
            }
            saved_trip = save_trip_data(request.json)
            if saved_trip:
                user.trip_count += 1
                db.session.add(saved_trip)
                db.session.commit()
                return jsonify(response=response)
            return jsonify({"Message":"There was a problem saving the trip"})
    token = ''
    return jsonify({"Message":"Not Authorized. Must Provide Valid JWT"})
    

###################################################################################
# Trip Deletion Route
# TODO -- SUBTRACT FROM TRIP_COUNT EVENTUALLY

@app.route('/users/<int:user_id>/trips/<int:trip_id>',methods=["DELETE"])
def delete_trip(user_id,trip_id):
    """ Handles deleting a trip based on user_id and trip_id
    
      Returns => {Message:Trip Deleted Successfully}
    """
    token = authenticate_jwt(request)
    if(token):
        # token = jwt_header.split(" ")[1]
        jwt_payload = User.decode_auth_token(token)
        if(is_correctuser_or_admin(jwt_payload,user_id)):
            try:
                Trip.query.filter_by(id=trip_id).delete()
                db.session.commit()
                return jsonify({"Message":"Trip Deleted Successfully"})
            except:
                return jsonify({f"Message":"There was a problem deleting trip #{trip_id} for user id {user_id}"})
        return jsonify({"Message":"You are not authorized to delete this trip"})
    return jsonify({"Message":"You are not authorized to delete this trip"})    


########################################################################################
## FUNCTIONS FOR MAP INTERACTION ##

def handle_trip_request_data(request_data):
    """ Handles gathering request data from a posted trip on the client side
        And then runs it through the get_top_rated_waypoints function 
        and returns the top_rated_waypoints results
    """
    start_location = request_data["startLocation"]
    end_location = request_data["endLocation"]
    region = request_data["region"] 
    waypoints = request_data["waypoints"]
    direction_data = get_directions(start_location,end_location,region)
    distance_between = get_total_distance(direction_data)
    path_points = get_path_points(direction_data)
    return get_top_rated_places(path_points,waypoints,distance_between)

def save_trip_data(request_data):
    """ Handles gathering request data when a user saves their trip details.
        This will save their trip data to the database
    """
    # sp and ep should be regular strings
    start_point = request_data["startLocation"] 
    end_point = request_data["endLocation"] 
    user_id = request_data["userId"] 
    marker_data = request_data["waypointData"]
    waypoint_names = []
    coords = []
    addresses = []  
    photo_obj = get_random_photo(marker_data)
     
     
    # for place in marker_data:
    #     for location in place:
    #         waypoint_names.append(location["name"])
    #         coords.append(location["position"])
    #         addresses.append(location["address"])
    
    saved_trip = Trip(start_point=start_point,end_point=end_point,waypoint_names=waypoint_names,
                      waypoint_addresses=addresses,waypoint_coords=coords,marker_data=json.dumps(marker_data),
                      photo=photo_obj,user_id=user_id)
   
    return saved_trip
    
         
        
####################################################################################
## PASSWORD RESET ROUTE ##       

# @app.route("/password/forgot",methods=["GET","POST"])
# def send_password_reset():
#     """ Handles showing email authentication page to recieve verification token
#        As well as sending the verification token to the user using twilio-mail service API
#     """
#     form = EmailConfirmationForm()
#     if form.validate_on_submit():
#         email = form.email.data
#         user = verify_email(email)
#         if user:
#             token = secrets.token_urlsafe(32)
#             url = os.environ.get('URL','http://127.0.0.1:5000/password?reset=') + token
#             body = f"""Hello, This Is The Password Reset Link You Requested From 'Down To The Route Of It'.
#                         Click the link below to be redirected to the password reset page:\n 
#                     {url}"""
#             subject = "Down To The Route Of It - Password Reset Link" 
#             msg = Message(recipients=[email],body=body,subject=subject)
#             mail.send(msg)
#             user.reset_token = token
#             db.session.commit()
#             flash("Code Has Been Sent and Should Be In Your Email Shortly","alert-success")
#             return redirect("/password/forgot")
#         else:
#             flash("User Not Found, Check The Email You Entered","alert-danger")
#             return redirect("/register")
#     return render_template("email_confirmation.html",form=form)

# @app.route("/password",methods=["GET","POST"])
# def show_reset_password_form():
#     """ Handles showing the reset password form as well as handling resetting the user's password
#         if the user is verified via request token
#     """
#     token = request.args.get('reset')
#     user = verify_token(token)
#     if user:
#         form = PasswordResetForm()
#         if form.validate_on_submit():
#             new_pass = form.password.data
#             User.reset_password(new_pass,user)
#             flash("Password Has Successfully Been Reset!","alert-success")
#             erase_pass_token(user)
#             return redirect("/login")
#         return render_template("password_reset_page.html",form=form)        
# ####################################################################################
# ## FUNCTIONS FOR VERIFYING and DELETEING PASSWORD RESET INFORMATION ##

# def verify_email(email):
#     """ function used for verifying users email is in the database system
#     """
#     user = User.query.filter_by(email=email).first()
#     if user:
#         return user
#     else:
#         return False
    
# def verify_token(token):
#     """ function for verifying the token in a query string
#         for password reset
#     """
#     user = User.query.filter_by(reset_token=token).first()
#     if user:
#         return user
#     else:
#         return False
    
# def erase_pass_token(user):
#     """ erases password reset token on users account
#     """
#     user.reset_token = None 
#     db.session.commit()

####################################################################################
## CSRF-TOKEN VALIDATION AND FREE-TRIP VALIDATION ##

def validate_client_side_data(request_headers):
    """ function for validating and securily checking form data from client side
    """
    csrf_token = request_headers["anti-csrf-token"]
    if csrf_token == session['csrf_token']:
        return True
    else:
        return False
    
def has_free_trips():
    """ Checks session data to see if user has free trips remaining
    """
    if session["free_trips"] > 0:
        return True
    else:
        return False

def can_save_trip():
    """ Checks if a user can still save a trip.
        This check is in place to only allow members to save more than 1 trip
    """
    if session["saved_trips"] >= 1:
        return False
    else:
        return True

    
 

          