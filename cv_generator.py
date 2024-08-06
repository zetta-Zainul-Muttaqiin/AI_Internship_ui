# *************** IMPORTS ***************
from langchain_core.pydantic_v1 import Field, BaseModel
from langchain_core.output_parsers import JsonOutputParser
from langchain.prompts import PromptTemplate
from langchain_core.runnables import RunnableParallel

from operator import itemgetter
from langchain_community.callbacks import get_openai_callback

# *************** IMPORT MODEL ***************
from models.llms import LLMModels

# *************** IMPORT VALIDATOR ***************
from validator.cv_payload_checker import (
    check_missing_keys,
    check_missing_values,
    check_incorrect_datatypes,
    validate_description_response,
)

# *************** ENVIRONMENT LOAD ***************
from setup import REQUIRED_FIELDS


# ********** Define Pydantic models for structured data handling
class SummaryAnswer(BaseModel):
    recommended: str = Field(description="A well-balanced summary that aligns closely with the input, providing a concise yet comprehensive overview.")
    simplified: str = Field(description="A shortened version of the summary, minimizing details to present the core information succinctly.")
    extended: str = Field(description="A detailed and elaborative summary, expanding on the input to provide a thorough explanation.")

class SkillsResult(BaseModel):
    recommended: list[str] = Field(description="array of well-balanced skills descriptions that aligns closely with the input, providing a concise yet comprehensive overview.")
    simplified: list[str] = Field(description="array of shortened version of the skills descriptions, minimizing details to present the core information succinctly.")
    extended: list[str] = Field(description="array of detailed and elaborative skills descriptions, expanding on the input to provide a thorough explanation.")

class DescriptionGenerator(BaseModel):
    recommended: list[str] = Field(description="array of 3 well-balanced descriptions that aligns closely with the input, providing a concise yet comprehensive overview.")
    simplified: list[str] = Field(description="array of 3 shortened version of the descriptions, minimizing details to present the core information succinctly.")
    extended: list[str] = Field(description="array of 3 detailed and elaborative descriptions, expanding on the input to provide a thorough explanation.")


# ********** Function summary AI to create the summary of the aplicant
def summary_ai(summary, keywords, job_info,):
    """
    Generates a summary description based on keywords and job information.

    Args:
        - summary  (str): Summary description from field input in cv form  
        - keywords (str): Keywords related to the job description.
        - job_info (str): Detailed information about the job.

    Returns:
        dict: Dictionary containing the generated summary, tokens used for input and output.
    """

    summary_template = """
    You are an expert in creating first-person view resume summaries for curriculum vitae. Please generate an upgraded and more detailed summary description for curriculum vitae based on the provided INPUT.

    INPUT:
    "summary": {summary}
    "keywords": {keywords}
    "job_info": {job_info}

    Based on the "summary" and "keywords", create an upgraded and more detailed summary description tailored to "job_info" while highlighting my competency that suits to the "job_info" for curriculum vitae section following the language used in the "keywords".

    Create a new JSON object with the summary tailored to the "job_info" in the following JSON format:
    {format_instructions}

    NOTE: Ensure the upgraded and more detailed summary is written in the same language as the input "keywords".
    """

    # ********** Initialize parser and prompt template for AI response handling
    summary_ai_parser = JsonOutputParser(pydantic_object=SummaryAnswer)
    summary_prompt = PromptTemplate(
        template=summary_template,
        input_variables=[
            "summary",
            "keywords",
            "job_info"
        ],
        partial_variables={
            "format_instructions": summary_ai_parser.get_format_instructions()
        },
    )
    runnable_summary_ai = RunnableParallel(
        {   
            "summary": itemgetter("summary"),
            "keywords": itemgetter("keywords"),
            "job_info": itemgetter("job_info"),
        }
    )

    # ********** Define the chain of operations for generating summary AI response
    summary_ai_chain = (
                  runnable_summary_ai
                | summary_prompt
                | LLMModels().llm_cv
                | summary_ai_parser
                )
    # ********** Invoke AI chain and handle response with OpenAI callback
    with get_openai_callback() as cb:
        response = summary_ai_chain.invoke(
            {
            'summary': summary,
            'keywords': keywords,
            'job_info':job_info,
            }
        )
        token_in = cb.prompt_tokens
        token_out = cb.completion_tokens
        print(cb)

    # ********** Validate and structure AI response for summary
    validate_description_response(response)

    result = {
        'summary_ai_result': {
            "recommended": response["recommended"],
            "simplified": response["simplified"],
            "extended": response["extended"]
        },
        "token_in": token_in,
        "token_out": token_out,
    }
    return result

