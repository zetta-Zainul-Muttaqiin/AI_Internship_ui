import streamlit as st
import os
import pandas as pd
from cv_upload import cv_extractor
from cv_generator import summary_ai, work_experience_ai, education_ai, project_ai, skills_ai
from job_recommend import get_selected_description

os.environ['Path'] = r'poppler-24.02.0\Library\bin'
api_config = st.secrets["api"]
openai_api_key = api_config["openai_api_key"]
os.environ['OPENAI_API_KEY'] = openai_api_key

def displayed_job_adapt():
    st.session_state["job_adapt"] = {
        'job_role': st.session_state["job_details"]['job_role'],
        'location': st.session_state["job_details"]['location'],
        'description': st.session_state["job_details"]['description'],
        'company': st.session_state["job_details"]['company'],
        'company_description': st.session_state["job_details"]['company_description'],
    }

    # *************** SIDEBAR FOR DISPLAYING JOB DETAILS ***************
    st.sidebar.header("Job Details")

    st.sidebar.text_input(label="Job Role", value=st.session_state["job_adapt"]['job_role'], disabled=True)

    st.sidebar.text_input(label="Location", value=st.session_state["job_adapt"]['location'], disabled=True)

    st.sidebar.text_area(label="Description", value=st.session_state["job_adapt"]['description'], disabled=True)

    st.sidebar.text_input(label="Company", value=st.session_state["job_adapt"]['company'], disabled=True)

    st.sidebar.text_area(label="Company Description", value=st.session_state["job_adapt"]['company_description'], disabled=True)

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

def update_skill(data):
    st.session_state['skill_data'] = data

def format_description(description_list):
                # Add '-' before each description item
                formatted = '\n'.join(f"- {desc}" for desc in description_list)
                return formatted

def save_details():
    st.session_state["cv_details"] = {
        'summary': st.session_state["summary_curr"] if 'summary_curr' in st.session_state else {},
        'work_experience': st.session_state["work_experience_curr"] if 'work_experience_curr' in st.session_state else {},
        'education': st.session_state["education_curr"] if 'education_curr' in st.session_state else {},
        'project': st.session_state["project_curr"] if 'project_curr' in st.session_state else {},
        'skills': st.session_state["skills_curr"] if 'skills_curr' in st.session_state else {},
    }
    st.success("CV details saved!")

