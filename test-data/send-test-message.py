#! /usr/bin/python
import boto3, iso8601, json, os, pprint

transaction_queue_info = os.environ['TRANSACTION_QUEUE'].split(':', 1)

transaction_queue = boto3.session.Session(region_name=transaction_queue_info[0]) \
    .resource('sqs').get_queue_by_name(QueueName=transaction_queue_info[1])

transaction_queue.send_message(
    MessageBody='{"amount": 9999, "date": "2017-06-12", "template_key": "templates/template.pdf", "result_key": "results/result.pdf"}'
)
