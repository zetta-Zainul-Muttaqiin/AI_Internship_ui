# *************** IMPORTS ***************
from typing import Any, Dict, List
import re

from setup import PAYLOAD_TYPE, REQUIRED_FIELDS

def is_url(
        text
    ):
    url_pattern = re.compile(
        r'^(https?|ftp)://'
        r'(([A-Z0-9][A-Z0-9_-]*(?:\.[A-Z0-9][A-Z0-9_-]*)+)\.?(:\d+)?|localhost|(\d{1,3}\.){3}\d{1,3})'
        r'(:\d+)?'
        r'(/\S*)?$',
        re.IGNORECASE
    )
    # url_match = re.match(url_pattern, text) is not None

    # if not url_match:
    #     raise ValueError(f"Expected an URL input, got {text}")

def validate_response(response: Dict[str, Any], expected_format: Dict[str, Any]) -> bool:
    """
    Validates the given response dictionary against the expected format.

    Args:
        response (Dict[str, Any]): The response to validate.
        expected_format (Dict[str, Any]): The expected format for the response.

    Returns:
        bool: True if the response matches the expected format, False otherwise.
    """
    # ********** Iterate through each key-value pair in the expected format
    for key, expected_value in expected_format.items():
        # ********** Check if the key exists in the response
        if key not in response:
            raise KeyError(f"Missing key: {key}")

        # ********** Check the type of the value in the response
        if isinstance(expected_value, dict):
            # ********** If the expected value is a dict, ensure the response value is also a dict
            if not isinstance(response[key], dict):
                raise TypeError(f"Incorrect format for key '{key}'. Expected dict, got {type(response[key])}")
        elif isinstance(expected_value, list):
            # ********** If the expected value is a list, ensure the response value is also a list
            if not isinstance(response[key], list):
                raise TypeError(f"Incorrect format for key '{key}'. Expected list, got {type(response[key])}")

            # ********** If both the expected list and response list are non-empty
            if expected_value and response[key]:
                if isinstance(expected_value[0], dict):
                    # ********** If the first item in the expected list is a dict, ensure the first item in the response list is also a dict
                    if not isinstance(response[key][0], dict):
                        raise TypeError(f"Incorrect format for items in list under key '{key}'. Expected dict, got {type(response[key][0])}")

        # ********** Check each item in the expected value
        for item in expected_value:
            # ********** Check if the item exists in the response key if the item is not a dict
            if item not in response[key] and not isinstance(item, dict):
                raise KeyError(f"Missing item '{item}' in key '{key}'")

            # ********** If the item is a dict, iterate through each subkey-subvalue pair
            elif isinstance(item, dict):
                for response_dict in response[key]:
                    for subkey, _ in item.items():
                        # ********** Check if the subkey exists in the response dict
                        if subkey not in response_dict:
                            raise KeyError(f"Missing key '{subkey}' in item '{item}' under key '{key}'")

    # ********** Return True if all checks pass
    return True

def is_dict(value: Any) -> bool:
    """
    Check if the value is a dictionary.
    """
    return isinstance(value, dict)

def is_list(value: Any) -> bool:
    """
    Check if the value is a list.
    """
    return isinstance(value, list)

def validate_dict(expected: Dict, actual: Dict, path: str) -> None:
    """
    Validate if actual dictionary matches the expected dictionary structure.
    """
    for key, value in expected.items():
        if key not in actual:
            raise KeyError(f"Missing key at {path}: {key}")
        validate_structure(value, actual[key], f"{path}.{key}")

def validate_list(expected: List, actual: List, path: str) -> None:
    """
    Validate if actual list matches the expected list structure.
    """
    for index, item in enumerate(expected):
        if index >= len(actual):
            raise IndexError(f"Missing item at {path}[{index}]")
        validate_structure(item, actual[index], f"{path}[{index}]")

def validate_structure(expected: Any, actual: Any, path: str = "root") -> None:
    """
    Validate if actual matches the expected structure.
    """
    if is_dict(expected):
        if not is_dict(actual):
            raise TypeError(f"Mismatch at {path}: expected dict, got {type(actual).__name__}")
        validate_dict(expected, actual, path)

    elif is_list(expected):
        if not is_list(actual):
            raise TypeError(f"Mismatch at {path}: expected list, got {type(actual).__name__}")
        validate_list(expected, actual, path)

    elif type(expected) != type(actual):
        raise ValueError(f"Type mismatch at {path}: expected {type(expected).__name__}, got {type(actual).__name__}")


