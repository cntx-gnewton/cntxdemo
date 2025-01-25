FROM python:3.11
WORKDIR /code
COPY requirements.txt .
RUN pip3 install --no-cache-dir -r requirements.txt
COPY app /code/app
COPY data /code/data
EXPOSE 8080

CMD ["streamlit","run","--server.port","8080","app/main.py"]