def show_main_content():
    
    if 'job_info' not in st.session_state:
        st.session_state["job_info"] = {
                        'job_url': "",
                        'job_role': ""
                        }
    else:
        if st.session_state["job_info"]["job_url"] != "":
            job_url = st.session_state["job_info"]["job_url"]
            st.session_state["job_details"] = get_selected_description(job_url)
            if not st.session_state["job_details"]:
                st.error("Internship Offer already close the regristation")
            st.session_state["job_adapt"] = {
                'job_role': st.session_state["job_details"]['job_role'],
                'location': st.session_state["job_details"]['location'],
                'description': st.session_state["job_details"]['description'],
                'company': st.session_state["job_details"]['company'],
                'company_description': st.session_state["job_details"]['company_description'],
            }
    if "file_contents" not in st.session_state:
        st.session_state["file_contents"] = ""
        st.title("LeBon Stage")
    
    if 'job_details' in st.session_state:
        displayed_job_adapt()
    else:
        st.sidebar.write("No job details available.")

    # File uploader
    uploaded_file = st.file_uploader("Choose a PDF file", type="pdf")

    if uploaded_file:
        if "uploaded_file" not in st.session_state:
            st.session_state.uploaded_file = uploaded_file
            file_path = save_uploaded_file(st.session_state.uploaded_file)
            with st.spinner("Processing your CV..."):
                # Process the uploaded PDF file
                st.session_state["file_contents"] = cv_extractor(file_path)
                st.success("CV processed successfully!")
                
                st.session_state.summary_curr = st.session_state["file_contents"]['cv']['summary']
                st.session_state.work_experience_curr = st.session_state["file_contents"]['cv']['work_experience']
                st.session_state.education_curr = st.session_state["file_contents"]['cv']['education']
                st.session_state.project_curr = st.session_state["file_contents"]['cv']['project']
                st.session_state.skills_curr = st.session_state["file_contents"]['cv']['skills']
        
        elif "uploaded_file" in st.session_state:
            
            if st.session_state.uploaded_file != uploaded_file:
                # Save the uploaded file to disk
                file_path = save_uploaded_file(uploaded_file)
                with st.spinner("Processing your CV..."):
                    # Process the uploaded PDF file
                    st.session_state["file_contents"] = cv_extractor(file_path)
                    st.success("New CV processed successfully!")
                    
                    st.session_state.summary_curr = st.session_state["file_contents"]['cv']['summary']
                    st.session_state.work_experience_curr = st.session_state["file_contents"]['cv']['work_experience']
                    st.session_state.education_curr = st.session_state["file_contents"]['cv']['education']
                    st.session_state.project_curr = st.session_state["file_contents"]['cv']['project']
                    st.session_state.skills_curr = st.session_state["file_contents"]['cv']['skills']
        
        st.session_state.uploaded_file = uploaded_file
            
        if st.session_state["file_contents"]:
            # Displaying the CV data in a table format using Streamlit
            
            cols_nav = st.columns([6,2,1,1])
            if cols_nav[2].button('Save'):
                save_details()
            
                if st.session_state.cv_details:
                    cols_nav[3].page_link(r'pages/Cover_Letter.py', label="Next")

            st.subheader("Let AI Boost Your CV for Your Internship")

            # ***************** SUMMARY *****************
            st.header("Summary")
            summary = st.session_state["file_contents"]['cv']['summary']
            
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
                st.session_state["code_executed"] = True
                keyword_text_summary = cols[0].text_input(label="", placeholder="Enter your keywords", key="summary_keywords")
                summary_ai_result = summary_ai(summary_text, keyword_text_summary, st.session_state["job_info"])
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
                        if st.button('➕', on_click=lambda d={'summary_ai_result': summary_ai_result, 'summary': summary}: update_summary(d), key=description):
                            st.toast("updated Summary description")
                            st.session_state.summary_curr['summary'] = st.session_state["summary"]  
            elif 'summary_data' in st.session_state:
                st.session_state["code_executed"] = True
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
                        if st.button('➕', on_click=lambda d={'summary_ai_result': summary_ai_result, 'summary': summary}: update_summary(d), key=description):
                            st.toast("updated Summary description")
                            st.session_state.summary_curr['summary'] = st.session_state["summary"]
         
            
            
            # ***************** WORK EXPERIENCE *****************
            st.header("Work Experience")
            experience_counter = 0
            for experience in st.session_state['file_contents']['cv']['work_experience']:
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
                    st.session_state["code_executed"] = True
                    keyword_text_experience = cols[0].text_input(label="", placeholder="Enter your keywords", key=key+"_keywords")
                    work_experience_result = work_experience_ai(experience_text, keyword_text_experience, st.session_state["job_info"])
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
                            if st.button('➕', on_click=lambda d={'data': work_experience_result, 'key': key, 'description': format_description(work_experience)}: update_work_experience(d), key=key+description):
                                st.toast("updated Work Experience description")
                                st.session_state.work_experience_curr[experience_counter]['description'] = work_experience
                
                elif key in st.session_state:
                    print(st.session_state[key])
                    st.session_state["code_executed"] = True
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
                            if st.button('➕', on_click=lambda d={'data': work_experience_result, 'key': key, 'description': format_description(work_experience)}: update_work_experience(d), key=key+description):
                                st.toast("updated Work Experience description")
                                st.session_state.work_experience_curr[experience_counter]['description'] = work_experience

                experience_counter += 1
            
            # ******************** EDUCATION ********************
            st.header("Education")
            education_counter = 0
            for edu in st.session_state["file_contents"]['cv']['education']:
                
                key = "education" + str(education_counter)
                keyword_text_education = ""
                st.subheader(edu['school_name'])
                st.text(f"Date: {edu['date']}")
                st.text(f"Degree: {edu['degree_major']}")
                st.text(f"Score: {edu['score']}")
                st.text("Description:")
                formatted_description = edu['description']
                cols = st.columns([4, 1, 1])
                if key not in st.session_state:    
                    education_text = cols[0].text_area(label="", value=formatted_description, key=f"edu_{edu['school_name']}_{edu['date']}")
                else:
                    education_text = cols[0].text_area(label="", value=st.session_state[key]['description'], key=f"edu_{edu['school_name']}_{edu['date']}")
                if cols[1].button("Generate AI", key=f"edit_edu_{edu['school_name']}_{edu['date']}"):
                    st.session_state["code_executed"] = True
                    keyword_text_education = cols[0].text_input(label="", placeholder="Enter your keywords", key=key+"_keywords")
                    education_result = education_ai(education_text, keyword_text_education, st.session_state["job_info"])
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

                    # Display the description and buttons
                    for description, education in education_result["education_ai_result"].items():
                        cols2 = st.columns([2, 5, 1])
                        cols2[0].write(description.capitalize() + ":")
                        cols2[1].write(education)
                        with cols2[2]:
                            if st.button('➕', on_click=lambda d={'data': education_result, 'key': key, 'description': format_description(education)}: update_education(d), key=key+description):
                                st.toast("updated Education description")
                                st.session_state.education_curr[education_counter]['description'] = education
                
                elif key in st.session_state:
                    print(st.session_state[key])
                    st.session_state["code_executed"] = True
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
                            if st.button('➕', on_click=lambda d={'data': education_result, 'key': key, 'description': format_description(education)}: update_education(d), key=key+description):
                                st.toast("updated Education description")
                                st.session_state.education_curr[education_counter]['description'] = education
                
                education_counter += 1
            
            # ***************** PROJECT ***************
            st.header("Projects")
            project_counter = 0
            for project in st.session_state["file_contents"]['cv']['project']:
                
                key = "project" + str(project_counter)
                keyword_text_project = ""
                st.subheader(project['project_name'])
                st.text(f"Date: {project['date']}")
                st.text("Description:")
                formatted_description = format_description(project['description'])
                
                cols = st.columns([4, 1, 1])
                if key not in st.session_state:    
                    project_text = cols[0].text_area(label="", value=formatted_description, key=f"project_{project['project_name']}_{project['date']}")
                else:
                    project_text = cols[0].text_area(label="", value=st.session_state[key]['description'], key=f"project_{project['project_name']}_{project['date']}")
                if cols[1].button("Generate AI", key=f"project_{project['project_name']}_{key}"):
                    st.session_state["code_executed"] = True
                    keyword_text_project = cols[0].text_input(label="", placeholder="Enter your keywords", key=key+"_keywords")
                    project_result = project_ai(project_text, keyword_text_project, st.session_state["job_info"])
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
                            if st.button('➕', on_click=lambda d={'data': project_result, 'key': key, 'description': format_description(project)}: update_project(d), key=key+description):
                                st.toast("updated Project description")
                                st.session_state.project_curr[project_counter]['description'] = format_description(project)
                
                elif key in st.session_state:
                    print(st.session_state[key])
                    st.session_state["code_executed"] = True
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
                            if st.button('➕', on_click=lambda d={'data': project_result, 'key': key, 'description': format_description(project)}: update_project(d), key=key+description):
                                st.toast("updated Project description")
                                st.session_state.project_curr[project_counter]['description'] = format_description(project)
                
                project_counter += 1
            
            
            # *************** SKILLS ***************
            st.header("Skills")
            formatted_description = format_description(st.session_state["file_contents"]['cv']['skills'])
            # Use text_area for the summary
            keyword_text_skill = ""
            cols = st.columns([4, 1, 1])
            if 'skill_data' not in st.session_state:
                skill_text = cols[0].text_area(label="", value=formatted_description, key=f"skills")   
            else:
                skill_text = cols[0].text_area(label="", value=st.session_state['skill_data']['skill'], key="skill")
            if cols[1].button("Generate AI", key="edit_skill"):
                st.session_state["code_executed"] = True
                keyword_text_summary = cols[0].text_input(label="", placeholder="Enter your keywords", key="skill_keywords")
                skills_result = skills_ai(skill_text, st.session_state["file_contents"]['cv'], keyword_text_skill, st.session_state["job_info"])
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
                skill_loop = 0
                for description, skill in skills_result["skills_ai_result"].items():
                    cols2 = st.columns([2, 5, 1])
                    cols2[0].write(description.capitalize() + ":")
                    cols2[1].write(skill)
                    skill_loop += 1
                    with cols2[2]:
                        if st.button('➕', on_click=lambda d={'skills_ai_result': skills_result, 'skill': format_description(skill)}: update_skill(d), key=description+str(skill_loop)):
                            st.toast("Updated Skills")
                            st.session_state.skills_curr = skill
            
            elif 'skill_data' in st.session_state:
                st.session_state["code_executed"] = True
                keyword_text_summary = cols[0].text_input(label="", placeholder="Enter your keywords", key="skill_keywords")
                skills_result = st.session_state['skill_data']['skills_ai_result']
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
                skill_loop = 0
                for description, skill in skills_result["skills_ai_result"].items():
                    cols2 = st.columns([2, 5, 1])
                    cols2[0].write(description.capitalize() + ":")
                    cols2[1].write(skill)
                    skill_loop += 1
                    with cols2[2]:
                        if st.button('➕', on_click=lambda d={'skills_ai_result': skills_result, 'skill': format_description(skill)}: update_skill(d), key=description+str(skill_loop)):
                            st.toast("Updated Skills")
                            st.session_state.skills_curr = skill
            
    
    else:
        st.write("Please upload your CV here.")
    

# Streamlit UI
def main():
    # if 'code_executed' not in st.session_state:
        
        # st.write(st.session_state)
        show_main_content()

if __name__ == "__main__":
    main()