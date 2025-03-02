FROM local/brenthy_prereqs:latest
WORKDIR /opt/Brenthy
COPY Brenthy /opt/brenthy_installer/Brenthy


## Install Brenthy:
RUN touch ../brenthy_installer/Brenthy/we_are_in_docker
RUN python3 ../brenthy_installer/Brenthy --dont-update --install-dont-run

# make Brenthy listen on all IP interfaces
RUN sed -i ':a;N;$!ba;s/User=brenthy/User=brenthy\nEnvironment=BRENTHY_API_IP_LISTEN_ADDRESS=0.0.0.0/g' /etc/systemd/system/brenthy.service

# make IPFS listen on all IP interfaces
RUN sed -i ':a;N;$!ba;s/## disable TCP communications/ipfs config Addresses.API "\/ip4\/0.0.0.0\/tcp\/5001"\n\n## disable TCP communications/g' /opt/ipfs_router_mercy.sh
## allow brenthy user to use shell for debugging
RUN usermod -s /bin/bash brenthy

COPY tests /opt/Brenthy/tests
## Run with:
# docker run -it --privileged local/brenthy_testing