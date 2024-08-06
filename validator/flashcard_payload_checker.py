from typing import List, Dict

from setup import EXPECTED_KEYS

def validate_cv(
        cv: Dict
        ) -> str:
    """
    Validate the format of the provided CV.

    This function checks if the provided CV contains all the required fields: 
    'summary', 'work_experience', 'education', 'project', and 'skills'.

    Args:
        cv (dict): A dictionary representing the CV.

    Returns:
        bool: True if the CV contains all required fields, False otherwise.
    """
    required_fields = ["summary", "work_experience", "education", "project", "skills"]
    if not all(field in cv for field in required_fields):
        return False
    return True

def validate_company(
        company: Dict
        ) -> str:
    """
    Validate the format of the provided company information.

    This function checks if the provided company information contains all the required fields:
    'company_name' and 'company_detail'.

    Args:
        company (dict): A dictionary representing the company information.

    Returns:
        bool: True if the company information contains all required fields, False otherwise.
    """
    required_fields = ["company_name", "company_detail"]
    if not all(field in company for field in required_fields):
        return False
    return True

def validate_job_detail(
        job_detail: Dict
        ) -> str:
    """
    Validate the format of the provided job detail.

    This function checks if the provided job detail contains all the required fields:
    'job_position' and 'job_description'.

    Args:
        job_detail (dict): A dictionary representing the job detail.

    Returns:
        bool: True if the job detail contains all required fields, False otherwise.
    """
    required_fields = ["job_position", "job_description"]
    if not all(field in job_detail for field in required_fields):
        return False
    return True

def validate_qna_list(
        qna_list: List[Dict[str, str]]
        ) -> bool:
    """
    Validate that each dictionary in the list contains the keys 'question' and 'answer'
    and that their associated values are non-empty strings.
    
    Args:
        qna_list (List[Dict[str, str]]): List of dictionaries containing questions and answers.
    
    Returns:
        bool: True if all dictionaries are valid, False otherwise.
    """
    # ****** Iterate through each item in the list ******
    for index, item in enumerate(qna_list):
        # ****** Check if the item contains the expected keys ******
        if not EXPECTED_KEYS.issubset(item.keys()):
            print(f"Item at index {index} is missing required keys.")
            raise KeyError(f"Item at index {index} is missing required keys.")
        # ****** Check if the values are non-empty strings ******
        for key in EXPECTED_KEYS:
            if not isinstance(item[key], str) or not item[key].strip():
                print(f"Item at index {index} has an invalid or empty '{key}'.")
                raise TypeError (f"Item at index {index} has an invalid or empty '{key}'.")
    return True