ARG BASE_IMAGE=python:3.14-slim
FROM $BASE_IMAGE

LABEL maintainer="Yuchen Jin <cainmagi@gmail.com>" \
      author="Yuchen Jin <cainmagi@gmail.com>" \
      description="Developer's environment for Steam Editor Tools." \
      version="1.0.0"

# Set configs
ARG INSTALL_MODE=default
# The following args are temporary but necessary during the deployment.
# Do not change them.
ARG DEBIAN_FRONTEND=noninteractive

# Force the user to be root
USER root

WORKDIR /app
COPY ./docker/*.txt /app/

# Install dependencies
COPY ./docker/install.sh /app/
RUN bash /app/install.sh $INSTALL_MODE

# Copy codes
COPY ./steam_editor_tools /app/steam_editor_tools
COPY ./examples /app/examples
COPY ./tests /app/tests
COPY ./version /app/version
COPY ./*.* /app/
COPY ./LICENSE /app/

# Finalize
COPY ./docker/entrypoint.sh /app/

ENTRYPOINT ["/bin/bash", "--login", "-i", "/app/entrypoint.sh"]
CMD [""]
