FROM python


RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir kafka-python transformers pyTelegramBotAPI torch

WORKDIR /bot/bot-server

COPY . .

CMD ["python3", "bot-server.py"]
