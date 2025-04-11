# object-detection-inventory
Final Project - Object detection for in-store inventory management.

# Set a virtual environment

`Created with python 3.9.0`

```bash
python -m venv testenv
```

# Access and activate virtual environment

```bash
.\testenv\Scripts\activate
```
# Install dependencies from requirements.txt

`IMPORTANT:` remember run this command inside the virtual environment

```bash
pip install -r requirements.txt
```

When we need more dependencies, add them to "requirements.txt" file

# Configure Docker

Make sure you have `Docker` installed in your computer and you have created the network for microservices.

To create the network:

```bash
$ docker network create shared_network
```

First time, create all images:

```bash
cd project
docker-compose up --build -d
```

Populate the database

```bash
cd project/api
cp .env.example .env
docker-compose up --build -d
```

# How to use this app

To test this application, you must download the `develop` branch from this repository.

Once this is done, use the command line to enter the `/project` directory, as this is where the `docker-compose.yml` file is defined. The containers must be started with the command

```
docker-compose up --build -d
```

When this process completes and the containers are running, the application will be available at http://localhost:9090

One last step, to login the application the credentials are:
- user: `admin@example.com`
- password: `admin`

# About notebooks

In the `notebooks` directory you can find some notebooks that show the work we have done both in the EDA and in the model training.