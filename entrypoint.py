import os

from setupEnv import setupEnv

setupEnv()
os.system("exec gunicorn --bind :$PORT --workers 1 --threads 8 --timeout 0 --log-level=info apps:app")