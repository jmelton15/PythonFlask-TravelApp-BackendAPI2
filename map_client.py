from config_files import keys
from urllib.parse import urlparse, parse_qsl
from urllib.parse import urlencode
import requests
import googlemaps
from datetime import datetime
import numpy
import math
from Linked_List import LinkedList

googleURL = "https://www.google.com/search?q="
GOOGLE_API_KEY = keys["GOOGLE_API_KEY"]

gmaps = googlemaps.Client(key=GOOGLE_API_KEY)
now = datetime.now() 

def get_latlng(address):
    """ Takes in a human-readable address and returns the lat,lng data
    """
    geocode_result = gmaps.geocode(address) 
    return geocode
# geocode_result = get_latlng('1700 Madison St.')
# print(geocode_result[0]['geometry']['location']['lat'],geocode_result[0]['geometry']['location']['lng'])

def unpack_decoded_coords(decoded_coordinates):
    """ Handles turning decoded coordinates that is an array of tuples into an array of-
        objects in the form of:
        ex: [{lat:<int>,lng:<int>}, etc...]
        This will allow the client side Google API to display markers again from a saved trip
    """
    return [{'lat':tupe[0],'lng':tupe[1]} for tupe in decoded_coordinates]


def get_directions(start,stop,region="US",mode="driving"):
    """ Gets directions data from google maps
    """
    directions_result = gmaps.directions(start,stop,
                                    region=region,
                                    mode=mode,)
    return directions_result 

def get_path_points(directions_data):
    steps = directions_data[0]["legs"][0]["steps"]
    path_points = {};   
    for i in range(1,len(steps)):
        path_points[i] = {"lat":steps[i-1]["start_location"]["lat"],"lng":steps[i-1]["start_location"]["lng"]}
    return path_points 
     
def sort_top_rated_locations(data,place):
    """ Takes data from nearby_places search results and returns the top rated place
        in the search category that is nearby.
        Returns: {name,rating,lat,lng,icon,place_id} object
        if there isn't anything it finds, then it returns None
        
        This function currently only returns one top rated place, but can be adjusted to easily 
        return a list of place objects if desired.
    """
    if data and data != []:
        d = data[0]
        if place and d.get('rating') and d['rating'] != 0:
            top_rated = {'name':d.get('name',place),'rating':d['rating'],'address':d.get('vicinity',"No Address Info On Google"),
                        'lat':d['geometry']['location']['lat'],'lng':d['geometry']['location']['lng'],
                        'icon':d['icon'],'place_id':d.get('place_id',"No Place-ID Info On Google")}
            return top_rated
    return None    
     

def get_places_nearby_sorted(coordinates, waypoints):
    """ Takes in an object of coordinates based on index {1:{lat,lng},2:{lat,lng} etc.} each index is a node along the route
        This function also calls the check_distance function to determine the distance between coordinates
            This allows the function to not return too many repeated data points
        
        Returns a dictionary of the top rated spots in each category along the route
        The dictionary looks like:
        {'0':[{'waypoint1':{'name':name str,'rating':rating int,'lat':lat int,'lng':lng int}}],1:[{place:{}}]} etc...
    """
    number_of_coords = len(coordinates.keys())
    last_index = number_of_coords - 1
    waypoint_json_data = LinkedList()
    stops = 0 ## used to keep track of how many stops we have found places at. 
    initial_coord = (coordinates[1]["lat"],coordinates[1]["lng"])
    last_coord = (coordinates[last_index]["lat"],coordinates[last_index]["lng"])
    steps = get_steps(initial_coord,last_coord,coordinates)
    
    starting_waypoint_details = get_starting_ending_details(waypoints,coordinates)
    ending_waypoint_details = get_starting_ending_details(waypoints,coordinates,dest="end")
    waypoint_json_data.push(starting_waypoint_details)
    
    for i in range(1,len(coordinates)): 
        if i != (steps * (stops+1)):   
            continue
        iterated_data = iterate_over_waypoints(waypoints,coordinates,i)
        stops += 1 
        if iterated_data and not waypoint_json_data.has_node_data(iterated_data):
            waypoint_json_data.push(iterated_data)
    if not waypoint_json_data.has_node_data(ending_waypoint_details):
        waypoint_json_data.push(ending_waypoint_details) 
    return waypoint_json_data
 

