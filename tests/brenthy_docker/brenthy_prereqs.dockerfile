FROM emendir/systemd-ipfs:latest
WORKDIR /opt/Brenthy
COPY Brenthy /opt/brenthy_installer/Brenthy
COPY tests /opt/Brenthy/tests

## Install Prerequisites:
RUN apt install -y virtualenv
RUN python3 -m pip install --root-user-action ignore --upgrade pip setuptools wheel build virtualenv
RUN python3 -m pip install --root-user-action ignore -r /opt/brenthy_installer/Brenthy/requirements.txt
RUN python3 -m pip install --root-user-action ignore /opt/brenthy_installer/Brenthy
RUN python3 -m pip install --root-user-action ignore /opt/brenthy_installer/Brenthy/blockchains/Walytis_Beta

## Install Brenthy:
RUN touch ../brenthy_installer/Brenthy/we_are_in_docker
RUN python3 ../brenthy_installer/Brenthy --dont-update --install-dont-run
## allow brenthy user to use shell for debugging
RUN usermod -s /bin/bash brenthy

RUN /opt/Brenthy/tests/brenthy_docker/ipfs_router_mercy.sh

## Run with:
# docker run -it --privileged local/brenthy_prereqs