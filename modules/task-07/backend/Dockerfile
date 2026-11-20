FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY mvstudy ./mvstudy
EXPOSE 8000
CMD ["flask", "--app", "mvstudy.app:create_review_demo", "run", "--host=0.0.0.0", "--port=8000"]
