import streamlit as st
from itertools import permutations
import googlemaps
from htmlTemplates import directions_map
from functions.preprocessing import generate_ordinal_suffix,generate_pair_distance,generate_permutation_duration,generate_textboxes,validate_postal_code
google_api_key = st.secrets["GOOGLE_API_KEY"]
gmaps = googlemaps.Client(key=google_api_key)

def main():
    # Initialize session_state if not already done
    if 'validation_flag' not in st.session_state:
        st.session_state.validation_flag = False

    pg_title = "Dr Ant-Thony :ant:"
    pg_icon = ":compass:"
    st.set_page_config(page_title=pg_title, page_icon=pg_icon, layout="centered", initial_sidebar_state="expanded", menu_items=None)
    # header
    mode = "place"
    location = "119074"
    st.write("Optimize Order of Visits:red_car:")

    placeholder = st.image('DisplayPic.jpg', caption='Dr Anthony')

    shortest_route = None

    # Validation flag
    invalid_postal_codes = []
    postal_code_distance_matrix_dict ={}
    duration_of_full_route_dict ={}

    with st.sidebar:
        st.title("Dr Ant-Thony :ant:")
        st.subheader(':green[Enter List of Address to Visit and Dr Ant-Thony will plan it out]')
        st.header(':blue[Instructions:] ')
        st.header(':blue[Follow :violet[Step 1 to Step 3]]')
        st.header(':blue[To Generate Order of Visits]')
        st.header(':violet[Step 1]')
        # Get the number of textboxes from the user
        num_textboxes = st.slider("Slide to Select Number of Patients you need to visit today::derelict_house_building:", 3, 10, 5)
        st.header(':violet[Step 2]')
        st.write('Input Address name/ Postal code to Visit and Press Validate Address')
        # Generate and display the textboxes
        postal_code_list = generate_textboxes(num_textboxes+2)

        if st.sidebar.button("Validate Address"):
            # Check for missing boxes
            if any(element == "" for element in postal_code_list):
                st.write(":orange[There is at least one missing visits.]")
            # Check for any repeat of visits
            if len(set(postal_code_list[1:-1])) < len(postal_code_list[1:-1]):
                st.write(":orange[Duplicated House Visit Detected, Please Check Entry]")
            else:
                for i, value in enumerate(postal_code_list):
                    result = validate_postal_code(value)
                    if result == "CONFIRMED":
                        continue
                    elif result == "UNCONFIRMED_BUT_PLAUSIBLE":
                        if i == 0:
                            st.write(f":red[Start Point Address is not fully validated in google maps, Do check before Optimizing]")
                        elif i == (num_textboxes-1):
                            st.write(f":red[End Point Address is not fully validated in google maps, Do check before Optimizing]")
                        else:
                            st.write(f":red[House Visit {i} is not fully validated in google maps, Do check before Optimizing]")
                    else:
                        if i == 0:
                            st.write(f":red[Start Point is not valid]")
                        elif i == (num_textboxes-1):
                            st.write(f":red[End Point is not valid]")
                        else:
                            st.write(f":red[House Visit {i} is not valid]")
                        invalid_postal_codes.append(value)

                if invalid_postal_codes == []:
                    st.session_state.validation_flag = True


        st.header(':violet[Step 3]')
        st.write('Press "Optimize" to generate Visit Plan')
        # Enable/disable based on the value of validation flag
        optimize_button_enabled = st.session_state.validation_flag

        optimize_button_clicked = st.sidebar.button("Optimize", key="optimize_button", disabled=not optimize_button_enabled)
        if optimize_button_clicked:
            if optimize_button_enabled == False:
                st.sidebar.write("Ensure Address are Valided before Optimizing")
            else:
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
            section[data-testid='stSidebar'] > div {
                height: 100%;
                width: 400px;
                position: relative;
                z-index: 1;
                top: 0;
                left: -5;
                background-color: #ADD8E6;
                overflow-x: hidden;
                transition: 0.5s ease;
                padding-top: -10px;
                white-space: nowrap;
            <style>
                """, unsafe_allow_html= True)


if __name__ == '__main__':
    main()
