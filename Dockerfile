FROM gcr.io/google_appengine/python

# Create a virtualenv for the application dependencies.
RUN virtualenv /env -p python3.6
ENV PATH /app:$PATH
ENV PATH /env/bin:$PATH
ENV FLASK_CONFIG /app/config.yaml

ADD requirements.txt /app/requirements.txt
RUN /env/bin/pip install -r /app/requirements.txt
ADD web_api /app/web_api
ADD cli.py /app
ADD /instance/config.yaml /app

EXPOSE 8080

CMD python cli.py --reset && gunicorn -w 2 -b 0.0.0.0:8080 'web_api:create_app()'