def get_starting_ending_details(waypoints,coords,dest="start"): 
    object_array = []
    number_of_coords = len(coords.keys())
    last_index = number_of_coords - 1
    initial_coord = (coords[1]["lat"],coords[1]["lng"]) 
    last_coord = (coords[last_index]["lat"],coords[last_index]["lng"])
    dest_coord = initial_coord if dest == "start" else last_coord
    for place in waypoints:
        place_details = gmaps.places_nearby(location=dest_coord,radius=24141,keyword=place)["results"]
        top_rated_details = sort_top_rated_locations(place_details,place)
        if not top_rated_details:
            continue
        place_obj = top_rated_details
        object_array.append(place_obj) 
    return object_array
    

def iterate_over_waypoints(waypoints,coordinates,i=None,initial_coord=None):
    """ Iterates over each waypoint and checks the nearby places to that waypoint
        Returns an array of objects to add to the json formatted object
        The place_count is in place here to index each object in the array of objects 
        that is in stored_objs
    """        
    object_array = []
    place_count = 0
    if i != None:
        for place in waypoints: 
            details = gmaps.places_nearby(location=(coordinates[i]["lat"],coordinates[i]["lng"]),radius=50000,keyword=place)['results']
            top_rated = sort_top_rated_locations(details,place)
            if not top_rated:
                continue
            obj = top_rated # {place details} 
            place_count += 1       
            object_array.append(obj)  
        return object_array  ## [{place details},{place details}]
    else:   
        for place in waypoints: 
            details = gmaps.places_nearby(location=initial_coord,radius=50000,keyword=place)['results']
            top_rated = sort_top_rated_locations(details,place)
            obj = top_rated
            object_array.append(obj)  
        return object_array

def urlEncoder(waypointnames):
    split_array = []
    "+".join(waypointnames[i:i+1] for i in range(0,len(waypointnames),2))
    return waypointnames

def createMarkerDataArrays(waypoints):
    infoWindowData = []
    placeDetails = []
    coordLocations = []
    currentNode = waypoints.head 
    while currentNode != None:
        if currentNode.data == []: 
            currentNode = currentNode.next_node
            continue 
        for node in currentNode.data:
            name = node['name']
            icon = node['icon']
            address = node['address']
            place_id = node['place_id']
            lat = node['lat']
            lng = node['lng']
            placeDetails.append({ 'name':name,
                                    'icon':icon,
                                    'place_id':place_id,
                                    'address':address,
                                    'web_url':f"{googleURL}{urlEncoder(name)}+{urlEncoder(address)}",
                                    'position':{"lat":lat,"lng":lng}
                                })
            # infoWindowData.append(f'''<div class="d-flex flex-column"> <h1>{node["name"]}</h1><blockquote>{node["address"]}''' + 
            #                       f'''</blockquote></div>''' + 
            #                       f'''<a href="{googleURL}{urlEncoder(node['name'])}+{urlEncoder(node["address"])}" target="_blank">Find It On The Web!</a>''')
            # coordLocations.append({"lat":lat,"lng":lng})
        currentNode = currentNode.next_node
        # [placeDetails,infoWindowData,coordLocations]
    return placeDetails


def get_steps(initial_coord,last_coord,coordinates):
    """ Takes in a starting point and end point coordinate, calculates
        a stops/distance ratio (step_ratio) and then returns a number of 
        steps based on that ratio percentage. The number of steps is how many 
        points to skip before checking nearby places again
    """
    num_of_coords = len(coordinates.keys())
    total_distance = get_distance_between_two_coords(initial_coord,last_coord)['distance']
    converted_array_length = num_of_coords * 1609
    step_ratio = (converted_array_length/total_distance)*100
    if step_ratio > 20 and step_ratio < 50:
        return math.floor(num_of_coords/7)
    elif step_ratio > 50:
        return math.floor(num_of_coords/5)
    else:
        return math.floor(num_of_coords/14)
    
def get_distance_between_two_coords(start,stop):
    """ Takes in two coordinates (lat,lng) and (lat,lng) and checks the distance between them
        Returns the distance value and time to travel. 
        Instead of returning true/false, I opened this function to be used for 
        all distance data
        returned data object looks like this:
        {'distance':value in meters,'duration':value in seconds}
        #{'elements':[{'distance':{'text':'km','value':num},'duration':{'text':hours mins,'value':num}}]}
    """
    distance_data = gmaps.distance_matrix(start,stop)
    return {'distance':distance_data['rows'][0]['elements'][0]['distance']['value'], #returns distance in meters
            'duration':distance_data['rows'][0]['elements'][0]['duration']['value']}  #returns duration in seconds
 
 
def extract_ids(search_result):
    """ Takes a search result and returns the place_ids of all the results
    """
    ids = []
    for place in search_result:
        ids.append(place['place_id'])
    return ids


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
