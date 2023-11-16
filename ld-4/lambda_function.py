import boto3
import hashlib

def lambda_handler(event, context):
    # Extract the username-datestring from the event input
    username_datestring = event['username_datestring']

    # Extract username and datestring from the input
    username, datestring = username_datestring.split('-')

    # Define bucket names
    approved_bucket = 'retroideal-approved-images'
    pending_bucket = 'retroideal-pending-images'

    # Create S3 clients
    s3 = boto3.client('s3')

    # Get the list of objects in the pending bucket with the given username-datestring as prefix
    pending_objects = s3.list_objects(Bucket=pending_bucket, Prefix=username_datestring)['Contents']

    # Get the list of objects in the approved bucket that match the username
    approved_objects = s3.list_objects(Bucket=approved_bucket, Prefix=username)['Contents']

    match_found = False

    # Iterate through pending images
    for pending_object in pending_objects:
        pending_key = pending_object['Key']

        # Retrieve the content of the pending image
        pending_object_data = s3.get_object(Bucket=pending_bucket, Key=pending_key)
        pending_content = pending_object_data['Body'].read()

        # Iterate through approved images with the same username
        for approved_object in approved_objects:
            approved_key = approved_object['Key']

            # Retrieve the content of the approved image
            approved_object_data = s3.get_object(Bucket=approved_bucket, Key=approved_key)
            approved_content = approved_object_data['Body'].read()

            # Compare image content using hash
            if hashlib.md5(pending_content).hexdigest() == hashlib.md5(approved_content).hexdigest():
                match_found = True
                break

        if match_found:
            break

    # Update DynamoDB entry for pending image based on match status
    if match_found:
        update_dynamodb_entry(username, datestring, "approved")
        return "Match"
    else:
        update_dynamodb_entry(username, datestring, "declined")
        return "No Match"

def update_dynamodb_entry(username, datestring, status):
    # Initialize DynamoDB client
    dynamodb = boto3.resource('dynamodb')
    
    # Define the table name
    table_name = 'retroideal-vehicle-images-records'

    # Get the DynamoDB table
    table = dynamodb.Table(table_name)

    # Define the item to update
    item_key = {
        'username': username,
        'datestring': datestring
    }

    # Update the item in DynamoDB
    response = table.update_item(
        Key=item_key,
        UpdateExpression="SET #s = :status",
        ExpressionAttributeNames={
            '#s': 'status'
        },
        ExpressionAttributeValues={
            ':status': status
        },
        ReturnValues="UPDATED_NEW"
    )

    # Print the updated item
    print("Updated item:", response)
