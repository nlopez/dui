FROM python:3.7.2-alpine3.8

ENV PYTHONUNBUFFERED 1
COPY requirements.txt /ruis/
RUN pip install --no-cache-dir -r /ruis/requirements.txt
COPY ruis.py /ruis/
WORKDIR /ruis
CMD ["python", "ruis.py"]
