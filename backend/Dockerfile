FROM python:3.9-slim

WORKDIR /app_backend

COPY requirements.txt .
RUN pip install -r requirements.txt --no-cache-dir

COPY . .
COPY media/fonts/DejaVuSerif.ttf ../usr/local/lib/python3.9/site-packages/reportlab/fonts

RUN chmod u+x start.sh

EXPOSE 8000

CMD [ "./start.sh" ]