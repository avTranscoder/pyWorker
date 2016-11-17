FROM arnaudmarcantoine/avtranscoder:dev

ADD . /server

RUN apk add py-pip
RUN pip install flask

CMD export PYTHONPATH=/usr/local/lib/python2.7/site-packages && python /server/server.py