# Use an official Python runtime as a parent image
FROM python:3.10-slim

# Set the working directory in the container
WORKDIR /usr/src/app

# Copy the requirements.txt to the container at /usr/src/app/
COPY requirements.txt ./

# Install any Python packages from requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy the current directory contents into the container at /usr/src/app/
COPY . .

# Expose port 80 for the container (optional, if you're running a web service)
EXPOSE 80

# Set the default command to run the Python script
CMD ["tail", "-f", "/dev/null"]
