FROM python:3


WORKDIR /code

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["python", "./bot.py"]
