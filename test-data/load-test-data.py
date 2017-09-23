#! /usr/bin/python
import boto3, iso8601, json, os, pprint

script_dir = os.path.dirname(os.path.realpath(__file__))

pdf_bucket_info = os.environ['PDF_BUCKET'].split(':', 2)
pdf_storage_class = pdf_bucket_info[2]
signing_events_topic_info = os.environ['SIGNING_EVENTS_TOPIC'].split(':', 1)

pdf_bucket = boto3.session.Session(region_name=pdf_bucket_info[0]) \
    .resource('s3').Bucket(pdf_bucket_info[1])
signing_events_topic = boto3.session.Session(region_name=signing_events_topic_info[0]) \
    .resource('sns').Topic(signing_events_topic_info[1])


pdf_bucket.upload_file(script_dir + '/s3-initial-data/template.pdf', 'templates/template.pdf', {
        "ServerSideEncryption": "AES256",
        "StorageClass": pdf_storage_class
    })

subscribe_result = signing_events_topic.subscribe(
    Protocol='email',
    Endpoint='email@example.com'
)
pprint.pprint(subscribe_result)
