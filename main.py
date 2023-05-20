import json
import boto3

client = boto3.client('sesv2')

def lambda_handler(event, context):
    # print(f'Event: {event}')

    bounced_emails = []
    complaint_emails = []
    
    # Extract email address from notification
    for record in event['Records']:
        print(f'Processing record: {record}')
        if not record.get('body'):
            print('Invalid record: missing attribute body')
            continue

        body = json.loads(record.get("body"))
        message = json.loads(body.get('Message'))
        print(message)
        
        # Bounce Notification
        if message.get('notificationType') == 'Bounce':
            recipients = message.get('bounce',{}).get('bouncedRecipients',[])
            bounced_emails.extend([r.get('emailAddress') for r in recipients])

        # Complaint Notification
        if message.get('notificationType') == 'Complaint':
            recipients = message.get('complaint',{}).get('complainedRecipients',[])
            complaint_emails.extend([r.get('emailAddress') for r in recipients])

    print(f'Bounced Emails: {bounced_emails}')
    print(f'Complaint Emails: {complaint_emails}')

    # Insert emails into SES Suppression List
    for email in bounced_emails:
        print(f'Supress {email} bounce email: {response}')
        try:
            response = client.put_suppressed_destination(
                EmailAddress=email,
                Reason='BOUNCE'
            )
        except Exception as ex:
            print('Exception:', ex)
        
    for email in complaint_emails:
        print(f'Supress {email} complaint email: {response}')
        try:
            response = client.put_suppressed_destination(
                EmailAddress=email,
                Reason='COMPLAINT'
            )
        except Exception as ex:
            print('Exception:', ex)
