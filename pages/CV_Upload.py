import streamlit as st
import os
import pandas as pd
from cv_upload import cv_extractor
from cv_generator import summary_ai, work_experience_ai, education_ai, project_ai, skills_ai

os.environ['Path'] = 'poppler-24.02.0\Library\bin'
api_config = st.secrets["api"]
openai_api_key = api_config["openai_api_key"]
os.environ['OPENAI_API_KEY'] = openai_api_key
if 'job_info' not in st.session_state:
    st.session_state.job_info = {
                'description': "",
                'job_role': ""
    } 

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

def update_summary(summary_data):
    st.session_state['summary_data'] = summary_data

def update_work_experience(data):
    st.session_state[data['key']] = data

def update_education(data):
    st.session_state[data['key']] = data

def update_project(data):
    st.session_state[data['key']] = data

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
            
            def format_description(description_list):
                # Add '-' before each description item
                formatted = '\n'.join(f"- {desc}" for desc in description_list)
                return formatted

            # Displaying the CV data in a table format using Streamlit
            # Summary
            st.header("Summary")
            summary = file_contents['cv']['summary']
            # Use text_area for the summary
            keyword_text_summary = ""
            st.text(f"Name: {summary['name']}")
            st.text(f"Location: {summary['location']}")
            st.text(f"Phone: {summary['phone']}")
            st.text(f"Email: {summary['email']}")
            cols = st.columns([4, 1, 1])
            if 'summary_data' not in st.session_state:
                summary_text = cols[0].text_area(label="", value=summary['summary'], key="summary")    
            else:
                summary_text = cols[0].text_area(label="", value=st.session_state['summary_data']['summary'], key="summary")
            if cols[1].button("Generate AI", key="edit_summary"):
                st.session_state.code_executed = True
                keyword_text_summary = cols[0].text_input(label="", placeholder="Enter your keywords", key="summary_keywords")
                summary_ai_result = summary_ai(summary_text, keyword_text_summary, st.session_state.job_info['description'])
                st.markdown("""
                    <style>
                    .stButton button {
                        height: 100%;
                    }
                    .stColumn div {
                        height: 100%;
                        display: flex;
                        align-items: center;
                    }
                    .stColumn {
                        display: flex;
                        flex-direction: column;
                    }
                    </style>
                    """, unsafe_allow_html=True)

                # Display the summaries and buttons
                for description, summary in summary_ai_result["summary_ai_result"].items():
                    cols2 = st.columns([2, 5, 1])
                    cols2[0].write(description.capitalize() + ":")
                    cols2[1].write(summary)
                    with cols2[2]:
                        st.button('➕', on_click=lambda d={'summary_ai_result': summary_ai_result, 'summary': summary}: update_summary(d), key=description)
            elif 'summary_data' in st.session_state:
                st.session_state.code_executed = True
                keyword_text_summary = cols[0].text_input(label="", placeholder="Enter your keywords", key="summary_keywords")
                summary_ai_result = st.session_state['summary_data']['summary_ai_result']
                st.markdown("""
                    <style>
                    .stButton button {
                        height: 100%;
                    }
                    .stColumn div {
                        height: 100%;
                        display: flex;
                        align-items: center;
                    }
                    .stColumn {
                        display: flex;
                        flex-direction: column;
                    }
                    </style>
                    """, unsafe_allow_html=True)

                # Display the summaries and buttons
                for description, summary in summary_ai_result["summary_ai_result"].items():
                    cols2 = st.columns([2, 5, 1])
                    cols2[0].write(description.capitalize() + ":")
                    cols2[1].write(summary)
                    with cols2[2]:
                        st.button('➕', on_click=lambda d={'summary_ai_result': summary_ai_result, 'summary': summary}: update_summary(d), key=description)
            # Work Experience
            st.header("Work Experience")
            experience_counter = 0
            for experience in file_contents['cv']['work_experience']:
                experience_counter += 1
                key = "work_experience" + str(experience_counter)
                keyword_text_experience = ""
                st.subheader(experience['company_name'])
                st.text(f"Job Title: {experience['job_title']}")
                st.text(f"Date: {experience['date']}")
                st.text("Description:")
                formatted_description = format_description(experience['description'])
                cols = st.columns([4, 1, 1])
                if key not in st.session_state:    
                    experience_text = cols[0].text_area(label="", value=formatted_description, key=f"work_{experience['company_name']}_{experience['date']}")
                else:
                    experience_text = cols[0].text_area(label="", value=st.session_state[key]['description'], key=f"work_{experience['company_name']}_{experience['date']}")
                if cols[1].button("Generate AI", key=f"edit_work_{experience['company_name']}_{experience['date']}"):
                    st.session_state.code_executed = True
                    keyword_text_experience = cols[0].text_input(label="", placeholder="Enter your keywords", key=key+"_keywords")
                    work_experience_result = work_experience_ai(experience_text, keyword_text_experience, st.session_state.job_info['description'])
                    st.markdown("""
                        <style>
                        .stButton button {
                            height: 100%;
                        }
                        .stColumn div {
                            height: 100%;
                            display: flex;
                            align-items: center;
                        }
                        .stColumn {
                            display: flex;
                            flex-direction: column;
                        }
                        </style>
                        """, unsafe_allow_html=True)

                    # Display the summaries and buttons
                    for description, work_experience in work_experience_result["work_experience_ai_result"].items():
                        cols2 = st.columns([2, 5, 1])
                        cols2[0].write(description.capitalize() + ":")
                        cols2[1].write(work_experience)
                        with cols2[2]:
                            st.button('➕', on_click=lambda d={'data': work_experience_result, 'key': key, 'description': format_description(work_experience)}: update_work_experience(d), key=key+description)
                elif key in st.session_state:
                    print(st.session_state[key])
                    st.session_state.code_executed = True
                    keyword_text_experience = cols[0].text_input(label="", placeholder="Enter your keywords", key=key+"_keywords")
                    work_experience_result = st.session_state[key]['data']
                    st.markdown("""
                        <style>
                        .stButton button {
                            height: 100%;
                        }
                        .stColumn div {
                            height: 100%;
                            display: flex;
                            align-items: center;
                        }
                        .stColumn {
                            display: flex;
                            flex-direction: column;
                        }
                        </style>
                        """, unsafe_allow_html=True)

                    # Display the summaries and buttons
                    for description, work_experience in work_experience_result["work_experience_ai_result"].items():
                        cols2 = st.columns([2, 5, 1])
                        cols2[0].write(description.capitalize() + ":")
                        cols2[1].write(work_experience)
                        with cols2[2]:
                            st.button('➕', on_click=lambda d={'data': work_experience_result, 'key': key, 'description': format_description(work_experience)}: update_work_experience(d), key=key+description)
                    
            # Education
            st.header("Education")
            education_counter = 0
            for edu in file_contents['cv']['education']:
                education_counter += 1
                key = "education" + str(education_counter)
                keyword_text_education = ""
                st.subheader(edu['school_name'])
                st.text(f"Date: {edu['date']}")
                st.text(f"Degree: {edu['degree_major']}")
                st.text(f"Score: {edu['score']}")
                st.text("Description:")
                formatted_description = format_description(experience['description'])
                cols = st.columns([4, 1, 1])
                if key not in st.session_state:    
                    education_text = cols[0].text_area(label="", value=formatted_description, key=f"edu_{edu['school_name']}_{edu['date']}")
                else:
                    education_text = cols[0].text_area(label="", value=st.session_state[key]['description'], key=f"edu_{edu['school_name']}_{edu['date']}")
                if cols[1].button("Generate AI", key=f"edit_edu_{edu['school_name']}_{edu['date']}"):
                    st.session_state.code_executed = True
                    keyword_text_education = cols[0].text_input(label="", placeholder="Enter your keywords", key=key+"_keywords")
                    education_result = education_ai(education_text, keyword_text_education, st.session_state.job_info['description'])
                    st.markdown("""
                        <style>
                        .stButton button {
                            height: 100%;
                        }
                        .stColumn div {
                            height: 100%;
                            display: flex;
                            align-items: center;
                        }
                        .stColumn {
                            display: flex;
                            flex-direction: column;
                        }
                        </style>
                        """, unsafe_allow_html=True)

                    # Display the summaries and buttons
                    for description, education in education_result["education_ai_result"].items():
                        cols2 = st.columns([2, 5, 1])
                        cols2[0].write(description.capitalize() + ":")
                        cols2[1].write(education)
                        with cols2[2]:
                            st.button('➕', on_click=lambda d={'data': education_result, 'key': key, 'description': format_description(education)}: update_education(d), key=key+description)
                elif key in st.session_state:
                    print(st.session_state[key])
                    st.session_state.code_executed = True
                    keyword_text_education = cols[0].text_input(label="", placeholder="Enter your keywords", key=key+"_keywords")
                    education_result = st.session_state[key]['data']
                    st.markdown("""
                        <style>
                        .stButton button {
                            height: 100%;
                        }
                        .stColumn div {
                            height: 100%;
                            display: flex;
                            align-items: center;
                        }
                        .stColumn {
                            display: flex;
                            flex-direction: column;
                        }
                        </style>
                        """, unsafe_allow_html=True)

                    # Display the summaries and buttons
                    for description, education in education_result["education_ai_result"].items():
                        cols2 = st.columns([2, 5, 1])
                        cols2[0].write(description.capitalize() + ":")
                        cols2[1].write(education)
                        with cols2[2]:
                            st.button('➕', on_click=lambda d={'data': education_result, 'key': key, 'description': format_description(education)}: update_education(d), key=key+description)
            st.header("Projects")
            project_counter = 0
            for project in file_contents['cv']['project']:
                project_counter += 1
                key = "project" + str(project_counter)
                keyword_text_project = ""
                st.subheader(project['project_name'])
                st.text(f"Date: {edu['date']}")
                st.text("Description:")
                formatted_description = format_description(project['description'])
                cols = st.columns([4, 1, 1])
                if key not in st.session_state:    
                    project_text = cols[0].text_area(label="", value=formatted_description, key=f"project_{project['project_name']}_{project['date']}")
                else:
                    project_text = cols[0].text_area(label="", value=st.session_state[key]['description'], key=f"project_{project['project_name']}_{project['date']}")
                if cols[1].button("Generate AI", key=f"project_{project['project_name']}_{key}"):
                    st.session_state.code_executed = True
                    keyword_text_project = cols[0].text_input(label="", placeholder="Enter your keywords", key=key+"_keywords")
                    project_result = project_ai(project_text, keyword_text_project, st.session_state.job_info['description'])
                    st.markdown("""
                        <style>
                        .stButton button {
                            height: 100%;
                        }
                        .stColumn div {
                            height: 100%;
                            display: flex;
                            align-items: center;
                        }
                        .stColumn {
                            display: flex;
                            flex-direction: column;
                        }
                        </style>
                        """, unsafe_allow_html=True)

                    # Display the summaries and buttons
                    for description, project in project_result["project_result_ai"].items():
                        cols2 = st.columns([2, 5, 1])
                        cols2[0].write(description.capitalize() + ":")
                        cols2[1].write(project)
                        with cols2[2]:
                            st.button('➕', on_click=lambda d={'data': project_result, 'key': key, 'description': format_description(project)}: update_project(d), key=key+description)
                elif key in st.session_state:
                    print(st.session_state[key])
                    st.session_state.code_executed = True
                    keyword_text_project = cols[0].text_input(label="", placeholder="Enter your keywords", key=key+"_keywords")
                    project_result = st.session_state[key]['data']
                    st.markdown("""
                        <style>
                        .stButton button {
                            height: 100%;
                        }
                        .stColumn div {
                            height: 100%;
                            display: flex;
                            align-items: center;
                        }
                        .stColumn {
                            display: flex;
                            flex-direction: column;
                        }
                        </style>
                        """, unsafe_allow_html=True)

                    # Display the summaries and buttons
                    for description, project in project_result["project_result_ai"].items():
                        cols2 = st.columns([2, 5, 1])
                        cols2[0].write(description.capitalize() + ":")
                        cols2[1].write(project)
                        with cols2[2]:
                            st.button('➕', on_click=lambda d={'data': project_result, 'key': key, 'description': format_description(project)}: update_project(d), key=key+description)
            # Skills
            st.header("Skills")
            formatted_description = format_description(file_contents['cv']['skills'])
            keyword_text_skill = ""
            cols = st.columns([4, 2])
            cols[0].text_area(label="", value=formatted_description, key=f"skills")
            if cols[1].button("Generate AI", key=f"edit_skills"):
                st.session_state.code_executed = True
                keyword_text_skill = cols[0].text_input(label="", placeholder="Enter your keywords")
                skills_result = skills_ai(experience_text, file_contents['cv'], keyword_text_skill, st.session_state.job_info['description'])
                # Create HTML table
                html_table = f"""
                    <div style="overflow-x: auto;">
                        <table style="width: 100%; border-collapse: collapse;">
                            <thead>
                                <tr>
                                    <th style="border: 1px solid black; padding: 8px; text-align: left;">Description</th>
                                    <th style="border: 1px solid black; padding: 8px; text-align: left;">Summary</th>
                                </tr>
                            </thead>
                            <tbody>
                                <tr>
                                    <td style="border: 1px solid black; padding: 8px;">Recommended</td>
                                    <td style="border: 1px solid black; padding: 8px;">{skills_result["skills_ai_result"]["recommended"]}</td>
                                </tr>
                                <tr>
                                    <td style="border: 1px solid black; padding: 8px;">Simplified</td>
                                    <td style="border: 1px solid black; padding: 8px;">{skills_result["skills_ai_result"]["simplified"]}</td>
                                </tr>
                                <tr>
                                    <td style="border: 1px solid black; padding: 8px;">Extended</td>
                                    <td style="border: 1px solid black; padding: 8px;">{skills_result["skills_ai_result"]["extended"]}</td>
                                </tr>
                            </tbody>
                        </table>
                    </div>
                    """

                # Inject the HTML table into Streamlit
                st.markdown(html_table, unsafe_allow_html=True)
                st.write(file_contents)
    else:
        st.write("Please upload your CV here.")

# Streamlit UI
def main():
    # if 'code_executed' not in st.session_state:
        show_main_content()

if __name__ == "__main__":
    main()