def check_missing_keys(
        cv_data_segment: Dict[str, Any],
        section: str,
        ) -> List[str]:
    """
    Checks for missing subfields in the CV data segment.
    Args:
        cv_data_segment (dict): The segment of the CV data to check.
        section         (str) : current cv_segment that need to generate the description  
    Returns:
        List[str]: List of missing subfields.
    """
     # ****** Initialize list to hold missing subfields 
    missing_keys = []

    # ****** START: Check each required subfield in the CV data segment
    for subfield in REQUIRED_FIELDS[section]:
        if subfield not in cv_data_segment.keys():
            # ****** If a subfield is missing, add it to the missing_keys list
            missing_keys.append(subfield)
    # ****** END: Check each required subfield in the CV data segment

    if missing_keys:
        raise KeyError(f"Missing key from {section} subfields: Missing key {missing_keys} ")

def check_missing_values(
        cv_data_segment: Dict[str, Any],
        section: str,
        ) -> List[str]:
    """
    Checks for missing or empty required subfields in the CV data segment.
    Args:
        cv_data_segment (dict): The segment of the CV data to check.
        section         (str) : current cv_segment that need to generate the description
    Returns:
        List[str]: List of missing or empty required subfields.
    """
    
    # ****** Initialize list to hold missing or empty subfields
    missing_values = []
    # ****** START: Iterate over each required section and its subfields
    for subfield in REQUIRED_FIELDS[section]:
        if subfield in cv_data_segment:     
        # ****** Section is present in the CV data segment
            if (not cv_data_segment[subfield] or   # subField is empty
                cv_data_segment[subfield] in [None, ""]  # subField is None or an empty string
            ):
                # ****** Add missing or empty subfield to the list
                missing_values.append(f"{section}.{subfield} is Empty/None")
    # ****** END: Iterate over each required section and its fields
    print("DONE!") 
    if missing_values:
        raise ValueError(f"Missing value from {section}: expected {REQUIRED_FIELDS[section]} but got: \n{missing_values}")

def check_incorrect_datatypes(
        cv_data_segment: Dict[str, Any],
        section: str,
        ) -> List[str]:
    """
    Checks for incorrect datatypes in the CV data segment.
    Args:
        cv_data_segment (dict): The segment of the CV data to check.
        section (str): current cv_segment that need to generate the description
    Returns:
        List[str]: List of subfields with incorrect datatypes.
    """
    # ****** Initialize list to hold subfields with incorrect datatypes
    incorrect_datatypes = []
    
    if section != "skills":
        # ****** START: Iterate over each section and its subfields in the required payload subfield
        for subfields, subfield_type in PAYLOAD_TYPE[section].items():
            # ****** Section is present in the CV data segment
            if subfields in cv_data_segment:
                # ****** subField is present in the section
                if not isinstance(cv_data_segment[subfields], subfield_type):
                    # ****** subField datatype is incorrect
                    incorrect_datatypes.append(f"{section}.{subfields} with type {type(cv_data_segment[subfields])} expect {subfield_type}")
    
    else: 
        if not isinstance(cv_data_segment, list):
            incorrect_datatypes.append(f"{section} with type {type(cv_data_segment[subfields])} expect a List")
    # ****** END: Iterate over each section and its subfields in the required payload subfield
    
    if incorrect_datatypes:
        raise TypeError(f"False Data Type from {section}: got {incorrect_datatypes}")

def validate_description_response(response: Dict[str, Any]) -> bool:
    """
    Validates the response to ensure it contains 'recommended', 'simplified', and 'extended' keys,
    
    Args:
        response (dict): The response to validate.
    
    Returns:
        List[str]: List of missing keys
    """
    # ****** Define the required keys ******
    required_keys = ['recommended', 'simplified', 'extended']

    # ****** START: Check for the presence of required keys ******
     # ****** Check for missing keys ******
    missing_keys = []
    for key in required_keys:
        if key not in response:
            missing_keys.append(key)

    if missing_keys:
        raise KeyError(f"Missing keys in response: {missing_keys}, expected {required_keys}")
