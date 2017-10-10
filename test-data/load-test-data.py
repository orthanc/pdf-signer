#! /usr/bin/python
import boto3, ConfigParser, os, yaml, sys

script_dir = os.path.dirname(os.path.realpath(__file__))

with open(script_dir + '/test_data.yaml') as stream:
    test_data = yaml.load(stream)

aws_config = ConfigParser.ConfigParser()
aws_config.read(script_dir + '/creds/' + sys.argv[1] + '/test_user-aws_services.ini')

aws_creds = {
    'aws_access_key_id': aws_config.get('DEFAULT', 'aws_access_key'),
    'aws_secret_access_key': aws_config.get('DEFAULT', 'aws_secret_key'),
}

pdf_bucket_info = aws_config.get('DEFAULT', 'pdf_bucket').split(':', 2)
pdf_storage_class = pdf_bucket_info[2]
signing_events_topic_info = aws_config.get('DEFAULT', 'signing_events_topic').split(':', 1)

pdf_bucket = boto3.session.Session(
        region_name=pdf_bucket_info[0],
        **aws_creds
    ).resource('s3').Bucket(pdf_bucket_info[1])
signing_events_topic = boto3.session.Session(
        region_name=signing_events_topic_info[0],
        **aws_creds
    ).resource('sns').Topic(signing_events_topic_info[1])


for template in test_data['templates'].itervalues():
    print("Uploading: template/" + template['template_pdf'])
    pdf_bucket.upload_file(script_dir + '/s3-initial-data/' + template['template_pdf'], 'templates/' + template['template_pdf'], {
        "ServerSideEncryption": "AES256",
        "StorageClass": pdf_storage_class
    })

for subscriber in test_data['sns_subscribers']:
    print("Subscribing: " + subscriber)
    subscribe_result = signing_events_topic.subscribe(
        Protocol='email',
        Endpoint=subscriber
    )
