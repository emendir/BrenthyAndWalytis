FROM emendir/systemd-ipfs:latest
WORKDIR /opt/Brenthy
RUN mkdir /opt/tmp/

## Install Prerequisites:
RUN apt update && apt install -y python3 python3-dev python3-venv python3-pip python-is-python3 virtualenv git jq
RUN python3 -m pip install --break-system-packages --upgrade setuptools build 

COPY Brenthy /opt/brenthy_installer/Brenthy
COPY tests /opt/Brenthy/tests
COPY requirements-devops.txt /opt/brenthy_installer

RUN ../brenthy_installer/Brenthy/InstallScripts/install_brenthy_linux_systemd_cpython.sh  /opt/Brenthy /opt/Brenthy/BlockchainData false true

RUN python3 -m pip install --break-system-packages --root-user-action ignore -r /opt/brenthy_installer/Brenthy/requirements.txt
RUN python3 -m pip install --break-system-packages --root-user-action ignore -r /opt/brenthy_installer/requirements-devops.txt
RUN python3 -m pip install --break-system-packages --root-user-action ignore -e /opt/brenthy_installer/Brenthy
RUN python3 -m pip install --break-system-packages --root-user-action ignore -e /opt/brenthy_installer/Brenthy/blockchains/Walytis_Beta
RUN python3 -m pip install --break-system-packages --root-user-action ignore -e /opt/brenthy_installer/Brenthy/blockchains/Walytis_Beta/legacy_packaging/walytis_beta_embedded
RUN python3 -m pip install --break-system-packages --root-user-action ignore -e /opt/Brenthy/tests/brenthy_docker

RUN for python_package in /opt/Brenthy/tests/brenthy_docker/python_packages/*; do [ -e "$python_package" ] || continue; python3 -m pip install --break-system-packages --root-user-action ignore "$python_package"; done
RUN for python_package in /opt/Brenthy/tests/brenthy_docker/python_packages/*; do [ -e "$python_package" ] || continue; /bin/bash -c "source /opt/Brenthy/Python/bin/activate && python3 -m pip install --break-system-packages --root-user-action ignore $python_package"; done

# clean up files that cause issues with brenthy updates
RUN find /opt/ -type d -name "*.egg-info" -exec rm -rf {} +



RUN /opt/Brenthy/tests/brenthy_docker/ipfs_router_mercy_systemd_setup.sh

## Run with:
# docker run -it --privileged local/brenthy_prereqs
