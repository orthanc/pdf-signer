#! /usr/bin/python
import boto3, ConfigParser, os, yaml, sys

script_dir = os.path.dirname(os.path.realpath(__file__))

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

templates = set()
for file_name in os.listdir(os.path.join(script_dir, 'profiles')):
    if file_name.endswith('.yaml'):
        profile_file = os.path.join(script_dir, 'profiles', file_name)
        print("Uploading: profiles/" + file_name)
        pdf_bucket.upload_file(profile_file, 'profiles/' + file_name, {
            "ServerSideEncryption": "AES256",
            "StorageClass": pdf_storage_class
        })
        with open(profile_file) as stream:
            profile = yaml.load(stream)
        templates.add(profile['pdf_template'])

for template in templates:
    print("Uploading: template/" + template)
    pdf_bucket.upload_file(os.path.join(script_dir, 'templates', template), 'templates/' + template, {
        "ServerSideEncryption": "AES256",
        "StorageClass": pdf_storage_class
    })

with open(script_dir + '/test_data.yaml') as stream:
    test_data = yaml.load(stream)

for subscriber in test_data['sns_subscribers']:
    print("Subscribing: " + subscriber)
    subscribe_result = signing_events_topic.subscribe(
        Protocol='email',
        Endpoint=subscriber
    )
