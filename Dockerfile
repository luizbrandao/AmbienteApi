FROM python:3.12-slim-bullseye

WORKDIR /api-climatica

COPY requirements.txt requirements.txt

RUN pip3 install -r requirements.txt

COPY . .

CMD [ "python3", "-m", "flask", "run", "--port=1234", "--host=0.0.0.0" ]