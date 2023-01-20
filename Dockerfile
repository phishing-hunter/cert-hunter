FROM python:3

ENV YARA_VERSION 4.2.3
ENV YARA_PY_VERSION 4.2.3

COPY ./yara_zip_module/ /yara_zip_module
RUN apt-get update && apt-get install -y automake libtool make gcc flex bison && \
    cd /tmp/ && git clone --recursive --branch v$YARA_VERSION https://github.com/VirusTotal/yara.git && \
    cp /yara_zip_module/miniz.c yara/libyara/miniz.c && \
    cp /yara_zip_module/include/yara/miniz.h yara/libyara/include/yara/miniz.h && \
    cp /yara_zip_module/modules/zip.c yara/libyara/modules/zip.c && \
    cp /yara_zip_module/modules/module_list yara/libyara/modules/module_list && \
    cp /yara_zip_module/Makefile.am yara/libyara/Makefile.am  && \
    cd /tmp/yara && ./bootstrap.sh && sync && ./configure && make -j $(nproc) && make install && \
    cd /tmp/ && git clone --recursive --branch v$YARA_PY_VERSION https://github.com/VirusTotal/yara-python && \
    cd yara-python && python3 setup.py build --dynamic-linking && python3 setup.py install && ldconfig && \
    mkdir /rules  && echo 'import "zip" rule dummy { condition: zip.has_string("index.php", "antibot") > 0 }' > /rules/test_rule && \
    rm -rf /tmp/*
COPY tests/test.zip /test.zip
RUN yara /rules/test_rule /test.zip

COPY requirements.txt .
RUN pip install -r requirements.txt
RUN mkdir /csv
COPY *.csv /csv/
COPY src /app
WORKDIR /app
