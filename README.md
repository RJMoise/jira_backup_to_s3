# jira_backup_to_s3

A script that automates the Jira backup process and uploads the zip to an AWS S3 bucket.

Important Note: Not all of this code is mine, credit does to (https://bitbucket.org/atlassianlabs/automatic-cloud-backup/src/master/) where a few good people have already written a python script (and others) that initiates and downloads the Jira backup locally.
I merely modified it to read the config options from a seperate file, upload to an S3 bucket and then remove the local copy.

The JSON_DATA at the top of the sctip can be modified to suit your needs. In my case I did not want attachments added, or for it to be exported to their cloud.
Sidenote: You can only backup Jira ONCE every 48 hours if you include attachments. There is no limit if you do not include them.

To use a config file to keep your keys and other variables hidden, create a (in my case) db.ini file in the same location as the script.
Template based off the code:


[jira]

site = (account name before '.atlassian.net')

email = (accounts uername)

token = (create an api token to place here)



[aws]

aws_access_key_id =

aws_secret_access_key =

send_to_bucket =



[localPath]

filePath = (folder that files are stored in locally when downloaded)
