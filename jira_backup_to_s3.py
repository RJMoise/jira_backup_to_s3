import time
import re
import configparser
import boto3
import requests
import os
from botocore.exceptions import NoCredentialsError

# Constants (DO NOT CHANGE)
JSON_DATA = b'{"cbAttachments": "false", "exportToCloud": "false"}'

# Loads key values from a seperate ini file
config = configparser.ConfigParser()
config.read("db.ini")
jiraSite = config["jira1"]["site"]
jiraEmail = config["jira1"]["email"]
jiraToken = config["jira1"]["token"]
awsAccesskey = config["training"]["aws_access_key_id"]
awsSecretKey = config["training"]["aws_secret_access_key"]


def jira_backup(account, username, token, json, folder):

    # Create the full base url for the JIRA instance using the account name.
    url = "https://" + account + ".atlassian.net"

    # Open new session for cookie persistence and auth.
    session = requests.Session()
    session.auth = (username, token)
    session.headers.update(
        {"Accept": "application/json", "Content-Type": "application/json"}
    )

    # Start backup
    backup_req = session.post(
        url + "/rest/backup/1/export/runbackup", data=json)

    # Catch error response from backup start and exit if error found.
    if "error" in backup_req.text:
        print(backup_req.text)
        exit(1)

    # Get task ID of backup.
    task_req = session.get(url + "/rest/backup/1/export/lastTaskId")
    task_id = task_req.text

    # set starting task progress values outside of while loop and if statements.
    task_progress = 0
    last_progress = -1

    # Get progress and print update until complete
    while task_progress < 100:

        progress_req = session.get(
            url + "/rest/backup/1/export/getProgress?taskId=" + task_id
        )
        print(progress_req)
        # Chop just progress update from json response
        try:
            task_progress = int(
                re.search('(?<=progress":)(.*?)(?=,)',
                          progress_req.text).group(1)
            )
            # print(progress_req.text)
        except AttributeError:
            print(progress_req.text)
            exit(1)

        if (last_progress != task_progress) and "error" not in progress_req.text:
            last_progress = task_progress
        elif "error" in progress_req.text:
            print(progress_req.text)
            exit(1)

        if task_progress < 100:
            time.sleep(10)

    if task_progress == 100:
        download = re.search('(?<=result":")(.*?)(?=\",)',
                             progress_req.text).group(1)

        print('Backup complete, downloading files.')
        print('Backup file can also be downloaded from ' +
              url + '/plugins/servlet/' + download)

        date = time.strftime("%Y%m%d_%H%M%S")

        filename = account + '_backup_' + date + '.zip'

        file = session.get(url + '/plugins/servlet/' + download, stream=True)

        file.raise_for_status()

        with open(folder + filename, 'wb') as handle:
            for block in file.iter_content(1024):
                handle.write(block)

        print(filename + 'downloaded to ' + folder)

        stream_to_s3(filename, folder)


def stream_to_s3(filename, folder):

    s3 = boto3.client(
        "s3",
        aws_access_key_id=awsAccesskey,
        aws_secret_access_key=awsSecretKey
    )

    bucket_resource = s3

    bucket_resource.upload_file(
        Bucket='jira-lucro',
        Filename=folder+filename,
        Key=filename
    )
    remove_from_local(folder, filename)


def remove_from_local(folder, filename):
    os.remove(folder+filename)


def main():

    localLocation = r"C:\Backups\\"
    jira_backup(jiraSite, jiraEmail, jiraToken, JSON_DATA, localLocation)


if __name__ == "__main__":
    main()
