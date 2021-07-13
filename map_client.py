from config_files import keys
from urllib.parse import urlparse, parse_qsl
from urllib.parse import urlencode
import requests
import googlemaps
from datetime import datetime
import numpy
import math
from Linked_List import LinkedList
from helpers import match_href

googleURL = "https://www.google.com/search?q="
GOOGLE_SERVER_API_KEY = keys["GOOGLE_SERVER_API_KEY"]
# GOOGLE_PHOTO_API_KEY = keys["GOOGLE_PHOTO_API_KEY"]

gmaps = googlemaps.Client(key=GOOGLE_SERVER_API_KEY)
now = datetime.now() 

def get_latlng(address):
    """ Takes in a human-readable address and returns the lat,lng data
    """
    geocode_result = gmaps.geocode(address) 
    return geocode_result 

def unpack_decoded_coords(decoded_coordinates):
    """ Handles turning decoded coordinates that is an array of tuples into an array of-
        objects in the form of:
        ex: [{lat:<int>,lng:<int>}, etc...]
        This will allow the client side Google API to display markers again from a saved trip
        
        NOTE -> this is only used if the encoding method is used on the server to encrypt trip data. 
                 Otherwise this goes unused 
    """
    return [{'lat':tupe[0],'lng':tupe[1]} for tupe in decoded_coordinates]


def get_directions(start,stop,region="US",mode="driving"):
    """ Gets directions data from google maps
    """
    directions_result = gmaps.directions(start,stop,
                                    region=region,
                                    mode=mode,)
    return directions_result 

def get_total_distance(directions_data):
    """[get the total distance from a directions result from google]

    Returns:
        [int]: [total distance in meters]
    """
    distance = directions_data[0]["legs"][0]["distance"]["value"]
    return distance

def get_path_points(directions_data):
    """[Gets the coordinates or "stops" along a directions result from google]

    Args:
        directions_data ([directions result object]): [object with directions data from google]

    Returns:
        [object]: [0:{lat,lng},1:{lat,lng},etc]
    """
    steps = directions_data[0]["legs"][0]["steps"]
    path_points = {};   
    for i in range(1,len(steps)):
        path_points[i] = {"lat":steps[i-1]["start_location"]["lat"],"lng":steps[i-1]["start_location"]["lng"]}
    return path_points 
     
def package_nearby_place_data(data,place="no business name",place_number=0):
    """ Takes data from nearby_places search results and returns the top rated place
        in the search category that is nearby.
        if there isn"t anything it finds, then it returns None
        
        place_number can be used to choose a different place in the list of results; defaults to the first place index 0
        
        place is used only for storing a name if there is no name to a location; defaults to "no business name"
        
        This function currently only returns one top rated place, but can be adjusted to easily 
        return a list of place objects if desired.
        
        RETURNS: 
        photo = {"img_url":node["photo"],"attribution":node["attribution"]}
        {"name":
        "icon":
        "rating":
        "place_id":
        "address":
        "web_url":f"{googleURL}{urlEncoder(name)}+{urlEncoder(address)}",
        "position":{"lat":lat,"lng":lng},
        "photo":}       
    """
    top_places = []
    if data and data != []:
        # d = data[place_number]
        for d in data:
            if place and d.get("rating") and d["rating"] != 0:
                photo_reference = d["photos"][0]["photo_reference"] if d.get("photos") else ""
                img_url = f"https://maps.googleapis.com/maps/api/place/photo?maxwidth=1600&maxheight=300&photoreference={photo_reference}&key={GOOGLE_SERVER_API_KEY}" if photo_reference != "" else ""
                attribution = match_href(d["photos"][0]["html_attributions"][0]) if img_url != "" else ""
                photo = {"img_url":img_url,"attribution":attribution}
                lat = d["geometry"]["location"]["lat"]
                lng = d["geometry"]["location"]["lng"]
                position = {"lat":lat,"lng":lng}
                name = d.get("name",place)
                address = d.get("vicinity","No Address Info On Google")
                web_url = f"{googleURL}{urlEncoder(name)}+{urlEncoder(address)}"
                
                top_rated = {"name":name,"rating":d["rating"],"address":address,"position":position,"icon":d["icon"],
                            "photo":photo,"place_id":d.get("place_id","No Place-ID Info On Google"),"web_url":web_url}
                top_places.append(top_rated)
        return top_places
    return None           
     
 ## anything >= 70 limit to 14
