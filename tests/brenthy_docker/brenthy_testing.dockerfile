FROM local/brenthy_prereqs:latest
WORKDIR /opt/Brenthy
COPY Brenthy /opt/brenthy_installer/Brenthy

# reinstall brenthy_api & walytis_beta_api
RUN python3 -m pip install  --break-system-packages --root-user-action ignore /opt/brenthy_installer/Brenthy
RUN python3 -m pip install  --break-system-packages --root-user-action ignore /opt/brenthy_installer/Brenthy/blockchains/Walytis_Beta

## Install Brenthy:
RUN touch ../brenthy_installer/Brenthy/we_are_in_docker
RUN python3 ../brenthy_installer/Brenthy --dont-update --install-dont-run
## allow brenthy user to use shell for debugging
RUN usermod -s /bin/bash brenthy

## Run with:
# docker run -it --privileged local/brenthy_testing