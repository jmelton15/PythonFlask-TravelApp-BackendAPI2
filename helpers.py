import random
import re
from flask import helpers, json

def is_correctuser_or_admin(jwt_payload,user_id):
    """[auth function that determines if the user is an Admin or the correct user]

    Args:
        user_id ([int]): [id of logged in user]
        jwt_payload ([object]): [json web token payload]
        
    Returns:
        Boolean (true or false)
    """
    if jwt_payload['user_id'] == user_id or jwt_payload['is_admin'] == True:
        return True
    return False

def authenticate_jwt(req):
    jwt_header = req.headers.get('Authorization')
    if jwt_header:
        return jwt_header
    return False

def get_random_photo(waypointData):
    rand_photos = []
    for place in waypointData:
        rand_location = random.choice(waypointData[place])
        rand_photos.append(rand_location["photo"])
    return json.dumps(random.choice(rand_photos))

def match_href(link):
    matched = re.findall(r'href\s?=\s?[\'"]?([^\'" >]+)',link)
    if matched:
        return matched[0]
    return ""
