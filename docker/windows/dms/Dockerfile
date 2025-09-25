# hadolint shell = cmd.exe
#
# Geometry service Windows-based Dockerfile
#
# Based on mcr.microsoft.com/dotnet/framework/runtime:4.7.2-windowsservercore-ltsc2019
FROM mcr.microsoft.com/dotnet/framework/runtime:4.7.2-windowsservercore-ltsc2019

# Define the working directory - /temp
WORKDIR /temp

# Download Microsoft Visual C++ Redistributable x64
ADD https://aka.ms/vs/17/release/VC_redist.x64.exe VC_redist.x64.exe
RUN VC_redist.x64.exe /install /quiet /norestart

# Define the working directory - /app
WORKDIR /app

# Add the binary files from the latest release
COPY windows-dms-binaries.zip .
RUN mkdir tmp_folder && \
    tar -xf windows-dms-binaries.zip -C tmp_folder && \
    xcopy tmp_folder\bin\x64\Release_Headless\net472\* . /e /i /h && \
    xcopy tmp_folder\* . && \
    del windows-dms-binaries.zip && \
    rmdir /s /q tmp_folder

# Defining environment variables
ENV LICENSE_SERVER=""
ENV SERVER_ENDPOINT="50051@0.0.0.0"
ENV ENABLE_TRACE=0
ENV LOG_LEVEL=2
ENV AWP_ROOT252=C:/app/unified

# Add container labels
LABEL org.opencontainers.image.authors="ANSYS Inc."
LABEL org.opencontainers.image.vendor="ANSYS Inc."

# Expose the Geometry service port
EXPOSE 50051

# Define the entrypoint for the Geometry service
ENTRYPOINT ["Presentation.ApiServerDMS.exe"]
