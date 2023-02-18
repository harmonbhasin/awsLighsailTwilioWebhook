# Set base image (host OS)
FROM python:3.10-bullseye

# By default, listen on port 5000
EXPOSE 5000/tcp

# Set the working directory in the container
WORKDIR /app

# Copy the dependencies file to the working directory
COPY requirements.txt .

# Copy credentials into the working directory
COPY service_account.json .
COPY Google.py .
COPY Helper.py .
COPY quotes.csv .
COPY .env .
COPY cert.pem .

# Install any dependencies
RUN pip install -r requirements.txt

# Copy the content of the local src directory to the working directory
COPY app.py .

# Specify the command to run on container start
CMD [ "python", "./app.py" ]
