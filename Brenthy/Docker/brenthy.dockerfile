FROM ubuntu:latest
WORKDIR /opt/Brenthy

## Install Prerequisites:
RUN apt update && apt install -y python-is-python3 python3-pip

COPY Brenthy/requirements.txt /tmp
RUN python3 -m pip install --break-system-packages --root-user-action ignore -r /tmp/requirements.txt

COPY Brenthy /opt/Brenthy/Brenthy

RUN python3 -m pip install --break-system-packages --upgrade setuptools build 
RUN python3 -m pip install --break-system-packages --root-user-action ignore -e /opt/Brenthy/Brenthy
RUN python3 -m pip install --break-system-packages --root-user-action ignore -e /opt/Brenthy/Brenthy/blockchains/Walytis_Beta

# disable auto install python libs
RUN sed -i 's/try_install_python_modules()/#try_install_python_modules()/' /opt/Brenthy/Brenthy/run.py

## Install Brenthy:
RUN touch we_are_in_docker
RUN touch Brenthy/we_are_in_docker

CMD ["/usr/bin/python3", "-u", "/opt/Brenthy/Brenthy", "--dont-install"]

## Run with:
# docker run local/brenthy