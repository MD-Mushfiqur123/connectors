FROM python:3.12-alpine
ENV CONNECTOR_TYPE=EXTERNAL_IMPORT

# Copy the connector
COPY src /opt/connector
WORKDIR /opt/connector

# Install Python modules
RUN apk --no-cache add git build-base libmagic libffi-dev libxml2-dev libxslt-dev
RUN pip3 install --no-cache-dir -r /opt/connector/requirements.txt

# Expose and entrypoint
CMD ["python", "main.py"]