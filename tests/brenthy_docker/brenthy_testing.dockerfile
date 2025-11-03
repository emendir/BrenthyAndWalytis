FROM local/brenthy_prereqs:latest
WORKDIR /opt/Brenthy
COPY Brenthy /opt/brenthy_installer/Brenthy


## Install Brenthy:
# RUN python3 ../brenthy_installer/Brenthy --dont-update --install-dont-run
RUN ../brenthy_installer/Brenthy/InstallScripts/install_brenthy_linux_systemd_cpython.sh  /opt/Brenthy /opt/Brenthy/BlockchainData false true

# make Brenthy listen on all IP interfaces
RUN sed -i ':a;N;$!ba;s/User=brenthy/User=brenthy\nEnvironment=BRENTHY_API_IP_LISTEN_ADDRESS=0.0.0.0/g' /etc/systemd/system/brenthy.service

# make IPFS listen on all IP interfaces
RUN sed -i ':a;N;$!ba;s/## disable TCP communications/ipfs config Addresses.API "\/ip4\/0.0.0.0\/tcp\/5001"\n\n## disable TCP communications/g' /opt/ipfs_router_mercy.sh
## allow brenthy user to use shell for debugging
RUN usermod -s /bin/bash brenthy

# why is this needed? One day brenthy always ended up disabled in the docker image
RUN systemctl enable brenthy ipfs

COPY tests /opt/Brenthy/tests
RUN find /opt/ -type d -name "*.egg-info" -exec rm -rf {} +
# COPY Brenthy/blockchains/Walytis_Beta/tests /opt/Brenthy/Brenthy/blockchains/Walytis_Beta/tests
## Run with:
# docker run -it --privileged local/brenthy_testing
