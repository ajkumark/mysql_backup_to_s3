import os
import json
import shutil
from datetime import datetime

import boto3

S3_BUCKET = ''

with open('databases.json', 'r') as f:
    data = f.read()
    data = json.loads(data)

time_prefix = datetime.now().strftime('%Y-%m-%dT%H-%M-%S')

os.system('mkdir -p backups')

for db in data:
    db_user = db.get('username')
    db_name = db.get('name')
    db_password = db.get('password')
    db_host = db.get('host', 'localhost')
    print('backing up {}'.format(db_name), datetime.now(), '\n')
    backup_file = 'backups/' + db_name + '-' + time_prefix + '.sql'
    dumpcmd = "mysqldump -h " + db_host + " -u " + db_user + " -p" + db_password + " " + db_name + " > " + backup_file
    os.system(dumpcmd)

    gzipcmd = "gzip " + backup_file
    os.system(gzipcmd)

    s3 = boto3.client('s3')
    for root, dirs, files in os.walk('backups'):
        for filename in files:
            full_path = os.path.join(root, filename)
            with open(full_path, "rb") as f:
                s3.upload_fileobj(f, S3_BUCKET, time_prefix+"/"+filename)
    print('completed backup {}'.format(db_name), datetime.now(), '\n')

shutil.rmtree("backups")

