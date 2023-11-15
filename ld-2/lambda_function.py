import boto3
import hashlib

def lambda_handler(event, context):
    # Get the bucket names from the event
    approved_bucket = 'approved-images'
    pending_bucket = 'pending-images'

    # Create S3 clients
    s3 = boto3.client('s3')

    # Get the list of objects in each bucket
    approved_objects = s3.list_objects(Bucket=approved_bucket)['Contents']
    pending_objects = s3.list_objects(Bucket=pending_bucket)['Contents']

    # Compare each object in the pending bucket with the approved bucket
    for pending_object in pending_objects:
        pending_key = pending_object['Key']

        # Retrieve the content of the pending image
        pending_object_data = s3.get_object(Bucket=pending_bucket, Key=pending_key)
        pending_content = pending_object_data['Body'].read()

        # Iterate through approved images and compare content
        for approved_object in approved_objects:
            approved_key = approved_object['Key']

            # Retrieve the content of the approved image
            approved_object_data = s3.get_object(Bucket=approved_bucket, Key=approved_key)
            approved_content = approved_object_data['Body'].read()

            # Compare image content using hash (you may need a more sophisticated comparison based on your use case)
            if hashlib.md5(pending_content).hexdigest() == hashlib.md5(approved_content).hexdigest():
                return "Match"

    return "Different"

# If no match is found after iterating through all images
# outside the for loop, return "Different"

