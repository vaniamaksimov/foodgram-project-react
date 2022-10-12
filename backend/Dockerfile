FROM python:3.9-slim

WORKDIR /app_backend

COPY requirements.txt .
RUN pip install -r requirements.txt --no-cache-dir

COPY . .

RUN chmod u+x start.sh

EXPOSE 8000

CMD [ "./start2.sh" ]