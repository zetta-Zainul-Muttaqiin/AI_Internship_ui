# ********** **** Import the library that needed *******************************
from langchain_core.pydantic_v1 import Field, BaseModel
from langchain_core.output_parsers import StrOutputParser
from langchain.prompts import PromptTemplate
from langchain_core.runnables import RunnableParallel

from operator import itemgetter
from langchain_community.callbacks import get_openai_callback


# *************** IMPORT MODEL ***************
from models.llms import LLMModels

# *************** IMPORT VALIDATOR ***************
from validator.flashcard_payload_checker import validate_cv

# *************** MAIN ***************
def cover_letter_creation(cv, job_info, keywords):
  """
  Generates a cover letter based on the provided CV, job information, and keywords.

    Args:
        cv (str): The CV content.
        job_info (str): The job information.
        keywords (str): The order of sections in the cover letter.

    Returns:
        dict: A dictionary containing the generated cover letter and token information.
    
  """
  
  # ********* Validate CV
  if not validate_cv(cv):
      raise KeyError('Invalid CV format')
  
  # ********* Initialize Parser and Templates
  cover_letter_parser = StrOutputParser()
  cover_letter_template = """
Student's data:
"cv": {cv}

Based on the data, create a cover letter for the following job information:
{job_info}

Ensure the cover letter follows this order:
{keywords}

NOTE: Ensure the response is written in the same language as the input "Student's data".
"""
  cover_letter_prompt = PromptTemplate(
            template=cover_letter_template,
            input_variables=["cv", "job_info", "keywords"],
            )
  
  # ********* Setup Runnable Chain
  runnable_cover_letter = RunnableParallel(
                            {
                                "cv": itemgetter('cv'),
                                "job_info": itemgetter('job_info'),
                                "keywords": itemgetter('keywords')
                            }
                        )
  cover_letter_chain = ( 
                runnable_cover_letter
                | cover_letter_prompt
                | LLMModels().llm_cv
                | cover_letter_parser
                )
  
  # ********* Generate Cover Letter
  with get_openai_callback() as cb:
        cover_letter = cover_letter_chain.invoke(
            {
                'cv':cv,
                'job_info':job_info,
                'keywords':keywords
            }
        )
        token_in = cb.prompt_tokens
        token_out = cb.completion_tokens
  
  # ********* Output
  cover_letter_result = {
        "cover_letter_ai": cover_letter, 
        'token_in': token_in, 
        'token_out': token_out
  }

  return cover_letter_result
