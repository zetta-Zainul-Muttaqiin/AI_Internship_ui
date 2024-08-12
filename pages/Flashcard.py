import streamlit as st
import os
from flashcard import generate_flashcards
from pages.CV_Upload import displayed_job_adapt
from setup import predefined_cvs, CV

def run_streamlit_app():
    if 'cv_details' not in st.session_state:
        st.session_state.cv_details = CV
    st.title("Interview Flashcards Generator")

    # ********* Sidebar for CV Upload *********
    st.sidebar.title("Select CV")
    if 'cv_details' in st.session_state and 'uploaded_file' in st.session_state:
        cv_selection = st.sidebar.selectbox("Select your CV", options=[st.session_state.uploaded_file.name], disabled=True)
        cv_content = st.session_state.cv_details
    else:    
        cv_selection = st.sidebar.selectbox("Select your CV", options=["", "ADE CV", "Joseph CV"])

        cv_content = predefined_cvs.get(cv_selection, "")
    # ********* Job Information Displayed *********
    if 'job_details' in st.session_state:
        displayed_job_adapt()
    else:
        st.sidebar.write("No job details available.")
   
    # ********* Generate Flashcards Button *********
    if st.sidebar.button("Generate Flashcards"):
        
        if not cv_content:
            st.sidebar.error("Please select a CV.")
        elif "job_adapt" not in st.session_state:
            st.sidebar.error("Please provide job information.")
        else:
            if "job_adapt" in st.session_state:
                if st.session_state.job_adapt == "":
                    st.sidebar.error("Job Information Not Found.")
            try:
                job_info = {
                    "job_position": st.session_state.job_adapt['job_role'],
                    "job_description": st.session_state.job_adapt['description'],
                    }
                company_info = {
                    "company_name": st.session_state.job_adapt['company'],
                    "company_detail": st.session_state.job_adapt['company_description'],
                    }
                with st.spinner("Generating flashcards..."):
                     result = generate_flashcards(cv_content, company_info, job_info)
                if result:
                    st.success("successfully generate Flashcard")
                # Separate flashcards by category
                technical_flashcards = [fc for fc in result['result'] if fc['category'] == 'technical']
                soft_skill_flashcards = [fc for fc in result['result'] if fc['category'] == 'soft skill']

                if technical_flashcards:
                    st.subheader("Technical Questions")
                    for flashcard in technical_flashcards:
                        st.markdown(f"""
                        <div style="border: 1px solid #ddd; border-radius: 10px; padding: 10px; margin-bottom: 10px; box-shadow: 2px 2px 5px rgba(0, 0, 0, 0.1);">
                            <h4 style="color: #444;">{flashcard['question']}</h4>
                            <p style="color: #666;">{flashcard['suggest_answer']}</p>
                        </div>
                        """, unsafe_allow_html=True)

                if soft_skill_flashcards:
                    st.subheader("Soft Skill Questions")
                    for flashcard in soft_skill_flashcards:
                        st.markdown(f"""
                        <div style="border: 1px solid #ddd; border-radius: 10px; padding: 10px; margin-bottom: 10px; box-shadow: 2px 2px 5px rgba(0, 0, 0, 0.1);">
                            <h4 style="color: #444;">{flashcard['question']}</h4>
                            <p style="color: #666;">{flashcard['suggest_answer']}</p>
                        </div>
                        """, unsafe_allow_html=True)
            except KeyError as e:
                st.error(f"Error: {str(e)}")
            except Exception as e:
                st.error(f"An unexpected error occurred: {str(e)}")

    # ********* Layout for Displaying CV *********
    st.subheader("CV Content")
    if cv_content:
        summary, works, educations, project, skills = st.tabs(
            [
                "Summary", 
                "Work Experiences", 
                "Educations", "Projects", 
                "Skills"
            ]
        )
        summary_data = cv_content['summary']
        summary.text(f"Name: {summary_data['name']}")
        summary.text(f"Location: {summary_data['location']}")
        summary.text(f"Phone: {summary_data['phone']}")
        summary.text(f"Email: {summary_data['email']}")
        with summary.expander('', expanded=True):
                summary.text_area(label='Summary:', value=summary_data['summary'])

        works_data = cv_content['work_experience']
        for experience in works_data:
            works.subheader(experience['company_name'])
            works.text(f"Job Title: {experience['job_title']}")
            works.text(f"Date: {experience['date']}")
            works.text("Description: ")
            for desc in experience['description']:
                works.markdown(f"- {desc}")

        edu_data = cv_content['education']
        for edu in edu_data:
            educations.subheader(edu['school_name'])
            educations.text(f"Degree/Major: {edu['degree_major']}")
            educations.text(f"Date: {edu['date']}")
            educations.text(f"Score: {edu['score']}")
            educations.text("Description: ")
            for desc in edu['description']:
                educations.markdown(f"- {desc}")

        proj_data = cv_content['project']
        for proj in proj_data:
            project.subheader(proj['project_name'])
            project.text(f"Date: {proj['date']}")
            project.text("Description: ")
            # for desc in proj['description']:
            project.markdown(f"- {proj['description']}")

        skill_list = cv_content['skills']
        for skill in skill_list:
            skills.markdown(f"- {skill}")
    
    st.sidebar.page_link(r'pages/Cover_Letter.py', label="Back to Cover Letter")

# *************** RUN STREAMLIT APP ***************
if __name__ == "__main__":
    # st.write(st.session_state)
    run_streamlit_app()