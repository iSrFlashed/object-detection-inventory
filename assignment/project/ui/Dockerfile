from python:3.8.13 as base

ENV PYTHONPATH=$PYTHONPATH:/src/


RUN apt-get update && apt-get install -y \
    libgl1-mesa-glx \
    libglib2.0-0
    
COPY ./requirements.txt /src/requirements.txt

WORKDIR /src

RUN pip install --upgrade pip && pip install --no-cache-dir -r requirements.txt

COPY ./ /src/

FROM base as test
RUN ["python", "-m", "pytest", "-v", "tests"]

FROM base as build
CMD streamlit run --server.port 9090 app/Login/login_ui.py