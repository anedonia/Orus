import os
import boto3
from typing import List, Tuple
from datetime import datetime, timezone
from pathlib import Path
from dotenv import load_dotenv
from botocore.client import Config
from botocore.exceptions import ClientError 

if not os.path.exists('.env'):
	print("Please create the env file")
	exit(0)

load_dotenv()
#conf
MINIO_URL = "http://localhost:9000"
ACCESS_KEY = os.getenv('AWS_ACCESS_KEY_ID')
SECRET_KEY = os.getenv('AWS_SECRET_ACCESS_KEY')
LOCAL_DIR = os.getenv('LOCAL_DIRECTORY')

#create client
s3_client = boto3.client(
    's3',
    endpoint_url=MINIO_URL,
    aws_access_key_id=ACCESS_KEY,
    aws_secret_access_key=SECRET_KEY,
    config=Config(signature_version='s3v4'),
    region_name='us-east-1'
)

bucket_name = os.getenv('S3_BUCKET_NAME')

def upload_file(file_path):
	try:
		s3_client.upload_file(file_path, bucket_name, file_path)
		print(f"{file_path} uploaded to {bucket_name}")
	except Exception as e:
		print(f"failed to upload file: {e}")

def delete_file(file_path):
	try:
		response = s3_client.delete_object(Bucket=bucket_name, Key=file_path)
		if response.get('ResponseMetadata', {}).get('HTTPStatusCode') == 204:
			print(f"{file_path} deleted from {bucket_name}")
		else:
			print(f" Failed to delete {file_path} from {bucket_name}")
	except Exception as e:
		print(f"failed to delete file: {e}")

def add_to_list(file_names, dirpath, list_file):
	for file in file_names:
		file_path = dirpath + '/' + file
		file_stats = os.stat(file_path)
		mod_time = datetime.fromtimestamp(file_stats.st_mtime, tz=timezone.utc)
		list_file.append([file_path, mod_time])

def file_parsing () :
	path = LOCAL_DIR
	list_file : List [Tuple[str, datetime]] = []

	for dirpath, dirnames, filenames in os.walk(path) :
		add_to_list(filenames, dirpath, list_file)
	return list_file

def get_bucket_files():
	bucket = {}
	try:
		response = s3_client.list_objects_v2(Bucket = bucket_name)
		if 'Contents' in response:
			for obj in response['Contents']:
				#constant lookup time avec un dict
				bucket["/" + obj['Key']] = obj['LastModified'].astimezone(timezone.utc)
			return bucket
		else:
			print("Empty bucket")
			return bucket
	except Exception as e:
		print("failed to get bucket files")

def bucket_exists():
	try: 
		s3_client.head_bucket(Bucket=bucket_name)
		return True
	except ClientError as e:
		error_code = int(e.response['Error']['Code'])
		if error_code == 404:
			init_bucket()
		else:
			print(f"An error occured{e}")
	return False

def init_bucket():
	try:
		s3_client.create_bucket(Bucket=bucket_name)
		print(f"Bucket '{bucket_name}' created successfully.")
	except Exception as e:
		print(f"Error creating bucket: {e}")
	file_2upload = file_parsing()
	for file in file_2upload:
		upload_file(file[0])

def syncing_files(bucket, local):
	for key, mod_time in local:
		if key in bucket and bucket[key] < mod_time:
			upload_file(key)
		elif key not in bucket:
			upload_file(key)

	local_files_path : List[str] = [file[0] for file in local]
	for key in bucket:
		if key not in local_files_path:
			delete_file(key)
	print("Syncing done :)")

def main():

	if not bucket_exists():
		return
	local_files = file_parsing()
	bucket_files = get_bucket_files()
	syncing_files(bucket_files, local_files)


if __name__ == "__main__":
    main()