# ********** Function WorkExperienceAI Creation
def work_experience_ai(work_experience, keywords, job_info):
    """
    Generates a work experience description based on provided work experience, keywords, and job information.

    Args:
        - work_experience (Dict): Details of work experience from field input in cv form.
        - keywords (str): Keywords related to the job description.
        - job_info (str): Detailed information about the job.

    Returns:
        dict: Dictionary containing the generated work experience description, tokens used for input and output.
    """
    work_experience_template = """
    You are an expert in creating resume descriptions. Please generate a work experience description based on the provided INPUT.

    INPUT:
    "work_experience": {work_experience}
    "keywords": {keywords}
    "job_info": {job_info}

    Based on the "work_experience", "keywords", and "job_info", create a work experience description section following the language used in the "keywords".

    Create a new JSON object with the work experience tailored to the "job_info" in the following JSON format:
    {format_instructions}

    NOTE: Ensure the descriptions are written in the same language as the input "keywords".
    NOTE: Do not use any personal pronouns or mention the name of the applicant.
    """
    # ********** Initialize parser and prompt template for AI response handling
    work_experience_parser = JsonOutputParser(pydantic_object=DescriptionGenerator)
    work_experience_prompt = PromptTemplate(
        template=work_experience_template,
        input_variables=[
            "work_experience",
            "keywords",
            "job_info"
        ],
        partial_variables={
            "format_instructions": work_experience_parser.get_format_instructions()
        },
    )
    runnable_work_experience_ai = RunnableParallel(
        {
            "work_experience": itemgetter("work_experience"),
            "keywords": itemgetter("keywords"),
            "job_info": itemgetter("job_info"),
        }
    )

    # ********** Define the chain of operations for generating work experience AI response
    work_experience_ai_chain = ( runnable_work_experience_ai
                | work_experience_prompt
                | LLMModels().llm_cv
                | work_experience_parser
    )
    # **********  Invoke AI chain and handle response with OpenAI callback
    with get_openai_callback() as cb:
        response = work_experience_ai_chain.invoke(
            {
                'work_experience':work_experience,
                'keywords': keywords,
                'job_info':job_info
            }
        )
        token_in = cb.prompt_tokens
        token_out = cb.completion_tokens
        print(cb)

    # ********** Validate and structure AI response for work experience
    validate_description_response(response)

    result = {
        'work_experience_ai_result': {
            "recommended": response["recommended"],
            "simplified": response["simplified"],
            "extended": response["extended"]
        },
        "token_in": token_in,
        "token_out": token_out,
    }
    return result

# ********** Function to education ai creation
def education_ai(education, keywords, job_info):
    """
    Generates an education description based on provided education details, keywords, and job information.

    Args:
        - education (Dict): Details of education from field input in cv form.
        - keywords (str): Keywords related to the job description.
        - job_info (str): Detailed information about the job.

    Returns:
        dict: Dictionary containing the generated education description, tokens used for input and output.
    """

    education_template = """
    You are an expert in creating resume descriptions. Please generate a education description based on the provided INPUT.

    INPUT:
    "education": {education}
    "keywords": {keywords}
    "job_info": {job_info}

    Based on the "education", "keywords", and "job_info", create a education description section following the language used in the "keywords".

    Create a new JSON object with the education tailored to the "job_info" in the following JSON format:
    {format_instructions}

    NOTE: Ensure the descriptions are written in the same language as the input "keywords".
    NOTE: Do not use any personal pronouns or mention the name of the applicant.
    """
    
    # ********** Initialize parser and prompt template for AI response handling
    education_ai_parser = JsonOutputParser(pydantic_object=DescriptionGenerator)
    education_prompt = PromptTemplate(
            template=education_template,
            input_variables=[
                "education",
                "keywords",
                "job_info"],
            partial_variables={"format_instructions": education_ai_parser.get_format_instructions()},
            )
    
    runnable_education_ai = RunnableParallel(
                            {
                                "education": itemgetter("education"),
                                "keywords": itemgetter("keywords"),
                                "job_info": itemgetter("job_info"),
                            }
                        )
    
    # ********** Define the chain of operations for generating education AI response
    education_ai_chain = ( runnable_education_ai
                | education_prompt
                | LLMModels().llm_cv
                | education_ai_parser
                )
    # ********** Invoke AI chain and handle response with OpenAI callback
    with get_openai_callback() as cb:
        response = education_ai_chain.invoke(
            {
                'education':education,
                'keywords': keywords,
                'job_info':job_info,
            }
        )
        
        token_in = cb.prompt_tokens
        token_out = cb.completion_tokens
        print(cb)
    
    # ********** Validate and structure AI response for education
    validate_description_response(response)

    result = {
        "education_ai_result": {
            "recommended": response["recommended"],
            "simplified": response["simplified"],
            "extended": response["extended"]
        },
        "token_in": token_in,
        "token_out": token_out,
    }
    return result

