# hadolint shell = cmd.exe
#
# Geometry service Windows-based Dockerfile
#
# Based on mcr.microsoft.com/dotnet/framework/runtime:4.7.2-windowsservercore-ltsc2022
FROM mcr.microsoft.com/dotnet/aspnet:8.0-preview-windowsservercore-ltsc2022

# Define the working directory - /temp
WORKDIR /temp

# Download Microsoft Visual C++ Redistributable x64
ADD https://aka.ms/vs/17/release/VC_redist.x64.exe VC_redist.x64.exe
RUN VC_redist.x64.exe /install /quiet /norestart
ADD https://download.visualstudio.microsoft.com/download/pr/f5f1c28d-7bc9-431e-98da-3e2c1bbd1228/864e152e374b5c9ca6d58ee953c5a6ed/dotnet-sdk-8.0.401-win-x64.exe dotnet-sdk-8.0.401-win-x64.exe
RUN dotnet-sdk-8.0.401-win-x64.exe /install /quiet /norestart

# Define the working directory - /app
WORKDIR /app

# Add the binary files from the latest release
COPY windows-core-binaries.zip .
RUN mkdir tmp_folder && \
    tar -xf windows-core-binaries.zip -C tmp_folder && \
    xcopy tmp_folder\bin\x64\Release_Core_Windows\net8.0\* . /e /i /h && \
    xcopy tmp_folder\* . && \
    del windows-core-binaries.zip && \
    rmdir /s /q tmp_folder

# Defining environment variables
RUN setx Path "%Path%;C:\app;C:\app\Native\Windows;C:\app\CADIntegration\bin"
ENV ANS_DSCO_REMOTE_PORT=50051
ENV ANS_DSCO_REMOTE_IP="0.0.0.0"
ENV LOG_LEVEL=2
ENV ANSYSLMD_LICENSE_FILE=""
ENV ANSYS_CI_INSTALL=C:/app/CADIntegration
ENV P_SCHEMA=C:/app/Schema
ENV ANSYSCL252_DIR=C:/app/licensingclient
ENV ANSYSCL261_DIR=C:/app/licensingclient

# Add container labels
LABEL org.opencontainers.image.authors="ANSYS Inc."
LABEL org.opencontainers.image.vendor="ANSYS Inc."

# Expose the Geometry service port
EXPOSE 50051

# Define the entrypoint for the Geometry service
# hadolint ignore=DL3025
ENTRYPOINT dotnet C:\app\Presentation.ApiServerCoreService.dll
