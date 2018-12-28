FROM python:3.7.2-alpine3.8

ENV PYTHONUNBUFFERED 1
COPY requirements.txt /dui/
RUN pip install --no-cache-dir -r /dui/requirements.txt
COPY dui.py /
WORKDIR /
CMD ["python", "/dui.py"]
