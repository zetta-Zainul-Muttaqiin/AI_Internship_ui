import streamlit as st
from cover_letter import cover_letter_creation
from pages.CV_Upload import displayed_job_adapt
from setup import predefined_cvs, CV

def run_streamlit_app():

    if 'cv_details' not in st.session_state:
        st.session_state.cv_details = CV

    st.title("Cover Letter Generator")

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

    # ********* Keywords Input *********
    keywords = st.sidebar.text_area("Enter keywords for the cover letter order", height=25)

    # ********* Generate Cover Letter Button *********
    if st.sidebar.button("Generate Cover Letter"):
        
        if not cv_content:
            st.sidebar.error("Please select a CV.")
        elif "job_adapt" not in st.session_state:
            st.sidebar.error("Please provide job information.")
        else:
            if "job_adapt" in st.session_state:
                if st.session_state.job_adapt == "":
                    st.sidebar.error("Job Information Not Found.")
            try:
                result = cover_letter_creation(cv_content, st.session_state["job_adapt"]["description"], keywords)
                st.subheader("Generated Cover Letter")
                st.write(result["cover_letter_ai"])
            except KeyError as e:
                st.error(f"Error: {str(e)}")
            except Exception as e:
                st.error(f"An unexpected error occurred: {str(e)}")
    
    st.sidebar.page_link(r'pages/CV_Upload.py', label="Back to CV Upload")

    # ********* Layout for Displaying CV and Cover Letter *********
    col1, col2 = st.columns([1, 1])

    with col1:
        st.subheader("CV Content")
        if cv_content:
            summary, works, educations, project, skills = st.tabs(
                [
                    "Summary", 
                    "Work Expereinces", 
                    "Edcuations", "Projects", 
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

    with col2:
        st.subheader("Cover Letter")
        if 'result' in locals():
            st.toast("Cover Letter Generated")
            st.text_area("Cover Letter", result["cover_letter_ai"], height=400)
    
    if 'result' in locals():
        st.sidebar.page_link(r'pages/Flashcard.py', label="Next Flashcard")
# *************** RUN STREAMLIT APP ***************
if __name__ == "__main__":
    # st.write(st.session_state)
    run_streamlit_app()
    # st.write(st.session_state)
