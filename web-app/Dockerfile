FROM python:3.12-slim
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
WORKDIR /app
COPY requirements.txt /tmp/requirements.txt
RUN pip install --no-cache-dir -r /tmp/requirements.txt
COPY web-app/ /app/
ENV FLASK_APP=app.py FLASK_ENV=production
EXPOSE 5000
#CMD ["python", "app.py", "--host=0.0.0.0", "--port=8000"]
CMD ["flask", "run", "--host=0.0.0.0", "--port=5000"]