import streamlit as st
import os
import pandas as pd
from cv_upload import cv_extractor
from cv_generator import summary_ai, work_experience_ai, education_ai, project_ai, skills_ai

# os.environ['Path'] = 'poppler-24.02.0\Library\bin'
# api_config = st.secrets["api"]
# openai_api_key = api_config["openai_api_key"]
# os.environ['OPENAI_API_KEY'] = openai_api_key
st.write(st.session_state)
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
            
            def format_description(description_list):
                # Add '-' before each description item
                formatted = '\n'.join(f"- {desc}" for desc in description_list)
                return formatted

            st.text(f"Generate description following job: {st.session_state.job_info['job_role']}")

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
            summary_text = cols[0].text_area(label="", value=summary['summary'], key="summary")
            if cols[1].button("Generate AI", key="edit_summary"):
                st.session_state.code_executed = True
                keyword_text_summary = cols[0].text_input(label="", placeholder="Enter your keywords")
                summary_ai_result = summary_ai(summary_text, keyword_text_summary, st.session_state.job_info['description'])
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
                                <td style="border: 1px solid black; padding: 8px;">{summary_ai_result["summary_ai_result"]["recommended"]}</td>
                            </tr>
                            <tr>
                                <td style="border: 1px solid black; padding: 8px;">Simplified</td>
                                <td style="border: 1px solid black; padding: 8px;">{summary_ai_result["summary_ai_result"]["simplified"]}</td>
                            </tr>
                            <tr>
                                <td style="border: 1px solid black; padding: 8px;">Extended</td>
                                <td style="border: 1px solid black; padding: 8px;">{summary_ai_result["summary_ai_result"]["extended"]}</td>
                            </tr>
                        </tbody>
                    </table>
                </div>
                """

                # Inject the HTML table into Streamlit
                st.markdown(html_table, unsafe_allow_html=True)

            # Work Experience
            st.header("Work Experience")
            for experience in file_contents['cv']['work_experience']:
                keyword_text_experience = ""
                st.subheader(experience['company_name'])
                st.text(f"Job Title: {experience['job_title']}")
                st.text(f"Date: {experience['date']}")
                st.text("Description:")
                formatted_description = format_description(experience['description'])
                cols = st.columns([4, 1])
                experience_text = cols[0].text_area(label="", value=formatted_description, key=f"work_{experience['company_name']}_{experience['date']}")
                if cols[1].button("Generate AI", key=f"edit_work_{experience['company_name']}_{experience['date']}"):
                    st.session_state.code_executed = True
                    keyword_text_experience = cols[0].text_input(label="", placeholder="Enter your keywords")
                    work_experience_result = work_experience_ai(experience_text, keyword_text_experience, st.session_state.job_info['description'])
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
                                    <td style="border: 1px solid black; padding: 8px;">{work_experience_result["work_experience_ai_result"]["recommended"]}</td>
                                </tr>
                                <tr>
                                    <td style="border: 1px solid black; padding: 8px;">Simplified</td>
                                    <td style="border: 1px solid black; padding: 8px;">{work_experience_result["work_experience_ai_result"]["simplified"]}</td>
                                </tr>
                                <tr>
                                    <td style="border: 1px solid black; padding: 8px;">Extended</td>
                                    <td style="border: 1px solid black; padding: 8px;">{work_experience_result["work_experience_ai_result"]["extended"]}</td>
                                </tr>
                            </tbody>
                        </table>
                    </div>
                    """

                    # Inject the HTML table into Streamlit
                    st.markdown(html_table, unsafe_allow_html=True)
                    
            # Education
            st.header("Education")
            for edu in file_contents['cv']['education']:
                keyword_text_education = ""
                st.subheader(edu['school_name'])
                st.text(f"Date: {edu['date']}")
                st.text(f"Degree/Major: {edu['degree_major']}")
                st.text(f"Score: {edu['score']}")
                st.text("Description:")
                formatted_description = format_description(edu['description'])
                cols = st.columns([4, 1])
                cols[0].text_area(label="", value=formatted_description, key=f"edu_{edu['school_name']}_{edu['date']}")
                if cols[1].button("Generate AI", key=f"edit_edu_{edu['school_name']}_{edu['date']}"):
                    st.session_state.code_executed = True
                    keyword_text_education = cols[0].text_input(label="", placeholder="Enter your keywords")
                    education_result = education_ai(experience_text, keyword_text_education, st.session_state.job_info['description'])
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
                                    <td style="border: 1px solid black; padding: 8px;">{education_result["education_ai_result"]["recommended"]}</td>
                                </tr>
                                <tr>
                                    <td style="border: 1px solid black; padding: 8px;">Simplified</td>
                                    <td style="border: 1px solid black; padding: 8px;">{education_result["education_ai_result"]["simplified"]}</td>
                                </tr>
                                <tr>
                                    <td style="border: 1px solid black; padding: 8px;">Extended</td>
                                    <td style="border: 1px solid black; padding: 8px;">{education_result["education_ai_result"]["extended"]}</td>
                                </tr>
                            </tbody>
                        </table>
                    </div>
                    """

                    # Inject the HTML table into Streamlit
                    st.markdown(html_table, unsafe_allow_html=True)
            # Projects
            st.header("Projects")
            for project in file_contents['cv']['project']:
                keyword_text_project = ""
                st.subheader(project['project_name'])
                st.text(f"Date: {project['date']}")
                st.text("Description:")
                formatted_description = format_description(project['description'])
                cols = st.columns([4, 1])
                cols[0].text_area(label="", value=formatted_description, key=f"project_{project['project_name']}_{project['date']}")
                if cols[1].button("Generate AI", key=f"edit_project_{project['project_name']}_{project['date']}"):
                    st.session_state.code_executed = True
                    keyword_text_project = cols[0].text_input(label="", placeholder="Enter your keywords")
                    project_result = project_ai(experience_text, keyword_text_project, st.session_state.job_info['description'])
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
                                    <td style="border: 1px solid black; padding: 8px;">{project_result["project_result_ai"]["recommended"]}</td>
                                </tr>
                                <tr>
                                    <td style="border: 1px solid black; padding: 8px;">Simplified</td>
                                    <td style="border: 1px solid black; padding: 8px;">{project_result["project_result_ai"]["simplified"]}</td>
                                </tr>
                                <tr>
                                    <td style="border: 1px solid black; padding: 8px;">Extended</td>
                                    <td style="border: 1px solid black; padding: 8px;">{project_result["project_result_ai"]["extended"]}</td>
                                </tr>
                            </tbody>
                        </table>
                    </div>
                    """

                    # Inject the HTML table into Streamlit
                    st.markdown(html_table, unsafe_allow_html=True)
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
    else:
        st.write("Please upload your CV here.")

# Streamlit UI
def main():
    # if 'code_executed' not in st.session_state:
        show_main_content()

if __name__ == "__main__":
    main()