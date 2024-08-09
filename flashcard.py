from langchain import LLMChain
from langchain.prompts import PromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from langchain_community.callbacks import get_openai_callback
from langchain_core.pydantic_v1 import Field, BaseModel
from langchain_core.runnables import RunnableParallel
from operator import itemgetter


# *************** IMPORT MODEL ***************
from models.llms import LLMModels

# *************** IMPORT VALIDATOR ***************
from validator.flashcard_payload_checker import (
    validate_company,
    validate_job_detail,
    validate_cv,
    validate_qna_list,
)

class FlashcardResponse(BaseModel):
    flashcards: list = Field(description=[{
        "category": "type of the interview question as technical or soft skill question",
        "question": "question of the interview",
        "suggest_answer": "question of the interview"
        }]
      )
    
# *************** MAIN ***************
def generate_flashcards(cv, company, job_detail):
    """
    Generate a list of interview flashcards based on the provided CV, company information, and job details.

    This function uses the provided CV, company information, and job details to generate a specified number of 
    flashcards. Each flashcard contains a question and an answer, formulated using the STAR method.

    Args:
        cv (dict): A dictionary containing the candidate's CV information. 
                   Expected keys: 'summary', 'work_experience', 'education', 'projects', and 'skills'.
        company (dict): A dictionary containing the company information.
                        Expected keys: 'company_name' and 'company_detail'.
        job_detail (dict): A dictionary containing the job details.
                           Expected keys: 'job_position' and 'job_description'.
 
    Returns:
        dict: A dictionary containing the generated flashcards and token usage information.
              Keys: 'result', 'tokens_in', and 'tokens_out'.
    """
    # *************** VALIDATOR ***************
    # ***** Validate required fields
    if not validate_cv(cv):
        raise KeyError('Invalid CV format')
    
    if not validate_company(company):
        raise KeyError('Invalid company format')
    
    if not validate_job_detail(job_detail):
        raise KeyError('Invalid job description format')

    # *************** INPUT ***************
    # ***** Prepare the input data for the prompt
    summary = cv["summary"]

    # ***** separate work_experience content in cv
    work_experience = "\n".join([f"""
        Company: {exp['company_name']}, 
        Title: {exp['job_title']}, 
        Date: {exp['date']}, 
        Description: {', '.join(exp['description'])}
        """ for exp in cv["work_experience"]])
    
    # ***** separate education content in cv
    education = "\n".join([f"""
        School: {edu['school_name']}, 
        Date: {edu['date']}, 
        Degree: {edu['degree_major']}, 
        Description: {', '.join(edu['description'])}
        """ for edu in cv["education"]])
    
    # ***** separate project content in cv
    projects = "\n".join([f"""
        Project: {proj['project_name']}, 
        Date: {proj['date']}, 
        Description: {', '.join(proj['description'])}
        """ for proj in cv["project"]])
    
    skills = ", ".join(cv["skills"])

    job_title = job_detail["job_position"]
    job_description = job_detail["job_description"]
    company_name = company["company_name"]
    company_detail = company["company_detail"]

    # ***** Define the prompt template
    base_prompt = """
    I have the following CV details:
    
    Summary: {summary}
    
    Work Experience:
    {work_experience}
    
    Education:
    {education}
    
    Projects:
    {projects}
    
    Skills:
    {skills}
    
    I am applying for the position of {job_title} at {company_name}. The job description is:
    {job_description}
    
    Company Profile:
    {company_detail}
    
    Please generate an array of 10 relevant interview questions and suggested answers in STAR method based on my CV, Company Profile, and the job description:
    
    - 5 technical skill questions
    - 5 soft skill questions
    
    The output should be an array of JSON objects, following structure:
    {format_instructions}
    """

    # ***** Initialize OpenAI LLM
    llm = LLMModels().llm_cv
    parser = JsonOutputParser(pydantic_object=FlashcardResponse)

    # ***** Intiate Prompt functionality
    prompt_template = PromptTemplate(
        template=base_prompt,
        input_variables=[
            "summary", 
            "work_experience", 
            "education", 
            "projects", 
            "skills", 
            "company_name",
            "company_detail",
            "job_title",
            "job_description",
            ],
        partial_variables={"format_instructions": parser.get_format_instructions()}
    )
    # ********* Setup Runnable Chain
    runnable_flashcard = RunnableParallel(
                        {
                            "summary": itemgetter('summary'),
                            "work_experience": itemgetter('work_experience'),
                            "education": itemgetter('education'),
                            "projects": itemgetter('projects'),
                            "skills": itemgetter('skills'),
                            "company_name": itemgetter('company_name'),
                            "company_detail": itemgetter('company_detail'),
                            "job_title": itemgetter('job_title'),
                            "job_description": itemgetter('job_description')
                        }
                    )
    flashcard_chain = ( 
                runnable_flashcard
                | prompt_template
                | llm
                | parser
                )

    # *************** PROCESS ***************
    # ***** activate tokens track
    with get_openai_callback() as flash_cb:
        # ***** Generate the flashcards
        response = flashcard_chain.invoke({
            "summary": summary,
            "work_experience": work_experience,
            "education": education,
            "projects": projects,
            "skills": skills,
            "company_name": company_name,
            "company_detail": company_detail,
            "job_title": job_title,
            "job_description": job_description
        })
    
    # *************** OUTPUT ***************
    # ***** validate response is exist and reformat the response as json
    print(response)
    if 'flashcards' in response:
        flash_card_qa = {
            "result": response['flashcards'],
            "tokens_in": flash_cb.prompt_tokens,
            "tokens_out": flash_cb.completion_tokens
            }
    else:
        raise KeyError("Response not contains list of questions and suggest_answer")

    # ***** validate each list of response is a json with question and answer
    if validate_qna_list(flash_card_qa["result"]):
        return flash_card_qa
   
    else:
        raise ValueError("Response is not a valid list of objects with 'category', 'question' and 'suggest_answer' fields")


