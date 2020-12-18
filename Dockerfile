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
COPY entrypoint.py entrypoint.py
CMD python entrypoint.py