#! /usr/bin/python
import boto.sqs
import iso8601
import json
import os
import pprint
import subprocess

script_dir = os.path.dirname(os.path.realpath(__file__))
cpdf_cmd = script_dir + '/cpdf-binaries-master/Linux-Intel-32bit/cpdf'

pdf_updates = [
        {"key": "amount", "x": 290, "y": 598, "page": 1},
        {"key": "date", "x": 367, "y": 549, "page": 1},
        {"key": "date", "x": 442, "y": 104, "page": 2}
  ]

conn = boto.sqs.connect_to_region(os.environ['AWS_REGION'])

queue = conn.get_queue(os.environ['TRANSACTION_QUEUE_NAME'])

while True:
  print "Getting Messages..."
  msg = queue.read(wait_time_seconds=20, message_attributes=['.*'])
  if msg == None:
    print "No Messages"
  else:
    print "Recieved Messages:"
#    pprint.pprint(msg)
#    pprint.pprint(msg.id)
#    pprint.pprint(msg.md5)
#    pprint.pprint(msg.message_attributes)
#    pprint.pprint(msg.get_body())

    msg_body = json.loads(msg.get_body())
    pprint.pprint(msg_body)

    date = iso8601.parse_date(msg_body['date'])
    
    amount = msg_body['amount']
    year = format(int(date.year), '04d')
    month = format(int(date.month), '02d')
    day = format(int(date.day), '02d')

    update_commands = []
    for update in pdf_updates:
      if update['key'] == 'amount':
        update_commands.append([cpdf_cmd, '-add-text', str(amount), '-pos-left',
            '{:02d} {:02d}'.format(update['x'], update['y']),
            '-stdin', str(update['page']), '-stdout' ])
      elif update['key'] == 'date':
        for i in [{"val": day, "offset": 0}, {"val": month, "offset": 20}, {"val": year, "offset": 40}]:
            update_commands.append([cpdf_cmd, '-add-text', '{:s}'.format(i['val']), '-pos-left',
            '{:02d} {:02d}'.format(update['x'] + i['offset'], update['y']),
            '-stdin', str(update['page']), '-stdout' ])
      #else:
    
    template_file = open(script_dir + '/template.pdf', 'r')
    last_out = template_file
    for cmd in update_commands[0:-1]:
      last_out = subprocess.Popen(cmd, stdin = last_out, stdout = subprocess.PIPE).stdout

    result_file = open(script_dir + '/result.pdf', 'w')
    subprocess.call(update_commands[-1], stdin = last_out, stdout = result_file)

    result_file.close()
    template_file.close()

    msg.delete()
