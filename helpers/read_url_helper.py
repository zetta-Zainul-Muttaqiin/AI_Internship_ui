# ************* IMPORT **************
import requests

def request_url(pdf_url):
    """
    Function to read an URL pdf to bytes and saved in temporary file

    Args:
        temp_pdf (string): a temporary pdf after request an url pdf
    Returns:
        string: a string of from temporary pdf string path
    """
    try:
        # ***** read url link to bytes
        with open(pdf_url, 'rb') as file:
            pdf_bytes = file.read()
        return pdf_bytes

    except Exception as request_error:
        print("an Error occured when try to read a pdf url: {cv_path} ", str(request_error))