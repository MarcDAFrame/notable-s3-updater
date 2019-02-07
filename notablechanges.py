import boto3
import os
import time
import datetime
import pytz
import json 

DIRECTORY_TO_WATCH = "/Users/marcframe/.notable/"

secrets = json.loads(open("secrets").read())
aws_access_key_id     = secrets['aws_key']
aws_secret_access_key = secrets['aws_secret']


TIMEZONE = pytz.timezone('America/Toronto')

client = boto3.client(
    's3',
    aws_access_key_id=aws_access_key_id,
    aws_secret_access_key=aws_secret_access_key,
    # aws_session_token=SESSION_TOKEN,
)

bucket = "<BUCKETNAME>"
DIRECTORY_TO_WATCH = "/Users/<NAME>/.notable/"
last_iteration_path = os.path.join(DIRECTORY_TO_WATCH, ".last_iteration")
exclude = set(["notablechanges.py", last_iteration_path])

try:
    last_iteration = set(open(last_iteration_path, "r").read().split('\n'))
except:
    last_iteration = []

p_local_dict = {}
for i in os.walk(DIRECTORY_TO_WATCH):
    for j in i[2]:
        absdir = os.path.join(i[0], j)
        reldir = os.path.relpath(absdir,DIRECTORY_TO_WATCH)
        t = os.path.getmtime(absdir)
        t = datetime.datetime.fromtimestamp(t, TIMEZONE)
        p_local_dict[reldir] = {'time' : t, 'absdir' : absdir}

p_s3_dict = {}
full_s3_bucket = client.list_objects(Bucket=bucket)
for f in full_s3_bucket.get('Contents', []):
    if f['Key'][-1] == '/' or f['Key'] in exclude:
        #if its a directory then continue
        continue
    p_s3_dict[f['Key']] = f['LastModified']

for p_s3, s3_time in p_s3_dict.items():
    if p_local_dict.get(p_s3) != None:
        #if it exists
        local_details = p_local_dict.get(p_s3)
        print(local_details['time'], s3_time)
        if local_details['time'] > s3_time:
            #if its a more recent copy
            #push it to s3
            print(p_s3, "updating s3")

            client.upload_file(local_details['absdir'], bucket, p_s3)
        else:
            #download it from s3
            print(p_s3, "updating local1")
            client.download_file(bucket, p_s3, os.path.join(DIRECTORY_TO_WATCH, p_s3))
    elif p_s3 in last_iteration:
        #if it was in the last iteration 
        #delete it from s3
        print(p_s3, "deleting s3")

        client.delete_object(Bucket=bucket, Key=p_s3)
    else:
        #download it from s3
        print(p_s3, "updating local2")

        client.download_file(bucket, p_s3, os.path.join(DIRECTORY_TO_WATCH, p_s3))
        
last_iteration = []
for p_local, local_details in p_local_dict.items():
    if p_s3_dict.get(p_local) == None:
        #upload to s3
        print(p_s3, "uploading to s3")

        client.upload_file(local_details['absdir'], bucket, p_local)
    last_iteration.append(p_local)

# open(last_iteration_path, "w+").write("\n".join(last_iteration))
        
