FROM ubuntu:18.04

WORKDIR /app

ENV LC_ALL=C.UTF-8

RUN apt-get update && apt-get install -y software-properties-common gcc && \
    add-apt-repository -y ppa:deadsnakes/ppa

RUN apt-get update && \
    apt-get install -y python3.7 python3.7-distutils python3.7-dev wget git tor libicu-dev pkg-config llvm-10* \
                       hfst openjdk-8-jdk ant libqt5gui5 graphviz graphviz-dev python3.7-gdbm && \
    apt-get clean
RUN ln /usr/bin/llvm-config-10 /usr/bin/llvm-config
ENV JAVA_HOME=/usr/lib/jvm/java-8-openjdk-amd64/
RUN export JAVA_HOME

RUN update-alternatives --install /usr/bin/python python /usr/bin/python3.7 10 && \
    ln -sf /usr/bin/python3.7 /usr/bin/python3 &&  \
    wget -qO- https://bootstrap.pypa.io/get-pip.py | python3
RUN pip3 install --upgrade cython==0.29.22

COPY ./requirements.txt /app/requirements.txt
RUN pip3 install -r requirements.txt && \
    pip3 cache purge

EXPOSE 5000
CMD [ "python3", "manage.py"]