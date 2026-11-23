FROM python:3.14-slim
WORKDIR /app
COPY app.py sample.txt ./
ENTRYPOINT ["python", "app.py"]
CMD ["sample.txt"]
