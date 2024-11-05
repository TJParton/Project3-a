# Use an official python image as a base image
FROM python:3.8-slim-buster

# set the working dir in the container to /app
WORKDIR /app

# copy the contents of the current directory in the computer /app directory
COPY . /app

# Upgrade pip
RUN pip install --upgrade pip 

# install any needed packages
RUN pip install  --no-cache-dir -r requirements.txt

# set the default commands to run when starting the container 
CMD ["python", "app.py"]
