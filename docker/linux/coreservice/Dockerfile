# Geometry service Linux-based Dockerfile
#
# Based on mcr.microsoft.com/dotnet/aspnet:8.0
FROM mcr.microsoft.com/dotnet/aspnet:8.0

# Define the working directory - /app
WORKDIR /app

# Install unzip
RUN apt-get update && \
    apt-get install -y --no-install-recommends unzip=6.* && \
    apt-get install -y --no-install-recommends gcc=4:12.2.* && \
    apt-get install -y --no-install-recommends mono-mcs=6.8.0.* && \
    apt-get install -y --no-install-recommends libgfortran5=12.2.* && \
    rm -rf /var/lib/apt/lists/*

# Add the binary files from the latest release
COPY linux-core-binaries.zip .
RUN unzip -qq linux-core-binaries.zip -d . && \
    rm linux-core-binaries.zip && \
    chmod -R 0755 bin && \
    mv bin/x64/Release_Core_Linux/net8.0/* . && \
    rm -rf bin

# Let the dynamic link loader where to search for shared libraries
ENV LD_LIBRARY_PATH=/app:/app/CADIntegration/bin:/app/Native/Linux

# Define env variables
ENV ANS_DSCO_REMOTE_PORT=50051
ENV ANS_DSCO_REMOTE_IP="0.0.0.0"
ENV LOG_LEVEL=2
ENV ANSYSLMD_LICENSE_FILE=""
ENV ANSYS_CI_INSTALL=/app/CADIntegration
ENV P_SCHEMA=/app/Schema/
ENV ANSYSCL252_DIR=/app/licensingclient/
ENV ANSYSCL261_DIR=/app/licensingclient/
ENV ANSYSCL271_DIR=/app/licensingclient/

# Add container labels
LABEL org.opencontainers.image.authors="ANSYS Inc."
LABEL org.opencontainers.image.vendor="ANSYS Inc."

# Expose the Geometry service port
EXPOSE 50051

# Define the entrypoint for the Geometry service
ENTRYPOINT ["dotnet", "/app/Presentation.ApiServerCoreService.dll"]
