import json, io, boto3, os, ydb, sys
from sanic import Sanic
from sanic.response import text
from PIL import Image

app = Sanic(__name__)

@app.after_server_start
async def after_server_start(app, loop):
    print(f"App listening at port {os.environ['PORT']}")

@app.route("/", methods=["POST"])
async def handler(request):
    msg = json.loads(json.loads(request.body)['messages'][0]['details']['message']['body'])
    print(msg)
    session = boto3.session.Session(region_name='ru-central1')
    s3 = session.client(service_name='s3', endpoint_url='https://storage.yandexcloud.net')
    img = io.BytesIO()
    photo_key = msg['photo_key']
    cords = msg['cords']
    s3.download_fileobj('cloudphoto', photo_key, img)

    image = Image.open(img)
    left = int(cords[0]['x'])
    top = int(cords[0]['y'])
    right = int(cords[3]['x'])
    bottom = int(cords[1]['y'])
    cropped = image.crop((left, top, right, bottom))

    upload_img = io.BytesIO()
    cropped.save(upload_img, 'jpeg')
    upload_img.seek(0)
    new_photo_key = ''.join([photo_key.split('.')[0], str(left), str(top), str(right), str(bottom), '.jpg'])
    s3.upload_fileobj(upload_img, 'itis-2022-2023-vvot45-faces', new_photo_key)

    endpoint = os.environ['DB_ENDPOINT']
    path = os.environ['DB_PATH']
    credentials = ydb.construct_credentials_from_environ()
    print(credentials)
    print(vars(credentials))
    driver_config = ydb.DriverConfig(
        endpoint, path, credentials=credentials
    )
    driver = ydb.Driver(driver_config)
    
    query = f"""
        PRAGMA TablePathPrefix("{os.environ['DB_PATH']}");
        INSERT INTO {os.environ['DB_NAME']} (original_photo, face_photo)
        VALUES ('{photo_key}', '{new_photo_key}');
    """
    session = driver.table_client.session().create()
    session.transaction().execute(query, commit_tx=True)
    session.closing()

    return text('Ok')

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=int(os.environ['PORT']), motd=False, access_log=False)