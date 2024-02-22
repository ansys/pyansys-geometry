# Geometry service Linux-based Dockerfile
#
# Based on mcr.microsoft.com/dotnet/aspnet:6.0
FROM mcr.microsoft.com/dotnet/aspnet:6.0

# Define the working directory - /app
WORKDIR /app

# Install unzip
RUN apt-get update && \
    apt-get install -y --no-install-recommends unzip=6.0-26+deb11u1 && \
    rm -rf /var/lib/apt/lists/*

# Add the binary files from the latest release
COPY linux-binaries.zip .
RUN unzip -qq linux-binaries.zip -d . && \
    rm linux-binaries.zip && \
    chmod -R 0755 DockerLinux && \
    mv DockerLinux/bin/x64/Release_Linux/net6.0/* . && \
    rm -rf DockerLinux

# Let the dynamic link loader where to search for shared libraries
ENV LD_LIBRARY_PATH="/app"

# Define env variables
ENV ANS_DSCO_REMOTE_PORT=50051
ENV ANS_DSCO_REMOTE_IP="0.0.0.0"
ENV ANS_DSCO_REMOTE_LOGS_CONFIG="linux"
ENV LOG_LEVEL=2
ENV ENABLE_TRACE=0
ENV ANSYSLMD_LICENSE_FILE=""

# Add container labels
LABEL org.opencontainers.image.authors="ANSYS Inc."
LABEL org.opencontainers.image.vendor="ANSYS Inc."

# Expose the Geometry service port
EXPOSE 50051

# Define the entrypoint for the Geometry service
ENTRYPOINT ["dotnet", "/app/Presentation.ApiServerLinux.dll"]