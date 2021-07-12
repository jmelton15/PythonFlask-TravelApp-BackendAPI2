""" Tests For Google API Interaction Functions in Map_Client.py """

# run these tests like:
#
#    python -m unittest test_googleAPI_functions.py

import os
from typing import List
from unittest import TestCase
from datetime import datetime
from config_files import keys
# from app import app
import map_client

os.environ['DATABASE_URL'] = "postgresql:///dtri_test"
GOOGLE_SERVER_API_KEY = keys["GOOGLE_SERVER_API_KEY"]
now = datetime.now()

class GoogleApiTestCase(TestCase):
    
    def setUp(self):
        """ Create test client and add sample testing data"""
        self.faux_nearby_places_data = [{'business_status': 'OPERATIONAL', 'geometry': {'location': {'lat': 42.9544878, 'lng': -85.4886045}, 'viewport': {'northeast': {'lat': 42.95579032989272, 'lng': -85.48719497010727}, 'southwest': {'lat': 42.95309067010728, 'lng': -85.48989462989272}}}, 'icon': 'https://maps.gstatic.com/mapfiles/place_api/icons/v1/png_71/shopping-71.png', 'name': "Scooper's Ice Cream Shoppe", 'opening_hours': {'open_now': True}, 'photos': [{'height': 3456, 'html_attributions': ['<a href="https://maps.google.com/maps/contrib/116817238352139987816">Tim Krueger</a>'], 'photo_reference': 'ATtYBwL-fZR1dojdwfvscLmrr8CapQGd5YBadZ2VYJNLxwc9G1ZrnQPIAW0uFI2MwMjFAAmqSHwwqmBb_vHEdtqn4Sqh2SCNlgdO6Tuk9bFnrNv4geg8imeGnXa1gSMtgiYDMov6DgpY7FScUSWa8uABQ8AraTji9rRk-vYpHuva7hlieB6K', 'width': 4608}], 'place_id': 'ChIJc265W7dRGIgRyZ5tMyesmSY', 'plus_code': {'compound_code': 'XG36+QH Ada, Michigan', 'global_code': '86JPXG36+QH'}, 'price_level': 1, 'rating': 5.0, 'reference': 'ChIJc265W7dRGIgRyZ5tMyesmSY', 'scope': 'GOOGLE', 'types': ['food', 'point_of_interest', 'store', 'establishment'], 'user_ratings_total': 105, 'vicinity': '591 Ada Dr SE, Ada'}]
        self.waypoints = ["Burgers","Ice Cream"]
        self.coordinates = [{"lat":42.9634,"lng":-85.6681},{'lat':41.7075,'lng':-86.8950},{'lat':41.8781,'lng':-87.6298}]
        self.initial_coord = (42.9634,-85.6681)
        self.last_coord = (41.8781,-87.6298)
        
        
    def tearDown(self):
        """ Reset test sample data"""
        self.nearby_places_data = []
    

    def test_package_nearby_place_data(self):
        """ Tests that the function can take data from a nearby search result and return the proper object
        This is the last function to run when returning the data back to the client side.
        What is returned by this is what will be used to display to the users
        
        RETURN Data should look like: 
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
        place_object = map_client.package_nearby_place_data(self.faux_nearby_places_data)
        self.assertEqual(place_object['name'],"Scooper's Ice Cream Shoppe");
        
        
    """
    READ BEFORE UNCOMMENTING THE FUNCTIONS BELOW!!!!!
    
    The functions below are tested by running actual requests to google. 
    NOTE -> ONLY RUN THIS IF YOU REALLY NEED. It Will Use Your API key quota.    
    """    

    # def test_get_directions(self):
    #     """ Tests that a directions result object is returned from a google api request
        
    #     This function is tested by running actual requests to google. 
    #     NOTE -> ONLY RUN THIS IF YOU REALLY NEED. It Will Use Your API key quota.
    #     """    
    #     directions_result = map_client.get_directions("Michigan","Chicago");
    #     self.assertEqual(type(directions_result),dict)
    
    # def test_get_path_points(self):
    #     """ Tests that the coords from a directions result are returned 
    #        Return type from this function should be a dict in the form:
    #        [0:{lat,lng},1:{lat,lng},etc]
    #     """
    #     directions_result = map_client.get_directions("Michigan","Chicago");
    #     coords = map_client.get_path_points(directions_result)
    #     self.assertEqual(type(coords),dict)
    #     self.assertEqual(type(coords[0]['lat']),int)
    
    # def test_get_total_distance(self):
    #     """Tests if an integer is returned between two locations 
    #        Number should be in the 10-thousands at least (for the majority of user searches)
           
    #        This function is tested by running actual requests to google. 
    #     NOTE -> ONLY RUN THIS IF YOU REALLY NEED. It Will Use Your API key quota.
    #     """
    #     directions_result = map_client.get_directions("Michigan","Chicago");
    #     distance = map_client.get_total_distance(directions_result)
    #     self.assertEqual(type(distance),int)
 
    # def test_get_top_rated_places(self):
    #     """ Tests that this function is able to make requests to google and return a final object
    #          That conains all the top rated places it has found along the route
             
    #         This function is tested by running actual requests to google. 
    #         NOTE -> ONLY RUN THIS IF YOU REALLY NEED. It Will Use Your API key quota.
            
    #         The final object should be in the form of:
    #         [{place1:[{location1},{location2},etc],place2:[]}]
    #     """
    #     directions_result = map_client.get_directions("Michigan","Chicago");
    #     distance = map_client.get_total_distance(directions_result)
    #     coords = map_client.get_path_points(directions_result)
        
    #     final_place_object = map_client.get_top_rated_places(coords,["parks"],distance)
    #     self.assertEqual(type(final_place_object),dict)
    #     self.assertEqual(type(final_place_object['parks']),list)
