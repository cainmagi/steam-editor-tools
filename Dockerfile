ARG BASE_IMAGE=amd64/node:26-slim
FROM $BASE_IMAGE

LABEL maintainer="Yuchen Jin <cainmagi@gmail.com>" \
      author="Yuchen Jin <cainmagi@gmail.com>" \
      description="Developer's environment for NodeJS/Yarn." \
      version="1.0.0"

# Set configs
# The following args are temporary but necessary during the deployment.
# Do not change them.
ARG DEBIAN_FRONTEND=noninteractive

# Force the user to be root
USER root

WORKDIR /workdir
RUN apt-get -y update -qq
RUN apt-get -o Acquire::Retries=5 -o Acquire::http::timeout=20 -o Acquire::https::timeout=20 -y install git-core procps
RUN apt-get -o Acquire::Retries=5 -o Acquire::http::timeout=20 -o Acquire::https::timeout=20 -y upgrade && apt-get -y autoremove && apt-get -y autoclean
RUN npm install -g corepack
RUN corepack enable && corepack prepare yarn --activate
RUN yarn set version latest && yarn install

EXPOSE 3000

ENTRYPOINT ["bash"]