# ********** Function to generate project descrition
def project_ai(project, keywords, job_info):
    """
    Generates a project description based on provided project details, keywords, and job information.

    Args:
        - project (Dict): Details of the project from field input in cv form.
        - keywords (str): Keywords related to the job description.
        - job_info (str): Detailed information about the job.

    Returns:
        dict: Dictionary containing the generated project description, tokens used for input and output.
    """

    project_template = """
    You are an expert in creating resume descriptions. Please generate a project description based on the provided INPUT.

    INPUT:
    "project": {project}
    "keywords": {keywords}
    "job_info": {job_info}

    Based on the "project", "keywords", and "job_info", create a project description section following the language used in the "keywords".

    Create a new JSON object with the project tailored to the "job_info" in the following JSON format:
    {format_instructions}

    NOTE: Ensure the descriptions are written in the same language as the input "keywords".
    NOTE: Do not use any personal pronouns or mention the name of the applicant.
    """
    
    # ********** Initialize parser and prompt template for AI response handling
    parser = JsonOutputParser(pydantic_object=DescriptionGenerator)
    project_prompt = PromptTemplate(
        template=project_template,
        input_variables=[
            "project",
            "keywords" 
            "job_info"],
        partial_variables={"format_instructions": parser.get_format_instructions()},
    )
    
    runnable = RunnableParallel(
        {
        "project": itemgetter("project"),
        "keywords": itemgetter("keywords"),
        "job_info": itemgetter("job_info"),
    })

    # ********** Define the chain of operations for generating project AI response
    chain = (runnable | project_prompt | LLMModels().llm_cv  | parser)

    # ********** Define input data
    input_data = {
        "project": project,
        "keywords": keywords,
        "job_info": job_info
    }

    # ********** Invoke the chain and print the result
    with get_openai_callback() as cb:
        response = chain.invoke(input_data)
        token_in = cb.prompt_tokens
        token_out = cb.completion_tokens
        print(cb)
    
    validate_description_response(response)

    # ********** Structuring the output
    result = {
        "project_result_ai": {
            "recommended": response["recommended"],
            "simplified": response["simplified"],
            "extended": response["extended"]
        },
        "token_in": token_in,
        "token_out": token_out,
    }
    # ********** Print the structured output
    return result

# ********** Function to generate skills list description
def skills_ai(skills, cv_description, keywords, job_info):
    """
    Generates a skills description based on provided skills CV description, keywords, and job information.

    Args:
        - skills (List) : List of skills from field input in cv form.
        - cv_description (Dict): CV Description from othre sections (summary/work_experience/education/project).
        - keywords (str): Keywords related to the job description.
        - job_info (str): Detailed information about the job.

    Returns:
        dict: Dictionary containing the generated skills description, tokens used for input and output.
    """

    skills_template = """
    You are an expert in creating resume descriptions. Please generate skills description based on the provided INPUT.

    INPUT:
    "skills": {skills}
    "cv_description": {cv_description}
    "keywords": {keywords}
    "job_info": {job_info}

    Based on the "skills", "cv_description", "keywords", and "job_info", create skills description section following the language used in the "keywords".

    Create a new JSON object with the skills tailored to the "job_info" in the following JSON format:
    {format_instructions}

    NOTE: Ensure the descriptions are written in the same language as the input "keywords".
    NOTE: Do not use any personal pronouns or mention the name of the applicant.
    """

    # ********** Initialize parser and prompt template for AI response handling
    parser = JsonOutputParser(pydantic_object=SkillsResult)
    skills_prompt = PromptTemplate(
        template=skills_template,
        input_variables=["skills","cv_description", "keywords", "job_info"],
        partial_variables={"format_instructions": parser.get_format_instructions()},
    )

    runnable = RunnableParallel({
        "skills": itemgetter("skills"),
        "cv_description": itemgetter("cv_description"),
        "keywords": itemgetter("keywords"),
        "job_info": itemgetter("job_info"),
    })

    # ********** Define the chain of operations for generating skills AI response
    chain = (
        runnable 
        | skills_prompt 
        | LLMModels().llm_cv 
        | parser
    )

    
    input_data = {
        "skills": skills,
        "cv_description": cv_description,
        "keywords": keywords,
        "job_info": job_info
    }

    # ********** Invoke the chain and return the result
    with get_openai_callback() as cb:
        response = chain.invoke(input_data)
        token_in = cb.prompt_tokens
        token_out = cb.completion_tokens
        print(cb)
        print(response)

    validate_description_response(response)

    # ********** Structuring the output
    result = {
        "skills_ai_result": {
            "recommended": response["recommended"],
            "simplified": response["simplified"],
            "extended": response["extended"]
        },
        "token_in": token_in,
        "token_out": token_out,
    }
    return result

