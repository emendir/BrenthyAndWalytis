FROM local/brenthy_prereqs:latest
WORKDIR /opt/Brenthy
COPY Brenthy /opt/brenthy_installer/Brenthy


## Install Brenthy:
RUN touch ../brenthy_installer/Brenthy/we_are_in_docker
RUN python3 ../brenthy_installer/Brenthy --dont-update --install-dont-run
## allow brenthy user to use shell for debugging
RUN usermod -s /bin/bash brenthy

## Run with:
# docker run -it --privileged local/brenthy_testing