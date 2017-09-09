#! /usr/bin/python
import boto3, iso8601, json, os, pprint, subprocess, tempfile

script_dir = os.path.dirname(os.path.realpath(__file__))
cpdf_cmd = script_dir + '/cpdf-binaries-master/Linux-Intel-32bit/cpdf'

pdf_updates = [
        {"key": "amount", "x": 290, "y": 598, "page": 1},
        {"key": "date", "x": 367, "y": 549, "page": 1},
        {"key": "date", "x": 442, "y": 104, "page": 2}
  ]

sqs = boto3.resource('sqs')
s3 = boto3.resource('s3')

transaction_queue = sqs.get_queue_by_name(QueueName=os.environ['TRANSACTION_QUEUE_NAME'])
pdf_bucket = s3.Bucket(os.environ['PDF_BUCKET_NAME'])

while True:
  print "Getting Messages..."
  messages = transaction_queue.receive_messages(WaitTimeSeconds=20, MaxNumberOfMessages=10)
  if len(messages):
    print "No Messages"
  for msg in messages:
    print "Recieved Messages:"
#    pprint.pprint(msg)
#    pprint.pprint(msg.id)
#    pprint.pprint(msg.md5)
#    pprint.pprint(msg.message_attributes)
#    pprint.pprint(msg.get_body())

    msg_body = json.loads(msg.body)
    pprint.pprint(msg_body)

    date = iso8601.parse_date(msg_body['date'])
    template_key = msg_body['template_key']
    result_key = msg_body['result_key']
    
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
    
    with tempfile.TemporaryFile() as template_file:
      pdf_bucket.Object(template_key).download_fileobj(template_file)
      template_file.seek(0)
      last_out = template_file
      for cmd in update_commands:
        last_out = subprocess.Popen(cmd, stdin = last_out, stdout = subprocess.PIPE).stdout

      pdf_bucket.Object(result_key).upload_fileobj(last_out)

    msg.delete()
