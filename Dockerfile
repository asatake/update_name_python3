FROM python:3

WORKDIR /usr/src/app
COPY requirements.txt ./

RUN pip install --no-cache-dir -r requirements.txt

COPY config ./config
COPY main ./main
RUN mkdir log

CMD [ "python", "/usr/src/app/main/main.py" ]
