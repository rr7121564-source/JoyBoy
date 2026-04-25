FROM python:3.10-slim
WORKDIR /app
COPY . .
RUN apt-get update && apt-get install -y ffmpeg
RUN pip install --no-cache-dir -r requirements.txt
RUN chmod +x start.sh
CMD ["./start.sh"]
