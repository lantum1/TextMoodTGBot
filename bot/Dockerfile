FROM python


RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir kafka-python transformers pyTelegramBotAPI torch

WORKDIR /bot/

COPY . .

CMD ["python3", "bot.py"]
