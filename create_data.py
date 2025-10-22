import os
import random
from datetime import datetime, timedelta, timezone
from google.cloud import bigquery
from faker import Faker
from google.api_core.exceptions import NotFound, Conflict
import uuid

# --- Configuration ---
project_id = "ajmalaziz-814-20250326021733"
region = "us-central1"
dataset_id = "plate_reader"

# Table name for the number plate reader system
TABLES = {
    'toll_records': 'toll_records',
}

client = bigquery.Client(project=project_id)

# --- Table Schema ---

# Toll records table schema - Core data for license plate reads
toll_records_schema = [
    bigquery.SchemaField("record_id", "STRING", mode="REQUIRED"),
    bigquery.SchemaField("plate_number", "STRING", mode="REQUIRED"),
    bigquery.SchemaField("toll_point_id", "STRING", mode="REQUIRED"),
    bigquery.SchemaField("timestamp", "TIMESTAMP", mode="REQUIRED"),
    bigquery.SchemaField("vehicle_type", "STRING", mode="NULLABLE"),
    bigquery.SchemaField("image_url", "STRING", mode="NULLABLE"),
]

# --- Data Generation Setup ---
fake = Faker()

# Define realistic toll points
toll_points = [
    "TP-001", "TP-002", "TP-003", "TP-004", "TP-005",
    "TP-006", "TP-007", "TP-008", "TP-009", "TP-010"
]

# Vehicle types
vehicle_types = ["Car", "Truck", "Bus", "Motorcycle", "Van"]

# --- Helper Functions ---

def generate_plate_number():
    """Generate a random license plate number."""
    return f"{''.join(random.choices('ABCDEFGHIJKLMNOPQRSTUVWXYZ', k=3))}-{''.join(random.choices('0123456789', k=3))}"

def generate_uuid():
    """Generate a UUID for unique identifiers."""
    return str(uuid.uuid4())

def generate_timestamp(start_date, end_date):
    """Generate a random UTC timestamp within a given date range."""
    time_between_dates = end_date - start_date
    seconds_between_dates = time_between_dates.total_seconds()
    random_seconds = random.uniform(0, seconds_between_dates)
    return (start_date + timedelta(seconds=random_seconds)).replace(tzinfo=timezone.utc)

def generate_date_range(days_back=30):
    """Generate start and end dates for data generation."""
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days_back)
    return start_date, end_date

# --- Data Generation Functions ---

def generate_toll_records_data(num_records):
    """Generate synthetic toll record data."""
    data = []
    start_date, end_date = generate_date_range(30)
    
    for _ in range(num_records):
        record_id = generate_uuid()
        plate_number = generate_plate_number()
        toll_point_id = random.choice(toll_points)
        timestamp = generate_timestamp(start_date, end_date)
        vehicle_type = random.choice(vehicle_types)
        image_url = f"http://example.com/images/{record_id}.jpg"
        
        data.append({
            "record_id": record_id,
            "plate_number": plate_number,
            "toll_point_id": toll_point_id,
            "timestamp": timestamp,
            "vehicle_type": vehicle_type,
            "image_url": image_url,
        })
    
    return data

# --- Table Management Functions ---

def create_dataset_if_not_exists(client, dataset_id, project_id, region):
    """Create a BigQuery dataset if it does not already exist."""
    dataset_ref = bigquery.DatasetReference(project_id, dataset_id)
    dataset = bigquery.Dataset(dataset_ref)
    dataset.location = region
    try:
        client.get_dataset(dataset)
        print(f"Dataset '{dataset_id}' already exists.")
    except NotFound:
        print(f"Creating dataset '{dataset_id}' in region '{region}'...")
        try:
            client.create_dataset(dataset)
            print(f"Dataset '{dataset_id}' created successfully.")
        except Conflict:
            print(f"Dataset '{dataset_id}' was created by another process concurrently.")
        except Exception as create_e:
            print(f"Error creating dataset '{dataset_id}': {create_e}")
            raise

def create_table_if_not_exists(client, dataset_id, table_id, schema):
    """Create a BigQuery table if it does not already exist."""
    table_ref = bigquery.TableReference(bigquery.DatasetReference(project_id, dataset_id), table_id)
    table = bigquery.Table(table_ref, schema=schema)
    try:
        client.get_table(table)
        print(f"Table '{table_id}' already exists.")
    except NotFound:
        print(f"Table '{table_id}' not found. Attempting to create it...")
        try:
            client.create_table(table)
            print(f"Table '{table_id}' created successfully.")
        except Conflict:
            print(f"Table '{table_id}' was created by another process concurrently.")
        except Exception as create_e:
            print(f"Error creating table '{table_id}': {create_e}")
            raise

def insert_data_into_table(client, dataset_id, table_id, data):
    """Insert rows into a BigQuery table."""
    table_ref = client.dataset(dataset_id).table(table_id)
    
    try:
        table = client.get_table(table_ref)
    except NotFound:
        print(f"Error: Table '{table_id}' not found during data insertion.")
        return

    errors = client.insert_rows(table, data)
    if errors:
        print(f"Encountered errors while inserting rows into '{table_id}': {errors}")
    else:
        print(f"Successfully inserted {len(data)} rows into '{table_id}'.")

# --- Main Execution ---
if __name__ == "__main__":
    try:
        # Create dataset if it doesn't exist
        create_dataset_if_not_exists(client, dataset_id, project_id, region)

        # Define table schema
        table_schemas = {
            TABLES['toll_records']: toll_records_schema,
        }

        # Create all tables
        for table_name, schema in table_schemas.items():
            create_table_if_not_exists(client, dataset_id, table_name, schema)

        # Generate and insert data
        print("\n=== Generating number plate reader data ===")
        
        # 1. Generate toll records
        print("Generating toll records data...")
        toll_records_data = generate_toll_records_data(random.randint(500, 1000))
        insert_data_into_table(client, dataset_id, TABLES['toll_records'], toll_records_data)

        print("\n=== Number plate reader data generation completed successfully! ===")
        print(f"Table created in dataset '{dataset_id}':")
        for table_name in table_schemas.keys():
            print(f"  - {table_name}")

        print(f"\nGenerated data summary:")
        print(f"  - Toll Records: {len(toll_records_data)} records")

    except Exception as e:
        print(f"An unhandled error occurred during script execution: {e}")
        print("Please verify your Google Cloud permissions and project setup.")