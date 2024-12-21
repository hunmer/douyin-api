
FROM python:3.12-bullseye
WORKDIR /app
COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r requirements.txt
COPY . /app
EXPOSE 3010
CMD ["python", "app.py"]