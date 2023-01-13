import boto3, io, base64, requests, json, os

def face_detection(img_b64, folderId, token, token_type):
    url = 'https://vision.api.cloud.yandex.net/vision/v1/batchAnalyze'
    req_json = {
        'folderId': folderId, 
        'analyze_specs': [{
            'content': img_b64, 
            'features': [{'type': 'FACE_DETECTION'}]
            }]
        }
    body = json.dumps(req_json)
    resp = requests.post(
        url=url, 
        headers={
            'Authorization': token_type + ' ' + token, 
            'Content-Type': 'application/json'
            }, 
        data=body)

    return resp


def handler(event, context):
    bucket = event['messages'][0]['details']['bucket_id']
    object_id = event['messages'][0]['details']['object_id']

    session = boto3.session.Session(region_name='ru-central1')
    s3 = session.client(
        service_name='s3',
        endpoint_url='https://storage.yandexcloud.net')
    img = io.BytesIO()
    s3.download_fileobj(bucket, object_id, img)
    img_b64 = str(base64.b64encode(img.getvalue()))[2:-1]

    iam_token = context.token['access_token']
    token_type = context.token['token_type']
    folderId = 'b1gqjhusttnaqbbclmk8'
    resp = face_detection(img_b64, folderId, iam_token, token_type)

    faces = json.loads(resp.content)
    faces_cord = faces['results'][0]['results'][0]['faceDetection']['faces']
    mq = session.client(
        service_name='sqs', 
        endpoint_url='https://message-queue.api.cloud.yandex.net', 
        aws_access_key_id='YCAJEa-unrazdIwwi-A7xr88R', 
        aws_secret_access_key='YCMtLeji1eGJ37qBJP5GLoeQh72K9CSJklwHhaug')
    queue_url = 'https://message-queue.api.cloud.yandex.net/b1g71e95h51okii30p25/dj600000000b17tl02mk/vvot45-tasks'
    for face in faces_cord:
        mq.send_message(
            QueueUrl=queue_url, 
            MessageBody=json.dumps({
                'photo_key': object_id, 
                'cords': face['boundingBox']['vertices']
                }))
    
    return {
        'statusCode': 200,
        'body': 'Hello World!',
    }


