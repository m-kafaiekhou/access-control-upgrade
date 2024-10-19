FROM python:3.11

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

WORKDIR /code
COPY requirements.txt /code/

RUN pip install -r requirements.txt

RUN apt-get update && apt-get install -y libgl1-mesa-glx

RUN pip install pyserial

COPY . /code/

CMD python3 manage.py makemigrations --noinput && \
    python3 manage.py migrate --noinput && \
    python manage.py runserver 0.0.0.0:8001

