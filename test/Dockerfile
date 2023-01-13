FROM python:3.11.1

WORKDIR /app
RUN pip install --prefer-binary sanic
COPY ./index.py .

CMD [ "python", "index.py" ]

