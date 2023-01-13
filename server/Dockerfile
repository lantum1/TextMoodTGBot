FROM python

RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir kafka-python transformers pyTelegramBotAPI torch

RUN  apt-get update && apt-get install -y wget

WORKDIR /server/

RUN  wget --load-cookies ./cookies.txt "https://docs.google.com/uc?export=download&confirm=$(wget --quiet --save-cookies ./cookies.txt --keep-session-cookies --no-check-certificate 'https://docs.google.com/uc?export=download&id=1Umk_pVp5VI4XZexWe0GU-D-6LjXojVt0' -O- | sed -rn 's/.*confirm=([0-9A-Za-z_]+).*/\1\n/p')&id=1Umk_pVp5VI4XZexWe0GU-D-6LjXojVt0" -O model.tar.gz && rm -rf ./cookies.txt

RUN tar -zxf model.tar.gz --directory .

COPY . .

CMD ["python3", "server.py"]
