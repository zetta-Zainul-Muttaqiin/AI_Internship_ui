import streamlit as st
import os
import pandas as pd
from cv_upload import cv_extractor

def save_uploaded_file(uploaded_file):
    # Create the "uploads" directory if it doesn't exist
    if not os.path.exists("uploads"):
        os.makedirs("uploads")

    # Save the uploaded file to disk
    file_path = os.path.join("uploads", uploaded_file.name)
    with open(file_path, "wb") as f:
        f.write(uploaded_file.getbuffer())
    return file_path

def format_description(description_list):
    # Add '-' before each description item
    formatted = '\n'.join(f"- {desc}" for desc in description_list)
    return formatted

def show_main_content():
    st.title("LeBon Stage")

    # File uploader
    uploaded_file = st.file_uploader("Choose a PDF file", type="pdf")

    if uploaded_file:
        # Save the uploaded file to disk
        file_path = save_uploaded_file(uploaded_file)
        with st.spinner("Processing your CV..."):
            # Process the uploaded PDF file
            file_contents = cv_extractor(file_path)
            # You can add any further processing or display of the file contents here
            st.success("File processed successfully!")
            # Displaying the CV data in a table format using Streamlit
            st.write(file_contents)
            
            # Summary
            st.header("Summary")
            summary = file_contents['cv']['summary']
            # Use text_area for the summary
            st.text(f"Name: {summary['name']}")
            st.text(f"Location: {summary['location']}")
            st.text(f"Phone: {summary['phone']}")
            st.text(f"Email: {summary['email']}")
            summary_text = st.text_area("Summary", value=summary['summary'], key="summary")

            # Work Experience
            st.header("Work Experience")
            for experience in file_contents['cv']['work_experience']:
                st.subheader(experience['company_name'])
                st.text(f"Job Title: {experience['job_title']}")
                st.text(f"Date: {experience['date']}")
                st.text("Description:")
                formatted_description = format_description(experience['description'])
                st.text_area(label="", value=formatted_description, key=f"work_{experience['company_name']}_{experience['date']}")

            # Education
            st.header("Education")
            for edu in file_contents['cv']['education']:
                st.subheader(edu['school_name'])
                st.text(f"Date: {edu['date']}")
                st.text(f"Degree/Major: {edu['degree_major']}")
                st.text(f"Score: {edu['score']}")
                st.text("Description:")
                formatted_description = format_description(edu['description'])
                st.text_area(label="", value=formatted_description, key=f"edu_{edu['school_name']}_{edu['date']}")

            # Projects
            st.header("Projects")
            for project in file_contents['cv']['project']:
                st.subheader(project['project_name'])
                st.text(f"Date: {project['date']}")
                st.text("Description:")
                formatted_description = format_description(project['description'])
                st.text_area(label="", value=formatted_description, key=f"project_{project['project_name']}_{project['date']}")

            # Skills
            st.header("Skills")
            for skill in file_contents['cv']['skills']:
                st.text(f"- {skill}")
    else:
        st.write("Please upload your CV here.")

# Streamlit UI
def main():
    show_main_content()

if __name__ == "__main__":
    main()