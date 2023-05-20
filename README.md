# Monitor SES Bounced Emails

AWS uses bounced and complaint rate of your SES account to measure the sender reputation of your email account. AWS recommends SES users to maintain a bounce rate below 5%. AWS might pause the SES acccount to send additional emails if the bounce rate exceeds 10%.

This article shows how to collect bounced or complaint email addresses from your past email sending activity. It will then put these emails into SES Suppression List so that future emails to these address will be suppressed.

![image-20230519184709206](./assets/Monitor%20SES%20Bounced%20Emails.assets/image-20230519184709206.png)



### 1. Configure SES to Send Feedback Notification to SNS

1. In SES console, select a verified identity.

   ![image-20230519160140532](./assets/Monitor%20SES%20Bounced%20Emails.assets/image-20230519160140532.png)

2. Under "Feedback notification" session, click on Edit button.

   ![image-20230519160222419](./assets/Monitor%20SES%20Bounced%20Emails.assets/image-20230519160222419.png)

3. Create a new SNS topic to receive feedback notifications. 
   ![image-20230519160308178](./assets/Monitor%20SES%20Bounced%20Emails.assets/image-20230519160308178.png)

4. Create a new SNS topic.

   ![image-20230519160446869](./assets/Monitor%20SES%20Bounced%20Emails.assets/image-20230519160446869.png)

5. Since we only concern about bounced and complaint emails, set the topic for both Bounce feedback and Complaint feedback. 

   ![image-20230519160626486](./assets/Monitor%20SES%20Bounced%20Emails.assets/image-20230519160626486.png)

6. Take note of the SNS topic ARN.

   ![image-20230519161340567](./assets/Monitor%20SES%20Bounced%20Emails.assets/image-20230519161340567.png)

   

### 2. Setup SNS to Send Message to SQS Queue

1. Create a standard SQS queue with default values.

   ![image-20230519161225836](./assets/Monitor%20SES%20Bounced%20Emails.assets/image-20230519161225836.png)

2. Go to "Access policy" tab of the SQS topic. Edit the access policy, add a statement to allow SNS topic to send message to the queue.

   ![image-20230519162013745](./assets/Monitor%20SES%20Bounced%20Emails.assets/image-20230519162013745.png)

   ```json
       {
         "Effect": "Allow",
         "Principal": {
           "Service": "sns.amazonaws.com"
         },
         "Action": "SQS:SendMessage",
         "Resource": "SQS_QUEUE_ARN",
         "Condition": {
           "ArnEquals": {
             "aws:SourceArn": "SNS_TOPIC_ARN"
           }
         }
       },
   ```

3. Go to the SNS topic detail page in SNS Console.

   ![image-20230519163210851](./assets/Monitor%20SES%20Bounced%20Emails.assets/image-20230519163210851.png)

4. Create a new subscription with the SQS queue as the endpoint.

   ![image-20230519163327335](./assets/Monitor%20SES%20Bounced%20Emails.assets/image-20230519163327335.png)

5. (Optional) Create a new message in SNS topic. Verify that it is 



### 3. Create and Subscribe Lambda Function to SQS Queue

1. Create a Lambda function for Python.

   ```python
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
   
   ```

2. Grant its IAM role permissions to access SQS and SES.

3. Add an trigger to 

   <img src="./assets/Monitor%20SES%20Bounced%20Emails.assets/image-20230519165714740.png" alt="image-20230519165714740" style="zoom:67%;" />

   ![image-20230519165746104](./assets/Monitor%20SES%20Bounced%20Emails.assets/image-20230519165746104.png)

4. Send test emails from SES. Verify that emails are insert into the SES Supression list.

   ![image-20230519184032288](./assets/Monitor%20SES%20Bounced%20Emails.assets/image-20230519184032288.png)



### Reference

* https://docs.aws.amazon.com/sns/latest/dg/subscribe-sqs-queue-to-sns-topic.html

