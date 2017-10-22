#! /usr/bin/python
import boto3, ConfigParser, iso8601, json, os, yaml, sys, ulid
from datetime import datetime

script_dir = os.path.dirname(os.path.realpath(__file__))

profile_file_name = sys.argv[2] + '.yaml'
with open(os.path.join(script_dir, 'profiles', profile_file_name)) as stream:
    profile = yaml.load(stream)

date = datetime.now()

aws_config = ConfigParser.ConfigParser()
aws_config.read(script_dir + '/creds/' + sys.argv[1] + '/test_user-aws_services.ini')

aws_creds = {
    'aws_access_key_id': aws_config.get('DEFAULT', 'aws_access_key'),
    'aws_secret_access_key': aws_config.get('DEFAULT', 'aws_secret_key'),
}

transaction_queue_info = aws_config.get('DEFAULT', 'transaction_queue').split(':', 1)

transaction_queue = boto3.session.Session(
        region_name=transaction_queue_info[0],
        **aws_creds
    ).resource('sqs').get_queue_by_name(QueueName=transaction_queue_info[1])

iso_date = '{:04d}-{:02d}-{:02d}'.format(date.year, date.month, date.day)
format_values = {
    'date': iso_date,
    'ulid': ulid.ulid(),
}
transaction_queue.send_message(
    MessageBody=json.dumps({
        'amount': int(sys.argv[3]),
        'date': iso_date,
        'profile_key': 'profiles/' + profile_file_name,
        'template_key': 'templates/' + profile['pdf_template'],
        'result_key': 'results/' + profile['result_key_template'].format(**format_values),
    })
)