# *************** MAIN ***************
# ********** Function to Create CV adapted to job
def cv_editor(cv_segment, cv_data_segment, keywords, job_info, cv_description):
    """
    Edits the CV segment based on job requirements using various AI models.

    Args:
        - cv_segment (str): Segment of CV to be edited ('summary', 'work_experience', 'education', 'project', 'skills').
        - cv_data_segment (dict): Data specific to the CV segment.
        - keywords (str): Keywords from user input.
        - job_info (str): Detailed information about the job.
        - cv_description (str): Description of CV (specifically used in 'skills' section).

    Returns:
        dict: Dictionary containing the edited CV segment, tokens used for input and output.
    """

    # *************** VALIDATOR ***************
    # ********** Checking missing key, value and format same as expected
    check_missing_keys(cv_data_segment, cv_segment)
    check_missing_values(cv_data_segment, cv_segment)
    check_incorrect_datatypes(cv_data_segment, cv_segment)  
     
    
    if cv_segment == 'summary':
        summary_result = summary_ai(cv_data_segment, keywords, job_info)
        return summary_result
    
    elif cv_segment == 'work_experience':
        work_result = work_experience_ai(cv_data_segment, keywords, job_info)
        return work_result
    
    elif cv_segment == 'education':
        education_result = education_ai(cv_data_segment, keywords, job_info)
        return education_result
    
    elif cv_segment == 'project':
        project_result = project_ai(cv_data_segment, keywords, job_info)
        return project_result
    
    elif cv_segment == 'skills':
        skills_result = skills_ai(cv_data_segment, cv_description, keywords, job_info)
        return skills_result
    else:
        raise KeyError(f"Missing cv_section key: expected one of {REQUIRED_FIELDS.keys} but got {cv_segment}")

# ********** Function summary AI to create the summary of the aplicant
def create_cv_summary_ai(summary, keywords):

    summary_template = """"
    INPUT:
    "summary": {summary}
    "keywords": {keywords}

    Please create summary for CV. Based on "summary" and "keywords", create new JSON in the following JSON format:
    {format_instructions}
    The language of summary_ai_result following the "keywords" language.
    NOTE: For the result don't say any PERSONAL PRONOUNCE OR SAY THE NAME OF THE APPLICANT
    """
    summary_ai_parser = JsonOutputParser(pydantic_object=SummaryAnswer)
    summary_prompt = PromptTemplate(
        template=summary_template,
        input_variables=["summary"],
        partial_variables={
            "format_instructions": summary_ai_parser.get_format_instructions()
        },
    )
    runnable_summary_ai = RunnableParallel({
        "summary": itemgetter("summary"),
        "keywords": itemgetter("keywords")
        })

    summary_ai_chain = ( 
        runnable_summary_ai
        | summary_prompt
        | LLMModels().llm_cv
        | summary_ai_parser
    )

    with get_openai_callback() as cb:
        response = summary_ai_chain.invoke(
            {
            'summary': summary,
            'keywords': keywords
            }
        )
        token_in = cb.prompt_tokens
        token_out = cb.completion_tokens
        print(cb)
    
    result = {
        'summary_ai_result': {
            "recommended": response["recommended"],
            "simplified": response["simplified"],
            "extended": response["extended"]
        },
        "token_in": token_in,
        "token_out": token_out,
    }
    return result
    
