FROM ubuntu:18.04

RUN apt-get update
RUN apt-get install -y apache2 \
    libapache2-mod-wsgi-py3 \ 
    #apt-get install libapache2-mod-wsgi-py3 вместо обычного
    build-essential \
    python3.6 \
    python3-dev \
    python3-pip \
    python3-flask \
    nano \
    mongodb \
    curl

#RUN pip3 install --upgrade pip3

COPY ./app/requirements.txt /var/www/apache-flask/app/requirements.txt
RUN pip3 install google-api-python-client google-auth-httplib2 google-auth-oauthlib oauth2client flask-wtf pymongo Flask-Dance flask_csv
RUN service mongodb start
#RUN pip3 install -r /var/www/apache-flask/app/requirements.txt

# Copy over the apache configuration file and enable the site
COPY ./apache-flask.conf /etc/apache2/sites-available/apache-flask.conf
RUN a2ensite apache-flask
RUN a2enmod headers

# Copy over the wsgi file
COPY ./apache-flask.wsgi /var/www/apache-flask/apache-flask.wsgi

COPY ./run.py /var/www/apache-flask/run.py
COPY ./app /var/www/apache-flask/app/

RUN a2dissite 000-default.conf
RUN a2ensite apache-flask.conf
RUN mkdir /var/www/apache-flask/logs

EXPOSE 80

WORKDIR /var/www/apache-flask

#CMD  /usr/sbin/apache2ctl -D FOREGROUND
#CMD service apache2 restart
CMD /etc/init.d/apache2 reload

#CMD /bin/bash
