#! /usr/bin/python
import boto3, iso8601, json, os, pprint

script_dir = os.path.dirname(os.path.realpath(__file__))

s3 = boto3.resource('s3')
pdf_bucket = s3.Bucket(os.environ['PDF_BUCKET_NAME'])
pdf_storage_class = os.environ['PDF_BUCKET_STORAGE_CLASS']
pdf_bucket.upload_file(script_dir + '/s3-initial-data/template.pdf', 'templates/template.pdf', {
        "ServerSideEncryption": "AES256",
        "StorageClass": pdf_storage_class
    })

sns = boto3.resource('sns')
signing_events_topic = sns.Topic(os.environ['SIGNING_EVENTS_TOPIC_ARN'])
subscribe_result = signing_events_topic.subscribe(
    Protocol='email',
    Endpoint='email@example.com'
)
pprint.pprint(subscribe_result)
