# lightweight Python base image
FROM python:3.11-slim

# set working directory inside container
WORKDIR /app

# copy everything into container
COPY . /app

# ensure python output shows immediately (important for console apps)
ENV PYTHONUNBUFFERED=1

# run the script
CMD ["python", "task_manager.py"]