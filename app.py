import streamlit as st
import googlemaps
import numpy as np
import pandas as pd
import itertools
import datetime

import pydeck as pdk
from datetime import datetime
from itertools import permutations

google_api_key =
gmaps = googlemaps.Client(key=google_api_key)

@st.cache_data
def generate_permutation_duration(permutations_list,postal_code_distance_matrix_dict):
    duration_of_full_route_dict = {}
    for possible_routes in permutations_list:
        duration_of_full_route=[]
        if possible_routes[0] == '119228' and possible_routes[-1] == '119228':
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
        textbox_value = st.text_input(f"Postal Code {i + 1}", f"119228")
        textboxes.append(textbox_value)
    return textboxes

def validate_postal_code(postal_code):
    # Replace this with your actual validation logic using gmaps or other methods
    # Return True if the postal code is valid, False otherwise
    return gmaps.addressvalidation(postal_code, regionCode="SG")['result']['address']['addressComponents'][0]['confirmationLevel'] == "CONFIRMED"

def main():

        # header
    st.header("Dr Ant-Thony")

    st.subheader("Optimizing your home visits route")

    # Validation flag
    all_validated = True

    postal_code_distance_matrix_dict ={}
    duration_of_full_route_dict ={}


    location = [37.7749, -122.4194]
    # Create a Google Maps Deckgl layer
    layer = pdk.Layer(
        "GoogleMapsLayer",
        google_api_key,
        zoom=12,
        center=location,
        id="google-maps",
    )

    # Create a Pydeck Deck instance
    view_state = pdk.ViewState(
        latitude=location[0],
        longitude=location[1],
        zoom=12,
        bearing=0,
        pitch=45,
    )

    r = pdk.Deck(
        layers=[layer],
        initial_view_state=view_state,
    )

    # Display the map using st
    st.pydeck_chart(r)



    with st.sidebar:
        st.subheader("List of Postal Codes to Visit")

        # Get the number of textboxes from the user
        num_textboxes = st.slider("Select the total of Postal Code:", 1, 10, 3)

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
                    with st.spinner("Ant-Thony is Working on it"):
                        postal_code_distance_matrix_dict = generate_pair_distance(postal_code_list)
                        permutations_list = list(permutations(postal_code_list))
                        duration_of_full_route_dict = generate_permutation_duration(permutations_list,postal_code_distance_matrix_dict)
                        shortest_route = min(duration_of_full_route_dict, key=duration_of_full_route_dict.get)
                        #st.write(f"duration_of_full_route_dict : {duration_of_full_route_dict}")
                        st.write(f'shortest_route : {shortest_route}')





        # # Check if the Analyse button is pressed
        # if st.button("Optimize"):


        #      with st.spinner("Analyzing"):


if __name__ == '__main__':
    main()
