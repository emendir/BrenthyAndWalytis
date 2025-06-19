FROM emendir/systemd-ipfs:latest
WORKDIR /opt/Brenthy
RUN mkdir /opt/tmp/

## Install Prerequisites:
RUN apt update && apt install -y python3 python3-dev python3-venv python3-pip python-is-python3 virtualenv git
RUN python3 -m pip install --break-system-packages --upgrade setuptools build 

COPY Brenthy /opt/brenthy_installer/Brenthy
COPY tests /opt/Brenthy/tests
COPY requirements-devops.txt /opt/brenthy_installer

RUN ../brenthy_installer/Brenthy/InstallScripts/install_brenthy_linux_systemd_cpython.sh  /opt/Brenthy /opt/Brenthy/BlockchainData false true

RUN python3 -m pip install --break-system-packages --root-user-action ignore -r /opt/brenthy_installer/Brenthy/requirements.txt
RUN python3 -m pip install --break-system-packages --root-user-action ignore -r /opt/brenthy_installer/requirements-devops.txt
RUN python3 -m pip install --break-system-packages --root-user-action ignore -e /opt/brenthy_installer/Brenthy
RUN python3 -m pip install --break-system-packages --root-user-action ignore -e /opt/brenthy_installer/Brenthy/blockchains/Walytis_Beta
RUN python3 -m pip install --break-system-packages --root-user-action ignore -e /opt/Brenthy/tests/brenthy_docker

# clean up files that cause issues with brenthy updates
RUN find /opt/ -type d -name "*.egg-info" -exec rm -rf {} +


## Install Brenthy:
RUN touch we_are_in_docker
RUN touch ../brenthy_installer/Brenthy/we_are_in_docker
# RUN python3 ../brenthy_installer/Brenthy --dont-update --install-dont-run
# RUN /opt/Brenthy/Python/bin/python -m pip install --break-system-packages -r /opt/brenthy_installer/requirements-devops.txt

## allow brenthy user to use shell for debugging
# RUN usermod -s /bin/bash brenthy

RUN /opt/Brenthy/tests/brenthy_docker/ipfs_router_mercy.sh

## Run with:
# docker run -it --privileged local/brenthy_prereqs