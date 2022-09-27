FROM python:3.7

WORKDIR /

RUN pip3 install --upgrade cython==0.29.22
COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt
# RUN python -m nltk.downloader punkt

COPY . .

EXPOSE 9000
CMD [ "python3", "models_server.py" ]