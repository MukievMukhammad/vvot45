FROM python:3.10-slim

COPY face-cut.py .
COPY requirements.txt .
RUN pip install --no-cache-dir --prefer-binary sanic \
    && pip install --no-cache-dir -r requirements.txt

CMD [ "python", "./face-cut.py" ]