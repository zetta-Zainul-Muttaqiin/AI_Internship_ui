import streamlit as st
from cover_letter import cover_letter_creation
from setup import predefined_cvs

def run_streamlit_app():
    st.set_page_config(layout="wide")

    st.title("Cover Letter Generator")

    # ********* Sidebar for CV Upload *********
    st.sidebar.title("Select CV")
    cv_selection = st.sidebar.selectbox("Select your CV", options=["", "ADE CV", "Joseph CV"])

    cv_content = predefined_cvs.get(cv_selection, "")

    # ********* Job Information Input *********
    st.sidebar.subheader("Goals")
    job_detail = st.sidebar.text_area("Job Information", height=150)
    job_role = st.sidebar.text_input("Job Role")
    company_name = st.sidebar.text_input("Company Name")


    job_info = {
        "job_detail": job_detail,
        "job_role": job_role,
        "compnay_name": company_name
    }

    # ********* Keywords Input *********
    keywords = st.sidebar.text_area("Enter keywords for the cover letter order", height=50)

    # ********* Generate Cover Letter Button *********
    if st.sidebar.button("Generate Cover Letter"):
        
        if not cv_content:
            st.sidebar.error("Please select a CV.")
        elif not job_info:
            st.sidebar.error("Please provide job information.")
        else:
            try:
                result = cover_letter_creation(cv_content, job_info, keywords)
                st.subheader("Generated Cover Letter")
                st.write(result["cover_letter_ai"])
            except KeyError as e:
                st.error(f"Error: {str(e)}")
            except Exception as e:
                st.error(f"An unexpected error occurred: {str(e)}")

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
                summary.markdown(f'''Summary:\n
                {summary_data['summary']}
                ''', 
                unsafe_allow_html=True)

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
            st.text_area("Cover Letter", result["cover_letter_ai"], height=400)

    # ********* Save and Next Step Buttons *********
    st.sidebar.button("Save")
    st.sidebar.button("Next Step")

# *************** RUN STREAMLIT APP ***************
if __name__ == "__main__":
    run_streamlit_app()