# Base image
FROM resin/raspberrypi-python:latest

# Set the maintainer
MAINTAINER Carlos Labrado

# Install packages for papirus
RUN apt-get update && apt-get install -y \
  git \
  bc \
  i2c-tools \
  fonts-freefont-ttf\
  libfuse-dev \
  python3 \
  python3-pil \
  python3-smbus \
  python3-dateutil \
  python3-rpi.gpio \
  && rm -rf /var/lib/apt/lists/*

RUN git clone --depth=1 https://github.com/PiSupply/PaPiRus.git /build/papirus
RUN git clone https://github.com/repaper/gratis.git /build/gratis

# Configure gratis
WORKDIR /build/gratis
RUN make rpi EPD_IO=epd_io.h PANEL_VERSION='V231_G2'
RUN make rpi-install EPD_IO=epd_io.h PANEL_VERSION='V231_G2'
RUN systemctl enable epd-fuse.service

# Install
WORKDIR /build/papirus
RUN python3 setup.py install

# Copy everything into the container
COPY . ./

# Systemd please
ENV INITSYSTEM on

# Start application
CMD ["bash", "start.sh"]

