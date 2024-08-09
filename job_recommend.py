# *************** Import Helper ***************
from helpers.astradb_connect_helper import get_astradb_collection, get_astradb_description

def search_simillar_job(query, search_filter):
    """
    Search for similar job postings in the AstraDB collection using vectorization.
    
    Args:
        query (str): The query string used to vectorize and search for similar jobs.
        
    Returns:
        list: A list of job documents with similarity scores.
    """
    # ****** Perform a search query in the AstraDB collection ******
    try:
        astrapy_collection, astrapy_collection_v2 = get_astradb_collection()

    except ConnectionError as e:
        # Handle the connection error
        print(e)
    v_search = astrapy_collection.paginated_find(
        filter=search_filter,
        options={"limit": 25}
        )
    v2_search = astrapy_collection_v2.find(
        sort={"$vectorize": query},
        limit=25,
        projection={"$vectorize": True},
        include_similarity=True,
    )
    return v_search, v2_search

def get_selected_description(job_url):
    """
    Search for similar job postings in the AstraDB collection using vectorization.
    
    Args:
        job_url (str): an unique url from the selected data from table
        
    Returns:
        dict: .
    """
    # ****** Perform a search query in the AstraDB collection ******
    try:
        astrapy_description = get_astradb_description()

    except ConnectionError as e:
        # Handle the connection error
        print(e)
        raise ConnectionError(str(e))

    get_one_details = astrapy_description.find_one(
        filter={
            'job_url': job_url
        }
    )

    return get_one_details['data']['document']

def set_sending_data(table, table_v2):
    """
    Prepare and format the job data to be sent as a response.
    
    Args:
        table (list): A list of job documents retrieved from the database.
        
    Returns:
        list: A list of formatted job data dictionaries.
    """
    job_list = [] # ****** Initialize an empty list to hold job data ******
    job_list_v2 = [] # ****** Initialize an empty list to hold job data ******

    for document in table:
        # ****** Create a dictionary for each job with the required fields ******
        data_field = {
            "job_id": document['_id'],
            "job_role": document['job_role'],
            "location": document['location'],
            "job_category": document['categories'],
            "education_level": document['standardized_level'],
            "job_contract": document['job_contract'],
            "description": document['summary'],
            }
        job_list.append(data_field) # ****** Add the formatted job data to the list ******
    
    if len(job_list) < 5:

        for document_v2 in table_v2:
            # ****** Create a dictionary for each job with the required fields ******
            data_field = {
                "job_id": document_v2['_id'],
                "similarity": document_v2['$similarity'],
                "job_role": document_v2['job_role'],
                "location": document_v2['location'],
                "job_category": document_v2['categories'],
                "education_level": document_v2['standardized_level'],
                "job_contract": document_v2['job_contract'],
                "description": document_v2['summary'],
                }
            job_list_v2.append(data_field) # ****** Add the formatted job data to the list ******

    return job_list, job_list_v2

def create_filter(query):
    search_filter = {
        "$and": [],
        "$or": []
        }
    if query['location']:
        filter_loc = {'location': query['location']}
        search_filter['$and'].append(filter_loc)

    if query['category']:
        filter_cat =  {'job_category': {
            "$in": [query['category']]
            }
        }
        search_filter['$and'].append(filter_cat)

    if query['education']:
        filter_edu = {'standardized_level': query['education']}
        search_filter['$and'].append(filter_edu)

    if query['duration']:
        filter_dur = {'job_contract': "Internship "+query['duration']}
        search_filter['$and'].append(filter_dur)
    
    if query['keywords']:
        filter_key =  {'job_role': {
            "$in": [query['keywords']]
            }
        }
        search_filter['$or'].append(filter_key)

    if not query['keywords'] and not query['location'] and not query['category'] and not query['education'] and not query['duration']: 
        search_filter = None

    print("FILTER: ", search_filter)
    joined_query = f"{query['keywords']} {query['location']} {query['category']} {query['education']} {query['duration']}"
    
    return joined_query, search_filter

def run_vector_search(query):
    """
    Execute a vector search for similar job postings and format the results.
    
    Args:
        query (str): The query string used to search for similar jobs.
        
    Returns:
        dict: A dictionary containing the list of recommended jobs.
    """

    joined_query, search_filter = create_filter(query)

    # ****** Search for similar job postings ******
    search_list, search_list_v2 = search_simillar_job(joined_query, search_filter)

    # ****** Format the search results ******
    list_filter, list_recommend = set_sending_data(search_list, search_list_v2)
    
    # ****** Create the final result dictionary ******
    result = {
        "data": list_filter,
        "data_recommend": list_recommend
    }

    return result

if __name__ == "__main__":

    run_vector_search("marketing")