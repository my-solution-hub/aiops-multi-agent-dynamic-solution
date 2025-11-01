FROM public.ecr.aws/docker/library/python:3.11-slim

WORKDIR /app

COPY ./requirements.txt .
COPY main.py .

RUN pip install --upgrade pip
RUN pip install -r requirements.txt

COPY . .

EXPOSE 8080

CMD ["python", "main.py"]