# ********** Function WorkExperienceAI Creation
def create_cv_work_experience_ai(work_experience, keywords):

    work_experience_template = """
    INPUT:
    "work_experience": {work_experience}
    "keywords": {keywords}

    Based on  the "work_experience" and "keywords", create new JSON in following JSON format:
    {format_instructions}
    The language of work_experience_ai following the "keywords" language.
    """
    work_experience_parser = JsonOutputParser(pydantic_object=DescriptionGenerator)
    work_experience_prompt = PromptTemplate(
        template=work_experience_template,
        input_variables=["work_experience"],
        partial_variables={
            "format_instructions": work_experience_parser.get_format_instructions()
        },
    )
    runnable_work_experience_ai = RunnableParallel(
        {
            "work_experience": itemgetter("work_experience"),
            "keywords": itemgetter("keywords")
        }
    )
    work_experience_ai_chain = ( 
        runnable_work_experience_ai
        | work_experience_prompt
        | LLMModels().llm_cv
        | work_experience_parser
    )
    with get_openai_callback() as cb:
        response = work_experience_ai_chain.invoke(
            {
                'work_experience':work_experience,
                'keywords':keywords
            }
        )
        token_in = cb.prompt_tokens
        token_out = cb.completion_tokens
        print(cb)

    result = {
        'work_experience_ai_result': {
            "recommended": response["recommended"],
            "simplified": response["simplified"],
            "extended": response["extended"]
        },
        "token_in": token_in,
        "token_out": token_out,
    }
    return result

# ********** Function to education ai creation
def create_cv_education_ai(education, keywords):
  
    education_template = """
    INPUT:
    "education": {education}
    "keywords": {keywords}

    Based on  the "education" and "keywords", create new JSON in following format:
    {format_instructions}
    The language of education_ai following the "keywords" language.
    """
    education_ai_parser = JsonOutputParser(pydantic_object=DescriptionGenerator)
    education_prompt = PromptTemplate(
        template=education_template,
        input_variables=["education"],
        partial_variables={
            "format_instructions": education_ai_parser.get_format_instructions()
        },
    )
    runnable_education_ai = RunnableParallel(
        {
            "education": itemgetter("education"),
            "keywords": itemgetter("keywords")
        }
    )
    education_ai_chain = ( 
        runnable_education_ai
        | education_prompt
        | LLMModels().llm_cv
        | education_ai_parser
    )

    with get_openai_callback() as cb:
        response = education_ai_chain.invoke(
            {
                'education':education,
                'keywords':keywords
            }
        )
        
        token_in = cb.prompt_tokens
        token_out = cb.completion_tokens
        print(cb)

    result = {
        "education_ai_result": {
            "recommended": response["recommended"],
            "simplified": response["simplified"],
            "extended": response["extended"]
        },
        "token_in": token_in,
        "token_out": token_out,
    }
    return result
    
# ********** Function to project ai adapt
def create_cv_project_ai(project, keywords):
    
    project_template = """"
    INPUT:
    "project": {project}
    "keywords": {keywords}

    Based on "project" and "keywords", create a new JSON in the following JSON format:
    {format_instructions}
    The language of project_ai following the "keywords" language.
    """
    parser = JsonOutputParser(pydantic_object=DescriptionGenerator)
    project_prompt = PromptTemplate(
        template=project_template,
        input_variables=["project"],
        partial_variables={
            "format_instructions": parser.get_format_instructions()
        },
    )
    runnable_project = RunnableParallel({
        "project": itemgetter("project"),
        "keywords": itemgetter("keywords")
    })

    project_ai_chain = (
        runnable_project 
        | project_prompt 
        | LLMModels().llm_cv 
        | parser
    )

    input_data = {
        "project": project,
        "keywords": keywords
    }

     # ********** Invoke the chain and print the result
    with get_openai_callback() as cb:
        response = project_ai_chain.invoke(input_data)
        token_in = cb.prompt_tokens
        token_out = cb.completion_tokens
        print(cb)

    # ********** Structuring the output
    result = {
        "project_result_ai": {
            "recommended": response["recommended"],
            "simplified": response["simplified"],
            "extended": response["extended"]
        },
        "token_in": token_in,
        "token_out": token_out,
    }
    # ********** Print the structured output
    return result

