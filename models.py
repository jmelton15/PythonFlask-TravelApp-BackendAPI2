from operator import truediv
from flask import current_app, json,jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import create_engine
from flask_bcrypt import Bcrypt
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
from config_files import keys
from sqlalchemy.dialects import postgresql
import ast
from map_client import unpack_decoded_coords 
import datetime
import pytz
import jwt 


db = SQLAlchemy()
bcrypt = Bcrypt()

def connect_db(app):
    """[connect to database]
    """
    db.app = app
    db.init_app(app)


class Follows(db.Model):
    """
     Follows model class that handles the follows table in the database
    """
    
    __tablename__ = 'follows'
    
    user_being_followed_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id",ondelete="CASCADE"),
        primary_key=True
    )
    user_following_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id",ondelete="CASCADE"),
        primary_key=True
    )


class Likes(db.Model):
    """
     Likes model class that handles the likes table in the database
    """

    __tablename__ = 'likes'
    
    id = db.Column(db.Integer,primary_key=True)
    user_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id",ondelete="CASCADE")
    )
    trip_id = db.Column(
        db.Integer,
        db.ForeignKey("trips.id",ondelete="CASCADE")
    )


class Messages(db.Model):
    """
     Messages model class that handles the messages table in the database
    """
    
    __tablename__ = 'messages'
    
    id = db.Column(db.Integer,primary_key=True)
    msg_txt = db.Column(db.String(400), nullable=False)
    created_on = db.Column(db.DateTime)
    conversation_id = db.Column(db.String,nullable=False)
    from_user_avatar = db.Column(db.String,nullable=False)
    to_user_id = db.Column(
        db.Integer, 
        db.ForeignKey("users.id",ondelete="CASCADE"),
        nullable=False
    )
    from_user_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id",ondelete="CASCADE"),
        nullable=False
    ) 


class User(db.Model):
    """User model/class for users table creation and methods for users
    """
    __tablename__ = "users"
    
    @classmethod
    def create_auth_token(cls,user_id,is_admin):
        """[Generates the JWT token for authorization on the site]

        Args:
            user_id ([int]): [Id of the logged in user]

        Returns:
            [jwt payload]: [
                            Returns a JWT payload with properties of: 
                             exp -> experiation time/date]
                             iat -> time token was generated
                             user_id -> contains the user_id
                             is_admin -> boolean for if user is admin
                            ]
        """
        try:
            payload = { 
                # 'exp': datetime.datetime.utcnow() + datetime.timedelta(days=0, seconds=5),
                # 'iat': datetime.datetime.utcnow(),
                'user_id': user_id, 
                'is_admin':is_admin
            }
            return jwt.encode(
                payload,
                current_app.config.get('SECRET_KEY'),
                algorithm='HS256'
            )
        except:
            return "error"
    
    @classmethod
    def decode_auth_token(cls,token):
        """
        Handles returning parts of the payload specified in the return
        """
        try:
            payload = jwt.decode(token,current_app.config.get('SECRET_KEY'))
            return {"user_id":payload['user_id'],"is_admin":payload['is_admin']}
        except jwt.exceptions.ExpiredSignatureError:
            return 'Auth Token Has Expired. Please Login Again'
        except jwt.exceptions.InvalidTokenError:
            return 'Token Not Valid. Please Register or Login'
    
    @classmethod
    def register(cls,username,password,email):
        """register class method for creating a User (registering a new User)
            With a secure and encrypted password that can be stored
        Args:
            username ([type]): [description]
            pwd ([type]): [password]
            email ([type]): [description]
            
        Returns:
            A User object with encrypted password for database storage
        """
        hashed = bcrypt.generate_password_hash(password)
        hashed_utf8 = hashed.decode("utf8")
        
        user = User(username=username,password=hashed_utf8,email=email)
        db.session.add(user)
        return user
    
    @classmethod
    def authenticate(cls,username,pwd):
        """validate a an attempted login is allowed and in the database
            and that the password is correct for that user
        Args:
            username ([type]): [description]
            pwd ([type]): [password]
        Returns:
            the user from User query if valid, otherwise false
        """
        user = User.query.filter_by(username=username).first()
        
        if user and bcrypt.check_password_hash(user.password,pwd):
            followers = user.followers
            following = user.following
           
            data = {"user":user,}
            return user
        else:
            return False
    
    @classmethod
    def serialize_user(cls,user):
        """
         method for serializing a User object into readable json
        """
        return {
            "username":user.username,
            "user_id":user.id,
            "bio":user.bio,
            "member_status":user.member_status,
            "avatar_pic_url":user.avatar_pic_url,
            "follow_count":user.follow_count,
            "follower_count":user.follower_count
        }
    
    @classmethod
    def reset_password(cls,new_pass,user):
        """ encrypts the new password a user created and stores it as their new password 
        """
        hashed = bcrypt.generate_password_hash(new_pass)
        hashed_utf8 = hashed.decode("utf8")
        user.password = hashed_utf8
        db.session.commit()
    
    
    def __repr__(self): 
        """show info about User objects
        """
        u = self
        return f"<User user_id={u.id} username={u.username} >"
    
    id = db.Column(db.Integer,primary_key=True,autoincrement=True)
    username = db.Column(db.String,nullable=False,unique=True)
    password = db.Column(db.String,nullable=False)
    email = db.Column(db.String,unique=True)
    member_status = db.Column(db.Boolean,server_default='f',nullable=True)
    bio = db.Column(db.String(300),nullable=True,default='No Bio Created Yet, Come Back Again To See!')
    avatar_pic_url = db.Column(db.String,nullable=True, server_default='/static/images/default_avatar.jpg')
    free_trips = db.Column(db.Integer, default=5,nullable=True)
    trip_count = db.Column(db.Integer,default=0,nullable=True)
    follow_count = db.Column(db.Integer,default=0,nullable=True)
    follower_count = db.Column(db.Integer,default=0,nullable=True)
    liked_trips = db.Column(db.ARRAY(db.Integer,zero_indexes=True),nullable=False)
    reset_token = db.Column(db.String,nullable=True,unique=True)
    is_admin = db.Column(db.Boolean,server_default='f',nullable=True)
    
    trips = db.relationship('Trip',backref='user',cascade="all, delete")
    # messages = db.relationship('Message')

    followers = db.relationship(
        "User",
        secondary="follows",
        primaryjoin=(Follows.user_being_followed_id == id),
        secondaryjoin=(Follows.user_following_id == id)
    )

    following = db.relationship(
        "User",
        secondary="follows",
        primaryjoin=(Follows.user_following_id == id),
        secondaryjoin=(Follows.user_being_followed_id == id)
    )

    # likes = db.relationship(
    #     'Message',
    #     secondary="likes"
    # )


