# *************** IMPORTS ***************
from flask import request, jsonify, Flask
from cv_generator import (
    cv_editor, 
    cv_create
)
from cv_upload import (
    cv_extractor,
)
from flashcard import (
    generate_flashcards,
)

from cover_letter import cover_letter_creation
from setup import LOGGER

app = Flask(__name__)

@app.route("/", methods=[ 'GET'])
def home():
    """
    Testing endpont for check server is running in correct endpoint
    """
    return jsonify({"message": "API AI ENGINE RUNNING"}), 200

@app.route('/cover_letter_creation', methods=['POST'])
def cover_letter_ai():
    """
    Endpoint to create Cover Letter based on the provided CV and other details.

    Expects a JSON payload with the following keys:
    - cv: The segment of the CV to edit.
    - job_info: The data for the specified segment.
    - keywords: keywords of user input.

    Returns:
        Response: JSON response containing the AI processed result or error message.
    """
    try:
        data = request.get_json()
        cv = data.get('cv')
        keywords = data.get('keywords')
        job_info = data.get('job_info')

        if keywords == "":
            keywords = "Introduction, Skills, Experience, Conclusion"

        payload_check = (cv and keywords and job_info)
        if payload_check:
            cover_letter_response = cover_letter_creation(cv, job_info, keywords)
            return jsonify(cover_letter_response), 200
        
        return jsonify({'error': True, 'message': 'Missing the parameter request body'})

    except (KeyError, IndexError, TypeError, ValueError) as error:
        error_message = str(error)
        LOGGER.error("error occured: ", error_message)
        return jsonify({'error': True, 'message': error_message}), 500
    
    except Exception as un_error:
        error_message = str(un_error)
        LOGGER.error("An unexpected error occurred (resume_editor): ", error_message)
        return jsonify({'error': True, 'message': error_message}), 404  

@app.route('/cv_extractor', methods=["POST"])
def cv_extractor_api():
    """
    API endpoint to extract information from a CV URL.
    
    Expects a JSON payload with 'cv_url' key in string.
    
    Returns:
    - JSON : a response with extracted CV information if successful.
    """
    data = request.get_json()
    cv_url = data.get('cv_url')
    try:
        
        if cv_url:
            cv_extractor_result = cv_extractor(cv_url)
            return jsonify(cv_extractor_result)     
        
        return jsonify({'error': True, 'message': 'Missing the parameter request body'}), 402
    
    except (KeyError, IndexError, TypeError, ValueError) as error:
        error_message = str(error)
        LOGGER.error("error occured: ", error_message)
        return jsonify({'error': True, 'message': error_message}), 500
    
    except Exception as un_error:
        error_message = str(un_error)
        LOGGER.error("An unexpected error occurred (resume_editor): ", error_message)
        return jsonify({'error': True, 'message': error_message}), 404  

@app.route('/cv_creation', methods=["POST"])
def cv_creation_api():
    """
    Endpoint to create CV based on the provided CV segment and other details.

    Expects a JSON payload with the following keys:
    - cv_segment: The segment of the CV to edit.
    - cv_data_segment: The data for the specified segment.
    - keywords: The list of keywords.
    - language: The language of the CV.

    Returns:
        Response: JSON response containing the AI processed result or error message.
    """
    try:
        data = request.get_json()
        cv_segment = data.get('cv_segment')
        cv_data_segment = data.get(cv_segment)
        cv_description = None
        keywords = data.get('keywords')

        # ****** If skills need to get cv_description
        if cv_segment.lower() == 'skills':
            cv_description = data.get('cv_description')        
        if (cv_data_segment ):
            cv_response = cv_create(
                cv_segment,
                cv_data_segment, 
                keywords, 
                cv_description,
            )
            return jsonify(cv_response), 200
        
        else:
            return jsonify({'error': True, 'message': 'Missing the parameter request body'}), 402

    
    except (KeyError, IndexError, TypeError, ValueError) as error:
        error_message = str(error)
        LOGGER.error("error occured: ", error_message)
        return jsonify({'error': True, 'message': error_message}), 401
    
    except Exception as un_error:
        error_message = str(un_error)
        LOGGER.error("An unexpected error occurred (resume_editor): ", error_message)
        return jsonify({'error': True, 'message': error_message}), 404    
   
@app.route('/resume_editor', methods=['POST'])
def resume_editor():
    """
    Endpoint to edit the resume based on the provided CV segment and other details.

    Expects a JSON payload with the following keys:
    - cv_segment: The segment of the CV to edit.
    - cv_data_segment: The data for the specified segment.
    - keywords: The list of keywords.
    - job_info: The job information.
    - language: The language of the CV.

    Returns:
        Response: JSON response containing the AI processed result or error message.
    """
    try:
        # ****** get payload from request
        data = request.get_json()
        cv_segment = data.get('cv_segment')
        cv_data_segment = data.get(cv_segment)
        job_info = data.get('job_info')    
        keywords = data.get('keywords')
        cv_description = None

        # ****** If skills need to get cv_description
        if cv_segment == "skills":
            cv_description = data.get('cv_description')
        
        # ****** Check for missing parameters in request body
        check_job_info = (job_info and isinstance(job_info, str))
        check_cv_data = (cv_segment and (cv_data_segment or keywords))

        cv_data = check_cv_data and check_job_info
        if (cv_data):
            cv_response = cv_editor(
                cv_segment,
                cv_data_segment,
                keywords,
                job_info,
                cv_description
            )
            
            return jsonify(cv_response), 200
        
        return jsonify({'error': True, 'message': 'Missing the parameter request body'}), 402
    
    except (KeyError, IndexError, TypeError, ValueError) as error:
        error_message = str(error)
        LOGGER.error(f"error occured: {error}")
        return jsonify({'error': True, 'message': error_message}), 500
    
    except Exception as un_error:
        error_message = str(un_error)
        LOGGER.error(f"An unexpected error occurred (resume_editor): {error_message}")
        return jsonify({'error': True, 'Type': type(un_error).__name__, 'Message': error_message}), 501

@app.route('/create_flashcard', methods=['POST'])
def create_flashcard():
    """
    Endpoint to edit the resume based on the provided CV segment and other details.

    Expects a JSON payload with the following keys:
    - cv: The The data of the CV.
    - comapny: The company information.
    - job_info: The job information.

    Returns:
        Response: JSON response containing the AI processed result or error message.
    """
    try:
        # ****** get payload data from request
        data = request.get_json()
        if not data:
            return jsonify({'error': True, 'message': 'Missing request body'}), 400

        # ****** get field data from payload
        cv = data.get('cv')
        company = data.get('company')
        job_info = data.get('job_info')

        # ****** check data
        if cv and company and job_info:
            result = generate_flashcards(cv, company, job_info)
            return jsonify(result)
        else:
            return jsonify({'error': True, 'message': 'Missing required fields in request body'}), 400
        
    except (KeyError, IndexError, TypeError, ValueError) as error:
        error_message = str(error)
        LOGGER.error("error occured: ", error_message)
        return jsonify({'error': True, 'message': error_message}), 400
    
    except Exception as un_error:
        error_message = str(un_error)
        LOGGER.error("An unexpected error occurred (resume_editor): ", error_message)
        return jsonify({'error': True, 'message': error_message}), 404

if __name__ == "__main__":
    app.run(host='192.168.1.46', port=2222, debug=True)
