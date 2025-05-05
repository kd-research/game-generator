import datetime
from google.cloud import storage
import requests

project_id
# Part 1: Generate a pre-signed URL for uploading
def generate_upload_signed_url(bucket_name, object_name):
    """Generates a pre-signed URL for uploading a file to GCS."""
    
    # Initialize the storage client
    storage_client = storage.Client(project=project_id)
    
    # Get the bucket
    bucket = storage_client.bucket(bucket_name)
    
    # Create a blob (object) reference
    blob = bucket.blob(object_name)
    
    # Generate a signed URL for uploading
    # Expires in 15 minutes
    url = blob.generate_signed_url(
        version="v4",
        method="PUT",
        expiration=datetime.timedelta(minutes=15),
        content_type="text/plain",  # Specify the content type of your file
    )
    
    print(f"Generated signed URL: {url}")
    print(f"URL expires in 15 minutes")
    
    return url