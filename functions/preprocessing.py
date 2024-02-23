import numpy as np
import pandas as pd
import googlemaps
import datetime
import inflect
import itertools
import streamlit as st
import streamlit.components.v1 as components

from datetime import datetime

google_api_key = st.secrets["GOOGLE_API_KEY"]
gmaps = googlemaps.Client(key=google_api_key)


def generate_permutation_duration(permutations_list,postal_code_distance_matrix_dict,postal_code_list):
    duration_of_full_route_dict = {}
    for possible_routes in permutations_list:
        duration_of_full_route=[]
        if possible_routes[0] == postal_code_list[0] and possible_routes[-1] == postal_code_list[-1]:
            for index in range(len(possible_routes)-1):
                # Cannot have Origin and Destination same
                if possible_routes[index] != possible_routes[index+1]:
                    ori_dest_pair = f"{possible_routes[index]},{possible_routes[index+1]}"
                    # If origin - dest pair distance inside dict, call dict to return value
                    if ori_dest_pair in postal_code_distance_matrix_dict:
                        result = postal_code_distance_matrix_dict[ori_dest_pair]
                    # Else switch origin - dest to dest - origin, call dict to return value
                    else:
                        result = postal_code_distance_matrix_dict[f"{possible_routes[index+1]},{possible_routes[index]}"]
                    duration_of_full_route.append(result)

            duration_of_full_route_dict[f"{possible_routes}"] = sum(duration_of_full_route)

    return duration_of_full_route_dict

def generate_pair_distance(postal_code_list):
    postal_code_distance_matrix_dict = {}
    now = datetime.now()

    pairs = list(itertools.combinations(postal_code_list, 2))
    pairs = [list(t) for t in pairs]

    for pair in pairs:

        ori = f"Singapore {pair[0]}"
        dest = f"Singapore {pair[1]}"

        if ori != dest:
            duration_in_traffic = gmaps.distance_matrix(ori,dest,mode="driving",departure_time=now,traffic_model="best_guess",region="SG")['rows'][0]['elements'][0]['duration_in_traffic']['value']
            postal_code_distance_matrix_dict[f"{pair[0]},{pair[1]}"]=duration_in_traffic

    return postal_code_distance_matrix_dict

def generate_ordinal_suffix(i):
        ordinal_suffix = inflect.engine()
        return ordinal_suffix.ordinal(i)


def generate_textboxes(num_textboxes):
    textboxes = []
    for i in range(num_textboxes):
        if i == 0:
            textbox_value = st.text_input(f":green[Start Point]", "119074")
            textboxes.append(textbox_value)

        elif i == (num_textboxes-1):
            textbox_value = st.text_input(f":red[End Point]", "119074")
            textboxes.append(textbox_value)

        else:
            textbox_value = st.text_input(f"House Visit {i}", "")
            textboxes.append(textbox_value)
    return textboxes

def validate_postal_code(postal_code):

    response = gmaps.addressvalidation(postal_code, regionCode="SG")
    confirmation_level = response['result']['address']['addressComponents'][0]['confirmationLevel']
    result = confirmation_level == "CONFIRMED" or confirmation_level == "UNCONFIRMED_BUT_PLAUSIBLE"

    return result
