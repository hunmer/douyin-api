
FROM python:3.12-bullseye
WORKDIR /app

# 安装 Node.js 和 npm (execjs 需要 JavaScript 运行时)
RUN curl -fsSL https://deb.nodesource.com/setup_18.x | bash - && \
    apt-get install -y nodejs

COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r requirements.txt
COPY . /app
EXPOSE 3010
CMD ["python", "app.py"]