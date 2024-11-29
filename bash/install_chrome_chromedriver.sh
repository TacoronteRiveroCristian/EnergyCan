#!/bin/bash

# Descargar e instalar la última versión de Google Chrome
wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
sudo dpkg -i google-chrome-stable_current_amd64.deb
sudo apt --fix-broken install -y
rm google-chrome-stable_current_amd64.deb

# Obtener la versión instalada de Google Chrome
CHROME_VERSION=$(google-chrome --version | grep -oP '\d+\.\d+\.\d+\.\d+')
CHROME_MAJOR_VERSION=$(echo $CHROME_VERSION | cut -d '.' -f 1)

# Determinar la versión compatible de ChromeDriver
CHROMEDRIVER_VERSION=$(curl -sS "https://googlechromelabs.github.io/chrome-for-testing/last-known-good-versions-with-downloads.json" | \
    grep -oP '"version":\s*"'$CHROME_MAJOR_VERSION'\.\d+\.\d+\.\d+"' | \
    head -1 | \
    grep -oP '\d+\.\d+\.\d+\.\d+')

# Descargar e instalar ChromeDriver
wget -O /tmp/chromedriver_linux64.zip "https://edgedl.me.gvt1.com/edgedl/chrome/chrome-for-testing/$CHROMEDRIVER_VERSION/linux64/chromedriver-linux64.zip"
unzip /tmp/chromedriver_linux64.zip -d /tmp/
sudo mv /tmp/chromedriver-linux64/chromedriver /usr/local/bin/
sudo chmod +x /usr/local/bin/chromedriver
rm -rf /tmp/chromedriver_linux64.zip /tmp/chromedriver-linux64/

# Verificar las instalaciones
echo "Google Chrome versión: $(google-chrome --version)"
echo "ChromeDriver versión: $(chromedriver --version)"