class Trip(db.Model):
    """ Trip model/class that handles setting up the trips table in the database
        This table will store data about a user's saved trip and allow them to see
        their past created trips
    """ 
    __tablename__ = "trips"
    
    @classmethod
    def encrypt_and_store_trip_data(cls,start_point,end_point,waypoint_names,waypoint_addresses,coords,photo,user_id):
        """ Classmethod for encrypting trip data to store in the Database.
            Uses AES Cipher.
        """
        key = keys['CIPHER_KEY']
        iv = keys['IV']
        sp_data = start_point.encode()
        ep_data = end_point.encode()
        wp_name_data = [wp.encode() for wp in waypoint_names]
        wp_address_data = [wp.encode() for wp in waypoint_addresses]
        wp_coords = [wp.encode() for wp in coords] 
        cipher = AES.new(key, AES.MODE_GCM, iv)
        enc_sp = cipher.encrypt(pad(sp_data, 16))
        enc_ep = cipher.encrypt(pad(ep_data, 16))
        enc_wp_names = [cipher.encrypt(pad(wp, 16)) for wp in wp_name_data]
        enc_address = [cipher.encrypt(pad(wp, 16)) for wp in wp_address_data]
        enc_coords = [cipher.encrypt(pad(wp, 16)) for wp in wp_coords]
        
        trip = Trip(start_point=enc_sp,end_point=enc_ep,waypoint_names=enc_wp_names,waypoint_addresses=enc_address,waypoint_latlng=enc_coords,
                    photo=photo,user_id=user_id)
        db.session.add(trip)
        return trip

    def decrypt_trip_data(self):
        """ Method for decrypting trip data of a Trip object to be accessed in the app
            Returns a dictionary:
            {'start_point':start_point,'end_point':end_point,'waypoints':waypoints, etc..}
        """
        key = keys['CIPHER_KEY']
        iv = keys['IV']
        cipher = AES.new(key,AES.MODE_GCM,iv)
        dec_sp = unpad(cipher.decrypt(self.start_point), 16)
        dec_ep = unpad(cipher.decrypt(self.end_point), 16)
        dec_wp_name = [unpad(cipher.decrypt(wp), 16).decode() for wp in self.waypoint_names]
        dec_wp_address = [unpad(cipher.decrypt(wp), 16).decode() for wp in self.waypoint_addresses]
        dec_coords = [ast.literal_eval(unpad(cipher.decrypt(wp), 16).decode()) for wp in self.waypoint_latlng]
        wp_coords = unpack_decoded_coords(dec_coords) 
        return {'id':self.id,'start_point':dec_sp.decode(),'end_point':dec_ep.decode(), 
                'waypoint_names':dec_wp_name,'addresses':dec_wp_address,'photo':self.photo,
                'waypoint_latlng':wp_coords}
     
     
    @classmethod 
    def serialize_trip(cls,trip):
        """
         method for serializing a Trip object into readable json
        """
        return {
            "id":trip.id,
            "start_point":trip.start_point,
            "end_point":trip.end_point,
            "waypoint_names":trip.waypoint_names,
            "waypoint_addresses":trip.waypoint_addresses,
            "waypoint_coords":trip.waypoint_coords,
            "marker_data":trip.marker_data,
            "photo":trip.photo,
            "user_id":trip.user_id
        }
    
    @classmethod
    def get_trips_from_db(cls,photo_string):
        engine =create_engine(current_app.config['SQLALCHEMY_DATABASE_URI'])
        connection = engine.connect()
        query = """ SELECT id,start_point,end_point,waypoint_names,waypoint_addresses,waypoint_coords,photo::jsonb"""

    def __repr__(self):  
        """show info about Trip objects
        """
        t = self
        return f"<Trip start_point={t.start_point} | end_point={t.end_point}>"
    
    id = db.Column(db.Integer,primary_key=True,autoincrement=True)
    start_point = db.Column(db.String,nullable=False) 
    end_point = db.Column(db.String,nullable=False)
    waypoint_names = db.Column(db.ARRAY(db.String,zero_indexes=True),nullable=False)
    waypoint_addresses = db.Column(db.ARRAY(db.String,zero_indexes=True),nullable=False)
    waypoint_coords = db.Column(db.ARRAY(db.String,zero_indexes=True),nullable=True)
    marker_data = db.Column(db.String,nullable=False)
    photo = db.Column(db.String, nullable=True, server_default="/static/images/default_trip.jpg")
    user_id = db.Column(db.Integer,db.ForeignKey("users.id",ondelete="CASCADE"),nullable=False)
    
    



     