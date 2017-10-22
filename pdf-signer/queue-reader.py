#! /usr/bin/python
import boto3, ConfigParser, iso8601, json, os, pprint, Queue, subprocess, sys, threading

script_dir = os.path.dirname(os.path.realpath(__file__))
cpdf_cmd = script_dir + '/cpdf-binaries-master/Linux-Intel-32bit/cpdf'

pdf_updates = [
        {"key": "amount", "x": 290, "y": 598, "page": 1},
        {"key": "date", "x": 367, "y": 549, "page": 1},
        {"key": "date", "x": 442, "y": 104, "page": 2}
    ]

aws_config = ConfigParser.ConfigParser()
aws_config.read(sys.argv[1])

aws_creds = {
    'aws_access_key_id': aws_config.get('DEFAULT', 'aws_access_key'),
    'aws_secret_access_key': aws_config.get('DEFAULT', 'aws_secret_key'),
}

transaction_queue_info = aws_config.get('DEFAULT', 'transaction_queue').split(':', 1)
pdf_bucket_info = aws_config.get('DEFAULT', 'pdf_bucket').split(':', 2)
pdf_storage_class = pdf_bucket_info[2]
signing_events_topic_info = aws_config.get('DEFAULT', 'signing_events_topic').split(':', 1)

def log_download(prog):
    print "download " + str(prog)
def log_upload(prog):
    print "upload " + str(prog)

def template_download(queue):
    print "thread start"
    pdf_bucket = boto3.session.Session(
        region_name=pdf_bucket_info[0],
        **aws_creds
    ) .resource('s3').Bucket(pdf_bucket_info[1])

    while True:
        template_info = queue.get(True)
        pprint.pprint(template_info)

        dest_stream = template_info["dest"]
        print "download start " + template_info["key"]
        pdf_bucket.Object(template_info["key"]).download_fileobj(dest_stream, Callback=log_download)
        dest_stream.close()
        print "download done"

template_download_queue = Queue.Queue()
template_download_thread = threading.Thread(target=template_download, args=(template_download_queue,))
template_download_thread.daemon = True
template_download_thread.start()

transaction_queue = boto3.session.Session(
        region_name=transaction_queue_info[0],
        **aws_creds
    ).resource('sqs').get_queue_by_name(QueueName=transaction_queue_info[1])
pdf_bucket = boto3.session.Session(
        region_name=pdf_bucket_info[0],
        **aws_creds
    ).resource('s3').Bucket(pdf_bucket_info[1])
signing_events_topic = boto3.session.Session(
        region_name=signing_events_topic_info[0],
        **aws_creds
    ).resource('sns').Topic(signing_events_topic_info[1])

while True:
    print "Getting Messages..."
    messages = transaction_queue.receive_messages(WaitTimeSeconds=20, MaxNumberOfMessages=5)
    if len(messages):
        print "No Messages"
    for msg in messages:
        print "Recieved Messages:"

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


        first_process = subprocess.Popen(
            update_commands[0],
            stdin = subprocess.PIPE,
            stdout = subprocess.PIPE,
            stderr = sys.stderr
        )

        template_download_queue.put({
            "key": template_key,
            "dest": first_process.stdin
        }, True, 5)

        print "create processes"
        last_out = first_process.stdout
        for cmd in update_commands[1:]:
            last_out = subprocess.Popen(
                cmd,
                stdin = last_out,
                stdout = subprocess.PIPE,
                stderr = sys.stderr
            ).stdout
        print "done create processes"

        print "upload start"
        pdf_bucket.Object(result_key).upload_fileobj(last_out, {
                "ContentType": "application/pdf",
                "ServerSideEncryption": "AES256",
                "StorageClass": pdf_storage_class,
        }, Callback=log_upload)
        print "upload done"

        signing_events_topic.publish(
            Subject='PDF Published',
            Message=msg.body
        )
        print "sns done"

        msg.delete()
        print "delete done"
