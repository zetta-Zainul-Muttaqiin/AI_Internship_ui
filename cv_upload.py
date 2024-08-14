# *************** IMPORTS ***************
from langchain_core.pydantic_v1 import Field, BaseModel
from langchain_core.output_parsers import JsonOutputParser
from langchain.prompts import PromptTemplate

from operator import itemgetter
from langchain_community.callbacks import get_openai_callback
import requests

# ***** PDFTOTEXT library *****
# ***** linux
# from pdftotext import PDF

# ***** windows
import tempfile
import os
import subprocess as sp

# *************** IMPORT MODEL ***************
from models.llms import LLMModels
from models.lingua import LinguaModel

# *************** IMPORT VALIDATOR ***************
from helpers.read_url_helper import request_url

# *************** IMPORT VALIDATOR ***************
from validator.cv_payload_checker import (
    validate_response,
    is_url,
)

# *************** ENVIRONMENT LOAD ***************
from setup import OUTPUT_CV_EXTRACT

class ExtractorResume(BaseModel):

    summary: dict = Field(description={
        "name": "CV owner name",
        "Location": "city, country",
        "phone": "string of phone number",
        "email": "email",
        "summary": "work summary of the CV owner",
        }
      )
    work_experience: list = Field(description=[{
        "company_name": "company name cv owner worked",
        "job_title": "string of job position",
        "date": "start and end of MONTH and YEAR",
        "description": "points of the description related to task, progress and achivement in company"
        }]
      )
    education: list = Field(description=[{
        "school_name": "school name, college name",
        "date": "start and end of MONTH and YEAR",
        "degree_major": "degree major of especially in university",
        "score": "A float of final score or evaluate point in university",
        "description": "points of the description about activity and achivement during school. Make it as detail as possible"
        }]
      )
    project: list = Field(description=[{
        "project_name": "the project name",
        "date": "start and end of MONTH and YEAR",
        "description": "describe what is project doing and the goal"
        }]
      )
    skills: list = Field(description="list of skills mentions at cv in array format")

# ********** Function for build Chain based: prompt, parser, llm
def llm_base_cv_extractor(parser, llm):
    """
    Function to build the chain for CV extraction using LLM.

    Args:
        parser (JsonOutputParser): The parser for extracting CV fields.
        llm (LLMModels): The language model for extracting CV fields.

    Returns:
        Chain: The constructed chain for CV extraction.
    """
    extractor_template = """
        You are a CV extractor. Your task is to extract all information from the "CV" below as detail as possible without reducing the "CV" content. To retrieve the information, you need to understand the layout of the CV.
        "CV" : {CV}
        The field will extract following {format_instructions}
        The field as output must be in {language} and has return as JSON Format:
        {output_cv_extract}
        """
    extractorPrompt = PromptTemplate(
        template=extractor_template,
        input_variables=[
            "CV",
            "language",
            "output_cv_extract"
            ],
        partial_variables={"format_instructions": parser.get_format_instructions()},
    )

    extractorChain = (
        {
          "CV": itemgetter("CV"),
          "language": itemgetter("language"),
          "output_cv_extract": itemgetter("format")
        }
        | extractorPrompt
        | llm
        | parser
    )

    return extractorChain

# ********** Function for generate extraction of cv with Chain LLM
def extract_cv_llm(chain, cv_content, language):
    """
    Function to extract CV content using the provided chain.

    Args:
        chain (Chain): The chain for extracting CV fields.
        cv_content (str): The content of the CV in text format.

    Returns:
        dict: The extracted CV fields.
    """
    result = chain.invoke(
        {
            "CV": cv_content,
            "language": language,
            "format": OUTPUT_CV_EXTRACT
        }
    )
    return result

# ********** Function for read a pdf, from pdf > images > text using OCR
def pdf_to_text(pdf_bytes):
    """
    Function to convert PDF to text using pdftotext within the layout.

    Args:
        pdf_bytes (string): a pdf bytes after request an url pdf
    Returns:
        string: text converted from PDF with the layout of the text also
    """
    try:

        # ***** set a temporary file for the pdf bytes
        # with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as temp_pdf:
        #     temp_pdf.write(pdf_bytes)
        #     temp_pdf_path = temp_pdf.name
    
        args = ['pdftotext', '-layout', pdf_bytes, '-']
        cp = sp.run(
        args, 
        stdout=sp.PIPE, 
        stderr=sp.PIPE,
        check=True,
        encoding='utf-8', 
        text=True
        )

        pdf = cp.stdout
    except Exception as er_pdf:
        print("An error occurred while converting PDF to text:", str(er_pdf))
    
    # ***** delete the temporary file    
    # finally:
    #     os.remove(temp_pdf_path)

    # ***** join the pages after extract the text
    join_page = ""
    for page in pdf:
        join_page += page

    return join_page

# ********** MAIN Function for extract cv 
def cv_extractor(cv_path):
    """
    Main Function to extract a CV for all possible field using OCR and LLM.

    Args:
        pdf_path (string): Path to the PDF file/ URL of pdf file
    Returns:
        Dict:
            Dict    : Required field existed following output_cv_extract
            Int     : Input/prompt tokens usage for llm
            Int     : Output/generated text tokens usage after generate text with LLM
    """
    # **********  call function validate input as url
    # is_url(cv_path)
    
    # ********* call function for read a pdf to temporary file
    # temp_pdf = request_url(cv_path)
    
    # ********** call function to convert pdf to text using pdftotext
    context = pdf_to_text(cv_path)
    # ********** call function fpr generate chain for generate response
    extractorParser = JsonOutputParser(pydantic_object=ExtractorResume)
    cv_language = LinguaModel().lingua.detect_language_of(context).name.lower()
    chain = llm_base_cv_extractor(extractorParser, LLMModels().llm_cv)

    # ********** call function for extract cv from llm
    with get_openai_callback() as extract_cost:
        response = extract_cv_llm(chain, context, cv_language)

    # ********** call validator for check Cv extract in correct format and expectation value
    validate_response(response, OUTPUT_CV_EXTRACT)

    result = {
        "cv" : response,
        "token_in" : extract_cost.prompt_tokens,
        "token_out" : extract_cost.completion_tokens,
    }
    return result