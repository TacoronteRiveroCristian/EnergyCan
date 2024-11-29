FROM cristiantr/dev_container_image:latest

ARG GITHUB_USERNAME
ARG GITHUB_GMAIL
ARG WORKDIR="/workspaces/EnergyCan"

# Establecer variables de entorno
ENV PYTHONPATH=${PYTHONPATH:-}:${WORKDIR}
ENV TZ=Atlantic/Canary
ENV WORKDIR=${WORKDIR}

# Cambiar directorio de trabajo
WORKDIR ${WORKDIR}

# Crear usuario sin privilegios
USER root

# Instalar dependencias generales y Chrome
RUN apt-get update && \
    apt-get install -y \
    wget \
    curl \
    unzip \
    gnupg \
    build-essential \
    pkg-config \
    libcairo2 \
    libcairo2-dev \
    python3-cairo \
    python3-pip \
    python3-dev \
    libgirepository1.0-dev \
    gir1.2-gtk-3.0 \
    libatk1.0-0 \
    libasound2 \
    libgbm1 \
    libnspr4 \
    libnss3 \
    libvulkan1 \
    locales \
    fonts-liberation \
    libappindicator3-1 \
    xdg-utils \
    software-properties-common \
    dos2unix \
    && rm -rf /var/lib/apt/lists/*

# Configurar la zona horaria de Canarias
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ | tee /etc/timezone

# Crear usuario sin privilegios en el caso de que no exista
RUN id -u dev_container || useradd -ms /bin/bash dev_container

# Configurar credenciales de GitHub
RUN git config --global user.name "${GITHUB_USERNAME}" && \
    git config --global user.email "${GITHUB_GMAIL}"

# Copiar archivos y configurar permisos
COPY . ${WORKDIR}
RUN chown -R dev_container:dev_container ${WORKDIR} && \
    chmod -R 770 ${WORKDIR} && \
    chmod 600 ${WORKDIR}/.env

# Copiar script para Instalar Chrome y chromedrivers
COPY ./bash/install_chrome_chromedriver.sh /usr/local/bin/
RUN chmod +x /usr/local/bin/install_chrome_chromedriver.sh && \
    dos2unix /usr/local/bin/install_chrome_chromedriver.sh

# Cambiar al usuario sin privilegios
USER dev_container

# Instalar Chrome y chromedriver
RUN /usr/local/bin/install_chrome_chromedriver.sh

# Instalar dependencias
COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir --upgrade pip && pip install --no-cache-dir -r requirements.txt

# Comando de arranque
CMD ["/bin/bash"]
