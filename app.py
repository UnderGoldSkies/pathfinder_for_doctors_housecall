import streamlit as st
import googlemaps
import numpy as np
import pandas as pd
import itertools
import datetime
import streamlit.components.v1 as components

from datetime import datetime
from itertools import permutations

from htmlTemplates import directions_map

google_api_key = st.secrets["GOOGLE_API_KEY"]
gmaps = googlemaps.Client(key=google_api_key)


@st.cache_data
def generate_permutation_duration(permutations_list,postal_code_distance_matrix_dict,postal_code_list):
    duration_of_full_route_dict = {}
    for possible_routes in permutations_list:
        duration_of_full_route=[]
        if possible_routes[0] == postal_code_list[0] and possible_routes[-1] == postal_code_list[-1]:
            for index in range(len(possible_routes)-1):
                ori_dest_pair = f"{possible_routes[index]},{possible_routes[index+1]}"
                if ori_dest_pair in postal_code_distance_matrix_dict:
                    result = postal_code_distance_matrix_dict[ori_dest_pair]
                else:
                    result = postal_code_distance_matrix_dict[f"{possible_routes[index+1]},{possible_routes[index]}"]
                duration_of_full_route.append(result)

            duration_of_full_route_dict[f"{possible_routes}"] = sum(duration_of_full_route)
    return duration_of_full_route_dict

@st.cache_data
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


def generate_textboxes(num_textboxes):
    textboxes = []
    for i in range(num_textboxes):
        textbox_value = st.text_input(f"Postal Code {i + 1}", f"119074")
        textboxes.append(textbox_value)
    return textboxes

def validate_postal_code(postal_code):
    # Replace this with your actual validation logic using gmaps or other methods
    # Return True if the postal code is valid, False otherwise
    return gmaps.addressvalidation(postal_code, regionCode="SG")['result']['address']['addressComponents'][0]['confirmationLevel'] == "CONFIRMED"

def main():

    # header
    st.title("Dr Ant-Thony :ant:")
    mode = "place"
    location = "119074"
    st.write("Optimizing Order of Visits for Maximum Efficiency :red_car:")

    placeholder = st.image('DisplayPic.jpg', caption='Dr Anthony')

    shortest_route = None

    # Validation flag
    all_validated = True

    postal_code_distance_matrix_dict ={}
    duration_of_full_route_dict ={}

    with st.sidebar:
        st.subheader('List of Postal Codes to Visit :derelict_house_building:')

        # Get the number of textboxes from the user
        num_textboxes = st.slider(":violet[Input the total of Postal Code:]", 1, 10, 5)

        # Generate and display the textboxes
        postal_code_list = generate_textboxes(num_textboxes)

        if any(element == "" for element in postal_code_list):
            st.write("There is at least one missing postal code.")
        else:
            invalid_postal_codes = []
            for i, value in enumerate(postal_code_list):
                if validate_postal_code(value) != True:
                    st.write(f"Postal Code box {i + 1} is not valid")
                    invalid_postal_codes.append(value)

            if not invalid_postal_codes:
                st.sidebar.write("All postal codes are valid.")

                if st.sidebar.button("Optimize"):
                    placeholder = st.empty()
                    with st.spinner("Ant-Thony is Working on it"):
                        postal_code_distance_matrix_dict = generate_pair_distance(postal_code_list)
                        permutations_list = list(permutations(postal_code_list))
                        duration_of_full_route_dict = generate_permutation_duration(permutations_list,postal_code_distance_matrix_dict,postal_code_list)
                        shortest_route = min(duration_of_full_route_dict, key=duration_of_full_route_dict.get)
                        shortest_route = shortest_route.replace("(","")
                        shortest_route = shortest_route.replace(")","")
                        shortest_route = shortest_route.split(",")


    if shortest_route != None:
        for i in range(len(shortest_route)-1):
            st.write(f"Order {i+1}")
            st.components.v1.html(directions_map.format(ori=shortest_route[i],dest=shortest_route[i+1],google_api_key=google_api_key), height=400)





if __name__ == '__main__':
    main()
