# *************** Import Helper ***************
from helpers.astradb_connect_helper import get_astradb_collection, get_astradb_description
from geopy.geocoders import Nominatim, options, ArcGIS
from haversine import haversine
import pandas as pd
import ast

geoLocator = Nominatim(user_agent="oneDetail")

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
    print("RESULT:", get_one_details)
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
            "job_url": document['job_url'],
            "job_role": document['job_role'],
            "location": document['location'],
            "job_category": document['job_category'],
            "education_level": document['standardized_level'],
            "job_contract": document['job_contract'],
            "description": document['summary']
            }
        job_list.append(data_field) # ****** Add the formatted job data to the list ******
    
    if len(job_list) < 5:

        for document_v2 in table_v2:
            # ****** Create a dictionary for each job with the required fields ******
            data_field = {
                "job_url": document_v2['job_url'],
                "similarity": document_v2['$similarity'],
                "job_role": document_v2['job_role'],
                "location": document_v2['location'],
                "job_category": document_v2['job_category'],
                "education_level": document_v2['standardized_level'],
                "job_contract": document_v2['job_contract'],
                "description": document_v2['summary'],
                "location_detail": document_v2['location_detail']
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
    print("QUE:",query)
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

def calculate_distance(location_name, df):
    
    # Function to get coordinates from a location name
    def get_coordinates(location_name):
        location = geoLocator.geocode(location_name, timeout=120)
        return (location.latitude, location.longitude) if location else (None, None)

    # Function to extract coordinates from location_detail column
    def extract_coordinates(loc_detail):
        print("detail: ", loc_detail)
        return ast.literal_eval(loc_detail)[0]  # Convert string to list and get the first item

    # Function to calculate distance using Haversine formula
    def haversine_distance(coord1, coord2):
        return haversine(coord1, coord2)

    def get_category(distance):
        if distance == 0:
            return 'Exact Location'
        elif distance < 10:
            return 'Within a radius of 10 km'
        elif distance < 25:
            return 'Within a radius of 25 km'
        elif distance < 50:
            return 'Within a radius of 50 km'
        elif distance < 75:
            return 'Within a radius of 75 km'
        elif distance < 100:
            return 'Within a radius of 100 km'
        elif distance < 250:
            return 'Within a radius of 250 km'
        elif distance < 500:
            return 'Within a radius of 500 km'
        elif distance < 750:
            return 'Within a radius of 750 km'
        elif distance < 1000:
            return 'Within a radius of 1000 km'
        else:
            return 'Radius more than 1000 km'

    # Get input coordinates
    input_coords = get_coordinates(location_name)
    
    # df['location_detail_coords'] = df['location_detail'].apply(extract_coordinates)
    df['distance'] = df['location_detail'].apply(lambda index: haversine_distance(input_coords, index[0]))
    df['distance_category'] = df['distance'].apply(get_category)

    # Sort by distance
    sorted_df = df.sort_values(by='distance')
    sorted_df.reset_index(drop=True, inplace=True)

    return sorted_df

if __name__ == "__main__":

    run_vector_search("marketing")