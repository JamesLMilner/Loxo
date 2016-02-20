FROM ubuntu:14.04

RUN apt-get update && apt-get install -y \
    mongo \
    python \
    nginx \
    pip

RUN mkdir /loxo
ADD . /loxo

RUN cd /loxo & pip install

CMD /etc/init.d/nginx start & \
    /etc.init.d/mongod start & \
    /python /loxo/loxoapi.py
