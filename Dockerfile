FROM python:3.12

WORKDIR /app

RUN apt-get update && apt-get install -y gcc libpq-dev

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . /app

ENV PORT=8001

EXPOSE 8001 8002

CMD bash -c "uvicorn api:app --host 0.0.0.0 --port 8001 & python main.py --port 8002 & wait"
