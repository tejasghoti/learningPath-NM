# app/services/s3_service.py
import os
import json
import boto3
from botocore.exceptions import ClientError
from dotenv import load_dotenv
import uuid

load_dotenv()

S3_BUCKET_NAME = os.environ.get("S3_BUCKET_NAME")

# Initialize boto3 S3 client
# AWS credentials (AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, AWS_REGION) 
# are automatically loaded by boto3 from environment variables.
s3_client = boto3.client('s3')

def upload_roadmap_to_s3(student_profile: dict, roadmap_data: dict) -> str:
    """
    Uploads the generated AI roadmap to Amazon S3 as a JSON file.
    Returns the public/presigned URL to access the roadmap.
    """
    if not S3_BUCKET_NAME:
        return "S3_BUCKET_NAME not configured. Roadmap saved locally only."

    try:
        # Generate a unique filename for the roadmap
        roadmap_id = str(uuid.uuid4())[:8]
        file_key = f"roadmaps/{student_profile.get('caste', 'user')}_{roadmap_id}.json"

        # Combine student profile and roadmap into one JSON document
        document = {
            "student_profile": student_profile,
            "roadmap": roadmap_data
        }

        json_string = json.dumps(document, indent=2)

        # Upload the JSON string directly to S3
        s3_client.put_object(
            Bucket=S3_BUCKET_NAME,
            Key=file_key,
            Body=json_string,
            ContentType='application/json'
        )

        # Generate a presigned URL valid for 7 days
        url = s3_client.generate_presigned_url(
            'get_object',
            Params={'Bucket': S3_BUCKET_NAME, 'Key': file_key},
            ExpiresIn=604800  # 7 days
        )

        return url

    except ClientError as e:
        print(f"Error uploading to S3: {e}")
        return f"Failed to upload to S3: {e.response['Error']['Message']}"
    except Exception as e:
        print(f"Unexpected S3 error: {e}")
        return "Failed to upload to S3 due to unexpected error."
