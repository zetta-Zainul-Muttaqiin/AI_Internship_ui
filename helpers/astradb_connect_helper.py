# ************ IMPORT ************
from astrapy import DataAPIClient
from astrapy.db import AstraDB

from setup import(
    ASTRADB_API_ENDPOINT,
    ASTRADB_NAMESPACE_NAME,
    ASTRADB_COLLECTION_NAME,
    ASTRADB_TOKEN_KEY
)

# ************ Function to get AstraDB Collection ************
def get_astradb_collection():
    """
    Initialize the DataAPIClient and get the AstraDB collection.

    Returns:
        astrapy_collection: The AstraDB collection object.
    """
    try:
        # ****** Initialize the client and get a "Database" object ******
        client = DataAPIClient(ASTRADB_TOKEN_KEY)
        database = client.get_database(ASTRADB_API_ENDPOINT)

        astrapy_collection_v2 = database.get_collection(
            "job_info_vectorize", 
            namespace=ASTRADB_NAMESPACE_NAME
        )
        astrapy = AstraDB(
            token=ASTRADB_TOKEN_KEY,
            api_endpoint="https://c8c9b326-6509-4516-9f07-54f186374421-us-east-2.apps.astra.datastax.com",
            namespace=ASTRADB_NAMESPACE_NAME)
        astrapy_collection = astrapy.collection(collection_name="job_info_vectorize")
        return astrapy_collection, astrapy_collection_v2
    except Exception as e:
        # ****** Handle exceptions ******
        raise ConnectionError(f"Failed to connect to AstraDB: {e}")