## anything >= 50 < 70 limit to 10
## anything >= 20 < 50 limit to 8
## anything >= 10 < 20 limit to 6
## else keep calculated num
## These numbers don"t include the start coord and end coord 
### so add 2 to these numbers to get exact number of stops
def calc_num_searches(radius,metersBetween):
    """[A function for setting an ideal number of times the algorithm should search along a route.
        This is to prevent overlapping the radius too often as well as limiting the number of times the 
          algorithm requests to google APIs
       ]

    Args:
        radius ([int]): [distance radius in meters]
        metersBetween ([int]): [distance between the start and stop location in meters]

    Returns:
        [int]: [a number representing the number of times to request to google for nearby places]
    """
    stops_with_radius = math.floor(metersBetween/radius)
    if stops_with_radius >= 70:
        return 14
    if stops_with_radius >= 50 and stops_with_radius < 70:
        return 10
    if stops_with_radius >= 20 and stops_with_radius < 50:
        return 8
    if stops_with_radius >= 10 and stops_with_radius < 20:
        return 6
    else:
        return stops_with_radius if stops_with_radius > 2 else 2

    
def calc_stops_between(coords,num_searches):
    """[calculates the number of iterations to skip before searching again.
        Uses the num_searches gotten from calc_num_searches() function to decide.
       ]

    Args:
        coords ([list]): [list of coordinates along a path]
        num_searches ([int]): [a number representing the number of times to request to google for nearby places]

    Returns:
        [int]: [iterations to skip before requesting to google again]
    """
    return math.floor(len(coords)/num_searches)


def has_already(place,top_place,place_object):
    """[Function used to determine if we have already seen a location in one of our requests.
        This is used to prevent storing multiple of the same locations in the users trip
       ]

    Args:
        place ([string]): [waypoint Point of interest]
        top_place ([object]): [current place to compare to]
        place_object ([object]): [object containing all the places we have seen so far]

    Returns:
        [boolean]: [true if seen false if not]
    """
    places_list = place_object.get(place)
    if places_list:
        for place in places_list:
            if place['address'] == top_place['address']:
                return True
        return False
    return False 
      
##create something to package according to place like so:
### {Place1:[{},{},{}],Place2:[{},{},{}]}

## create a function or way to get start coord and end coord POIs
## could add in a param for number of stops. default = calc_num_searches() result
def get_top_rated_places(coords,waypoints,metersBetween,radius=50000):
    """[Handles iterating over the points of interest/waypoints a user input
        and finding the top rated places along the route. This is done using the other methods in the map_client.py file.
        
        recheck_value is used if a top_rated place has already been found. It will search for the next place available in the google results.
       ]

    Args:
        coords ([list]): [list of coordinates along a path]
        waypoints ([list]): [list of strings that contains all the points of interest from user input]
        metersBetween ([int]): [distance between the start and stop location in meters]
        radius ([int,optional]): [distance radius in meters] Defaults to 50000.

    Returns:
        [object]: [{place1:[{location1},{location2},etc],place2:[]}]
    """
    final_places = {}
    num_searches = calc_num_searches(radius,metersBetween)
    stops_between = calc_stops_between(coords,num_searches)
    
    
    iterations = stops_between
    while(iterations < len(coords)):
        for place in waypoints:
            recheck_value = 2
            if iterations+stops_between > len(coords):
                iterations = len(coords)-1
            place_details = gmaps.places_nearby(location=(coords[iterations]["lat"],coords[iterations]["lng"]),radius=radius,keyword=place)['results']
            top_places = package_nearby_place_data(place_details,place) 
            top_place = top_places[0]
            if(not top_place):
                iterations = iterations + stops_between
                continue
            while(has_already(place,top_place,final_places)):
                top_place = top_places[recheck_value]
                recheck_value += 1
            ## this line makes sure we already have an array going before adding
            if final_places.get(place):
                final_places[place].append(top_place)
            else: 
                final_places[place] = [top_place]
        iterations = iterations + stops_between
    return final_places



def urlEncoder(waypointnames):
    "+".join(waypointnames[i:i+1] for i in range(0,len(waypointnames),2))
    return waypointnames

    
# def get_distance_between_two_coords(start,stop):
#     """ Takes in two coordinates (lat,lng) and (lat,lng) and checks the distance between them
#         Returns the distance value and time to travel. 
#         Instead of returning true/false, I opened this function to be used for 
#         all distance data
#         returned data object looks like this:
#         {'distance':value in meters,'duration':value in seconds}
#         #{'elements':[{'distance':{'text':'km','value':num},'duration':{'text':hours mins,'value':num}}]}
#     """
#     distance_data = gmaps.distance_matrix(start,stop)
#     return {'distance':distance_data['rows'][0]['elements'][0]['distance']['value'], #returns distance in meters
#             'duration':distance_data['rows'][0]['elements'][0]['duration']['value']}  #returns duration in seconds
 
 
# def extract_ids(search_result):
#     """ Takes a search result and returns the place_ids of all the results
#     """
#     ids = []
#     for place in search_result:
#         ids.append(place['place_id'])
#     return ids


def lat_lng(search_result):
    """ Generator function that returns one lat,lng tuple at a time from 
        places search results
        Can be used to send back individual waypoints to JavaScript
    """
    for place in search_result:
#       [(place['geometry']['location']['lat'],place['geometry']['location']['lng']) for place in r]
        lat = place['geometry']['location']['lat']
        lng = place['geometry']['location']['lng']
        yield (lat,lng)
