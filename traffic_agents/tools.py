from google.cloud import bigquery
from typing import List, Dict, Any
import logging
from .config import config

client = bigquery.Client(project=config.PROJECT_ID)
logger = logging.getLogger(__name__)


def execute_query(query: str) -> List[Dict[str, Any]]:
    """
    Execute a BigQuery SQL query and return results as a list of dictionaries.
    
    This simplified version streams results directly from the BigQuery API
    without using pandas, avoiding complex data cleaning.
    """
    try:
        logger.info(f"Executing query: {query[:150]}...")
        
        # 1. Execute the query
        query_job = client.query(query)
        
        # 2. Get the RowIterator from the results
        results = query_job.result()
        
        # 3. Convert the RowIterator directly to a list of dicts
        # The `bigquery.Row` object behaves like a dict, so
        # we can just cast it. The client library handles
        # BQ types (e.g., TIMESTAMP) to Python types (e.g., datetime.datetime).
        records = [dict(row) for row in results]
        
        return records
        
    except Exception as e:
        logger.error(f"Error executing query: {e}")
        raise


def get_toll_records_by_plate_number(plate_number: str = "NJL-694") -> List[Dict[str, Any]]:
    """
    Get toll records by plate number.
    
    Args:
        plate_number (str): The license plate number. Defaults to "NJL-694".
    
    Returns:
        List[Dict[str, Any]]: A list of toll records, where each record is a dictionary.
    """
    # Using f-string to build the query as shown in the provided example.
    # Note: For production use, parameterized queries are safer against SQL injection.
    query = f"""
    select * from `ajmalaziz-814-20250326021733.tolls.toll_records`
    where plate_number = '{plate_number}';
    """
    return execute_query(query)


def get_vehicle_count_by_type(start_timestamp: str, end_timestamp: str) -> List[Dict[str, Any]]:
    """
    Get the count of vehicles by type for a given time interval.
    
    Args:
        start_timestamp (str): The start of the time interval (e.g., '2023-01-01 00:00:00 UTC').
        end_timestamp (str): The end of the time interval (e.g., '2023-01-31 23:59:59 UTC').
    
    Returns:
        List[Dict[str, Any]]: A list of dictionaries, each with 'vehicle_type' and 'vehicle_count'.
    """
    query = f"""
    select
      vehicle_type,
      count(record_id) as vehicle_count
    from `ajmalaziz-814-20250326021733.tolls.toll_records`
    where timestamp between '{start_timestamp}' and '{end_timestamp}'
    group by vehicle_type;
    """
    return execute_query(query)
