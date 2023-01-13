FROM ubuntu:22.04

WORKDIR /bot/bot-server

RUN  apt-get update && apt-get install -y wget && \
     wget "https://downloader.disk.yandex.ru/disk/5ca2c6340c0285bc7cced6e116c85ff9b9bb0ca05643b6984d206a689775d45d/63c17111/2LHPJYDrUb-WQau2SdHjT1DOLdz_k4UnmNeFWX_4wD7cDTUER7K1fm3RE0yo_WviB60HlzvVn9o9-PrUvRSK1w%3D%3D?uid=0&filename=model.tar.gz&disposition=attachment&hash=NY4MGkQzpfRLE06gWXYDdS3KGdEab0cAjo1YtIlEbewjUiZsS2JOo0vyF7ldwoInq/J6bpmRyOJonT3VoXnDag%3D%3D%3A&limit=0&content_type=application%2Fx-gzip&owner_uid=275871738&fsize=630084669&hid=78e18ba770b0cbd0c1c0588977a1e28d&media_type=compressed&tknv=v2" -O model.tar.gz && \
     tar -xzvf model.tar.gz



COPY . .
