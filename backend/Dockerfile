FROM python:3.9
RUN apt update &&\
    apt upgrade -y &&\
    apt install -y libpq-dev gcc netcat-traditional
WORKDIR /app
COPY requirements.txt ./
RUN pip install -U pip &&\
    pip install -r requirements.txt --no-cache-dir
COPY foodgram/ ./
RUN chmod +x run_app.sh
CMD [ "gunicorn", "-b", "0:8000", "foodgram.wsgi" ]
