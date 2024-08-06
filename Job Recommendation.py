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

if "results" not in st.session_state:
    st.session_state.results = {}
if "keywords" not in st.session_state:
    st.session_state.keywords = ""
if "location" not in st.session_state:
    st.session_state.location = ""
if "category" not in st.session_state:
    st.session_state.category = ""
if "education" not in st.session_state:
    st.session_state.education = ""
if "duration" not in st.session_state:
    st.session_state.duration = ""

st.title("LeBon Stage")

# File uploader
st.title("Job Recommendation System")

cols = st.columns([6,2,1],)
if cols[2].button("Reset"):
    if 'query' in st.session_state:
        st.session_state.query = None
        st.session_state.results = None 
# Input for the query
keywords = st.text_input("Enter your keywords")
if keywords:
    st.session_state.keywords = keywords

location = st.selectbox("Location", list_of_locations)
if location:
    st.session_state.location = location

category = st.selectbox("Job Category", list_of_category)
if category:
    st.session_state.category = category

education = st.selectbox("Level of Education", list_of_education)
if education:
    st.session_state.education = education

duration = st.selectbox("Internship Duration", list_of_durations)
if duration:
    st.session_state.duration = duration



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
        "keywords": keywords,
        "location": location if location else None,
        "category": category if category else None,
        "education": education if education else None,
        "duration": duration if duration else None
    }


# Search button
if st.button("Search") and st.session_state.query != curr_query:
    st.session_state.query = curr_query
    # Run the vector search process
    st.session_state.results = run_vector_search(st.session_state.query)
        

if ('data' in st.session_state.results) or ('data_recommend' in st.session_state.results):
    # Create a DataFrame from the results
    results = st.session_state.results
    data = results["data"]
    df = pd.DataFrame(data)
    print("LEN_data : ", len(st.session_state.results))
    # Selecting relevant columns for display
    columns_to_display = [
            "job_role", "job_category", "location", 
            "education_level", "job_contract", "description"
        ]
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
            st.page_link('pages/CV_Upload.py.py', label=f"Apply as {job_role}")


    if len(df) < 5:
        st.text(f"Just Found {len(df)} Exactly Internship Offer Currently")
    
        st.write("Our Recommendation, based on your search:")
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
                st.page_link('pages/CV_Upload.py.py', label=f"Apply as {job_role}")
