import streamlit as st
import googlemaps
import numpy as np
import pandas as pd
import itertools
import datetime
import streamlit.components.v1 as components
import inflect

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
                # Cannot have Origin and Destination same
                if possible_routes[index] != possible_routes[index]:
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
            textbox_value = st.text_input(f"House Visit {i}", "119074")
            textboxes.append(textbox_value)
    return textboxes

def validate_postal_code(postal_code):
    # Replace this with your actual validation logic using gmaps or other methods
    # Return True if the postal code is valid, False otherwise
    return gmaps.addressvalidation(postal_code, regionCode="SG")['result']['address']['addressComponents'][0]['confirmationLevel'] == "CONFIRMED"

def main():
    pg_title = "Dr Ant-Thony :ant:"
    pg_icon = ":compass:"
    st.set_page_config(page_title=pg_title, page_icon=pg_icon, layout="centered", initial_sidebar_state="expanded", menu_items=None)
    # header
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
        st.title("Dr Ant-Thony :ant:")

        st.subheader(':violet[Step 1]')
        # Get the number of textboxes from the user
        num_textboxes = st.slider("Select Number of Visits::derelict_house_building:", 3, 10, 5)
        st.subheader(':violet[Step 2]')
        st.write('Input Address name/ Postal code to Visit')
        # Generate and display the textboxes
        postal_code_list = generate_textboxes(num_textboxes)

        # Check for missing boxes
        if any(element == "" for element in postal_code_list):
            st.write(":orange[There is at least one missing visits.]")
        # Check for any repeat of visits
        if len(set(postal_code_list[1:-1])) < len(postal_code_list[1:-1]):
            st.write(":orange[Duplicated Visits Detected, Please Check Entry]")
        else:
            invalid_postal_codes = []
            for i, value in enumerate(postal_code_list):
                if validate_postal_code(value) != True:
                    if i == 0:
                        st.write(f":red[Start Point is not valid]")
                    elif i == (num_textboxes-1):
                        st.write(f":red[End Point is not valid]")
                    else:
                        st.write(f":red[House Visit {i + 1} is not valid]")
                    invalid_postal_codes.append(value)

            if not invalid_postal_codes:
                st.sidebar.write(":green[All Address are valid.]")
                st.subheader(':violet[Step 3]')
                st.write('Press "Optimize" to generate Visit Plan')
                if st.sidebar.button("Optimize"):
                    placeholder.empty()
                    with st.spinner("Ant-Thony is Working on it"):
                        postal_code_distance_matrix_dict = generate_pair_distance(postal_code_list)
                        permutations_list = list(permutations(postal_code_list))
                        duration_of_full_route_dict = generate_permutation_duration(permutations_list,postal_code_distance_matrix_dict,postal_code_list)
                        shortest_route = min(duration_of_full_route_dict, key=duration_of_full_route_dict.get)
                        shortest_route = shortest_route.replace("(","")
                        shortest_route = shortest_route.replace(")","")
                        shortest_route = shortest_route.split(",")
                    st.markdown("""
                        <style>
                            section[data-testid="stSidebar"][aria-expanded="true"]{
                                display: none;
                            }
                        </style>
                        """, unsafe_allow_html=True)


    if shortest_route != None:

        for i in range(len(shortest_route)-1):
            if i == len(shortest_route)-2:
                st.markdown(f"Last Destination:  \n	:large_green_circle: :green[From Address {shortest_route[i]}] :large_red_square: :red[To Address {shortest_route[i+1]}]")
            else:
                st.markdown(f"{generate_ordinal_suffix(i+1)} Visit:  \n	:large_green_circle: :green[From Address {shortest_route[i]}] :large_red_square: :red[To Address {shortest_route[i+1]}]")
            st.components.v1.html(directions_map.format(ori=shortest_route[i],dest=shortest_route[i+1],google_api_key=google_api_key), height=400)

        if st.button(":red[Change Address]"):
            shortest_route = None
            st.markdown("""
                <style>
                    section[data-testid="stSidebar"][aria-expanded="true"]{
                        display: initial;  /* Set it to 'block' or 'initial' to show the sidebar */
                    }
                </style>
                """, unsafe_allow_html=True)





if __name__ == '__main__':
    main()
