#! /usr/bin/python
import boto.sqs
import os
import pprint

pprint.pprint(boto.sqs.regions())
conn = boto.sqs.connect_to_region(os.environ['AWS_REGION'])

queue = conn.get_queue(os.environ['TRANSACTION_QUEUE_NAME'])

while True:
  print 'Getting Messages...'
  rs = queue.get_messages(num_messages=1, wait_time_seconds=20)
  if len(rs) > 0:
    print 'Recieved Messages:'
  else:
    print 'No Messages'
  for msg in rs:
    pprint.pprint(msg.get_body())
    msg.delete()
