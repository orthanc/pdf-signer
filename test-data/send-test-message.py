#! /usr/bin/python
import boto3, iso8601, json, os, pprint

sqs = boto3.resource('sqs')
transaction_queue = sqs.get_queue_by_name(QueueName=os.environ['TRANSACTION_QUEUE_NAME'])

transaction_queue.send_message(
    MessageBody='{"amount": 9999, "date": "2017-06-12", "template_key": "templates/template.pdf", "result_key": "results/result.pdf"}'
)