# ********** Function to create Skills
def create_cv_skills_ai(skills, cv_description, keywords):
    
    skills_template ="""
    INPUT:
    "skills": {skills}
    "cv_description": {cv_description}
    "keywords": {keywords}

    Based on the "skills", "cv_description", and "keywords" create skills description section following the language used in the "keywords".
    {format_instructions}

    NOTE: Ensure the descriptions are written in the same language as the input "keywords".
    NOTE: Do not use any personal pronouns or mention the name of the applicant.
    """

    parser = JsonOutputParser(pydantic_object=SkillsResult)
    skills_prompt = PromptTemplate(
        template=skills_template,
        input_variables=["skills", "cv_description", "keywords"],
        partial_variables={
            "format_instructions": parser.get_format_instructions()
        },
    )

    runnable = RunnableParallel({
        "cv_description": itemgetter("cv_description"),
        "keywords": itemgetter("keywords"),
        "skills": itemgetter("skills"),
    })
    chain = (
        runnable 
        | skills_prompt 
        | LLMModels().llm_cv 
        | parser)
    
    input_data = {
        "cv_description": cv_description,
        "keywords": keywords,
        "skills": skills
    }
    # ********** Invoke the chain and return the result
    with get_openai_callback() as cb:
        response = chain.invoke(input_data)
        token_in = cb.prompt_tokens
        token_out = cb.completion_tokens
        print(cb)
        print(response)

    # ********** Structuring the output
    result = {
        "skills_ai_result": {
            "recommended": response["recommended"],
            "simplified": response["simplified"],
            "extended": response["extended"]
        },
        "token_in": token_in,
        "token_out": token_out,
    }
    return result


# ********* Function to create CV
def cv_create(cv_segment, cv_data_segment, keywords, cv_description): 
    
    # *************** VALIDATOR ***************
    # ********** Checking missing key, value and format same as expected
    check_missing_keys(cv_data_segment, cv_segment)
    check_missing_values(cv_data_segment, cv_segment)
    check_incorrect_datatypes(cv_data_segment, cv_segment) 
    
    if cv_segment == 'summary':
        description_response = create_cv_summary_ai(cv_data_segment, keywords)
        return description_response
    
    elif cv_segment == 'work_experience':
        description_response = create_cv_work_experience_ai(cv_data_segment, keywords)
        return description_response
    
    elif cv_segment == 'education':
        description_response = create_cv_education_ai(cv_data_segment, keywords)
        return description_response
    
    elif cv_segment == 'project':
        description_response = create_cv_project_ai(cv_data_segment, keywords)
        return description_response
    
    elif cv_segment == 'skills':
        description_response = create_cv_skills_ai(cv_data_segment, cv_description, keywords)
        return description_response   
    else:
        raise KeyError(f"Missing cv_section key: expected one of {REQUIRED_FIELDS.keys} but got {cv_segment}")

if __name__ == "__main__":
    # ********* Local Testing Section

    cv_segment = "summary"
    cv_data_segment = {"description": 1}
    keywords = "make a summary is acceptable for the job"
    job_info = "For more than 115 years, Securex has been helping its clients and employees to shine in their professional lives. Every day, our 1,700 colleagues are committed to supporting entrepreneurs and employers in their professional activities.We offer these entrepreneurs and employers the most extensive range of services on the market: Self-employment Counter, Social Insurance Fund, Payroll services, External Service for Prevention and Protection at Work, Insurance, HR consulting and Medical Controls. This allows us to help our clients at every stage of their entrepreneurship and in the development of their personnel policy.Securex is active in 5 European countries (Belgium, Netherlands, France, Luxembourg and Spain) and has the ambition to keep expanding this international presence.Moreover, Securex obtained the certificate Pioneer Employer '22. Pioneer Employer is a movement of Belgian employers who choose to put people first in their policy on hybrid working and mobility. They work around three pillars: less travel to work, people-oriented hybrid work and smarter & greener travel to work.As a result, we have made a strong commitment to a New Way of Working policy in recent years. At Securex, we work at least 1 day in the office and are furthermore free to plan our work with clients and colleagues. We have redesigned our offices with 'activity-based zones'We mainly work together in Majors (Brussels, Ghent, Liège, Antwerp, Charleroi, Kortrijk, Louvain-la-neuve) but also have smaller Agencies or local offices and Meeting points where work is done and we can help clients further. Some colleagues even work at our clients' premises.See more"
    cv_description = None
    result = cv_editor(cv_segment, cv_data_segment, keywords, job_info, cv_description)
    print(result)