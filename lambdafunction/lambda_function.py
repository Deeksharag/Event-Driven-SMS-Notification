import json
import io
import urllib.parse
import boto3
import os

print('Loading function')

s3 = boto3.client('s3')
s3_res = boto3.resource('s3')

def lambda_handler(event, context):

    # Get the object from the event and show its content type
    bucket = event['Records'][0]['s3']['bucket']['name']
    awsRegion = event['Records'][0]['awsRegion']
    key = urllib.parse.unquote_plus(event['Records'][0]['s3']['object']['key'], encoding='utf-8')
    
    try:
        bucket_obj = s3_res.Bucket(bucket)
        print(event)
        obj = next((obj for obj in bucket_obj.objects.all() if obj.key == key ), None)
        print(obj)
        body = obj.get()['Body'].read()
        data = json.load(io.BytesIO(body))
        print(data)
        email = data['email']
        phone = data['phone']
        message = data['message']
        ses_client = boto3.client("ses", awsRegion)
        verify_email(email, ses_client)
        send_email(email, message, ses_client)
        send_sms(phone, message, awsRegion)
            
    except Exception as e:
        print(e)
        print('Error getting object {} from bucket {}. Make sure they exist and your bucket is in the same region as this function.'.format(key, bucket))
        raise e

# Sending mobile SMS
def send_sms(phone, message, awsRegion):
    sms_client = boto3.client(
            "sns",
            aws_access_key_id=os.environ.get('AWS_USER_ACCESS_KEY'), 
            aws_secret_access_key=os.environ.get('AWS_USER_SECRET_KEY'),
            region_name=awsRegion
        )
    sms_client.set_sms_attributes(
            attributes={
                'DefaultSMSType': 'Transactional',
                'DeliveryStatusSuccessSamplingRate': '100',
                'DefaultSenderID': 'CodeBriefly'
            }
        )
    # Send your sms message.
    response = sms_client.publish(
        PhoneNumber=str(phone),
        Message=message
    )
    print(response)
    

# Sending email notification    
def verify_email(email, ses_client):
    response = ses_client.verify_email_identity(EmailAddress=email)
    print(response)
    
def send_email(email, message, ses_client):
    CHARSET = "UTF-8"
    response = ses_client.send_email(
        Destination={
            "ToAddresses": [
                email
            ],
        },
        Message={
            "Body": {
                "Text": {
                    "Charset": CHARSET,
                    "Data": message,
                }
            },
            "Subject": {
                "Charset": CHARSET,
                "Data": "S3 Bucket Notification",
            },
        },
        Source=email,
    )

