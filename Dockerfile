FROM python:3.8
WORKDIR /app
# Set environment variable
ENV PYTHONUNBUFFERED True
COPY requirements.txt .
RUN pip install -r requirements.txt
RUN pip install gunicorn
COPY src src
COPY setupEnv.py setupEnv.py
COPY apps.py apps.py
CMD exec gunicorn --bind :$PORT --workers 1 --threads 8 --timeout 0 --log-level=info apps:app