if __name__ == '__main__':
    # ***** local testing section
    cv = {
        "summary": {
            "name": "Billy Hill",
            "Location": "Missouri, USA",
            "phone": "+1 568 888 000",
            "email": "john_doe@gmail.com",
            "summary": "work as a chef"
        },
        "work_experience": [{
            "company_name": "Spice Legend",
            "job_title": "Chef junior",
            "date": "APR 2024 to MAY 2025",
            "description": ["preparing dishes", "assisting the head chef", "managing inventory"]
        }],
        "education": [{
            "school_name": "Sidehill College",
            "date": "APR 2024 to MAY 2026",
            "degree_major": "Computer Engineering",
            "description": []
        }],
        "project": [{
            "project_name": "Bridge Reinforcement",
            "date": "APR 2024 to MAY 2026",
            "description": []
        }],
        "skills": []
    }

    company = {
        "company_name": "USU Software AG",
        "company_detail": "Als führender Anbieter von Software und Services für das IT- und Customer Service Management ermöglicht USU Unternehmen, die Anforderungen der heutigen digitalen Welt zu meistern. Globale Organisationen setzen unsere Lösungen ein, um Kosten zu senken, agiler zu werden und Risiken zu reduzieren – mit smarteren Services, einfacheren Workflows und besserer Zusammenarbeit. Mit mehr als 40 Jahren Erfahrung und Standorten weltweit bringt das USU-Team Kunden in die Zukunft.See more"
    }
    job_detail = {
        "job_position": "Praktikant (w/d/m) Entwicklung IT-Monitoring Suite",
        "job_description": "Ändere mit uns die Servicewelt und lass uns gemeinsam Unternehmen durch bessere Workflows, bessere Zusammenarbeit und besseren Informationsfluss begeistern! USU ist der führende Anbieter von Software- und Servicelösungen für IT & Customer Service Management. Es erwarten Dich mehr als 750 tolle Kolleg:innen an 17 Standorten in vielen Ländern, die sich darauf freuen, zusammen mit Dir Maßstäbe für eine bessere Servicewelt zu setzen.An unserem Echterdinger Standort erwarten Dich 30 versierte Kolleg:innen, die Dir bei Deinem Praktikum aktiv zur Seite stehen. Damit Dein Praktikum erfolgreich verläuft, steht Dir ein fachlicher Betreuer zur Seite. Regelmäßige Update Meetings helfen Dir, Deine Aufgaben zielgerichtet im Blick zu behalten.Gemeinsam begeistern wir unsere Kunden für eine bessere Servicewelt. Join us now!Deine Aufgaben:• Eigenständige Entwicklung kleinerer Features mit Spring Boot, React und Java• Eigenständige Entwicklung von Unit Tests• Mitwirkung bei der Verbesserung der Bauprozesse• Administration von GitDeine Qualifikationen:• Du studierst (angewandte) Informatik, Software Engineering oder ein vergleichbares Studienfach• Softwareentwicklung begeistert dich und es macht dir Spaß, dein Fachwissen zu erweitern und Neues auszuprobieren• Dich zeichnet eine analytische, strukturierte und lösungsorientierte Arbeitsweise ausApplication deadlineNot givenJob CategoryProgramming"    
        }
    print(generate_flashcards(cv, company, job_detail))