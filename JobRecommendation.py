import streamlit as st
import os
import pandas as pd
from cv_upload import cv_extractor
from job_recommend import run_vector_search
from setup import (
    list_of_category,
    list_of_durations,
    list_of_education,
    list_of_locations
)

st.set_page_config(
    page_title="search"
)

    # Initialize session state for inputs and results if not already set
if 'keywords' not in st.session_state:
    st.session_state.keywords = ""
if 'location' not in st.session_state:
    st.session_state.location = ""
if 'category' not in st.session_state:
    st.session_state.category = ""
if 'education' not in st.session_state:
    st.session_state.education = ""
if 'duration' not in st.session_state:
    st.session_state.duration = ""
if 'results' not in st.session_state:
    st.session_state.results = {}

st.title("LeBon Stage")

# File uploader
st.title("Job Recommendation System")

cols = st.columns([6,2,1],)
if 'query' in st.session_state:
    if cols[2].button("Reset"):
        st.session_state.keywords = ""
        st.session_state.location = ""
        st.session_state.category = ""
        st.session_state.education = ""
        st.session_state.duration = ""
        st.session_state.results = {}
        st.rerun() # Force rerun to update the state

# Input for the query
st.session_state.keywords = st.text_input("Enter your keywords", st.session_state.keywords)
st.session_state.location = st.selectbox("Location", list_of_locations, index=list_of_locations.index(st.session_state.location) if st.session_state.location else 0)
st.session_state.category = st.selectbox("Job Category", list_of_category, index=list_of_category.index(st.session_state.category) if st.session_state.category else 0)
st.session_state.education = st.selectbox("Level of Education", list_of_education, index=list_of_education.index(st.session_state.education) if st.session_state.education else 0)
st.session_state.duration = st.selectbox("Internship Duration", list_of_durations, index=list_of_durations.index(st.session_state.duration) if st.session_state.duration else 0)



# Combine all inputs into a query
curr_query = {
        "keywords": st.session_state.keywords if st.session_state.keywords else "",
        "location": st.session_state.location if st.session_state.location else None,
        "category": st.session_state.category if st.session_state.category else None,
        "education": st.session_state.education if st.session_state.education else None,
        "duration": st.session_state.duration if st.session_state.duration else None
}

if 'query' not in st.session_state:
    
    st.session_state.query = {
        "keywords": st.session_state.keywords if st.session_state.keywords else None,
        "location": st.session_state.location if st.session_state.location else None,
        "category": st.session_state.category if st.session_state.category else None,
        "education": st.session_state.education if st.session_state.education else None,
        "duration": st.session_state.duration if st.session_state.duration else None
    }


# Search button
if st.button("Search") and st.session_state.query != curr_query:
    st.session_state.query = curr_query
    # Run the vector search process
    st.session_state.results = run_vector_search(st.session_state.query)
        

columns_to_display = [
        "job_role", "job_category", "location", 
        "education_level", "job_contract", "description"
    ]
if ('data' in st.session_state.results) or ('data_recommend' in st.session_state.results):
    # Create a DataFrame from the results
    results = st.session_state.results
    if results['data']:
        data = results["data"]
        df = pd.DataFrame(data)
        print("LEN_data : ", len(st.session_state.results))
        # Selecting relevant columns for display
        print("COLUMNS: ", df.columns)
        # Ensuring columns exist in the DataFrame
        valid_columns = [col for col in columns_to_display if col in df.columns]

        if valid_columns:
            df_display = df[valid_columns]
            
            # Renaming columns for better readability
            df_display.columns = [
                "Job Role", "Job Category", "Location", 
                "Education Level", "Job Contract", "Description"
            ]    
        # Displaying the DataFrame with select buttons
            data_display = st.dataframe(
                df_display,
                on_select='rerun',
                selection_mode=["single-row"],
                key="list_data"
            )

            if len(data_display.selection['rows']):
                selected_row = data_display.selection['rows'][0]
                desc = df_display.iloc[selected_row]['Description']
                job_role = df_display.iloc[selected_row]['Job Role']

                st.write("Selected data: ", len(data_display.selection['rows']))
                st.session_state.job_info = {
                    'description': desc,
                    'job_role': job_role
                    }
                st.page_link('pages/CV_Upload.py', label=f"Apply as {job_role}")

    else:
        st.text("No internships matched your keyword.")

    if len(results['data']) < 5:
        st.text(f"Just Found {len(results['data'])} Exactly Internship Offer Currently")
    
        st.write("You can check our recommendations based on your search below:")
        # Create a DataFrame from the results
        data_recom = results["data_recommend"]
        df_recom = pd.DataFrame(data_recom)

        valid_columns = [col for col in columns_to_display if col in df_recom.columns]

        if valid_columns:
            df_display_recom = df_recom[valid_columns]
            
            # Renaming columns for better readability
            df_display_recom.columns = [
                "Job Role", "Job Category", "Location", 
                "Education Level", "Job Contract", "Description"
            ]  

            # Displaying the DataFrame with select buttons
            data_display_recomm = st.dataframe(
                df_display_recom,
                on_select='rerun',
                selection_mode=["single-row"],
                key="list_data_recomm"
            )

            if len(data_display_recomm.selection['rows']):
                selected_row = data_display_recomm.selection['rows'][0]
                desc = df_display_recom.iloc[selected_row]['Description']
                job_role = df_display_recom.iloc[selected_row]['Job Role']

                st.write("Selected data: ", len(data_display_recomm.selection['rows']))
                st.session_state.job_info = {
                    'description': desc,
                    'job_role': job_role
                    }
                st.page_link('pages/CV_Upload.py', label=f"Apply as {job_role}")
