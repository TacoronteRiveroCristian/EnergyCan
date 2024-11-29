FROM cristiantr/dev_container_image:latest

ARG GITHUB_USERNAME
ARG GITHUB_GMAIL
ARG WORKDIR="/workspaces/EnergyCan"

# Establecer variables de entorno
ENV PYTHONPATH=${PYTHONPATH}:${WORKDIR}
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
    libasound2 \
    libxi6 \
    libgconf-2-4 \
    libxrender1 \
    libxtst6 \
    libxss1 \
    libnss3 \
    libatk1.0-0 \
    libvulkan1 \
    fonts-liberation \
    libappindicator3-1 \
    xdg-utils \
    software-properties-common \
    dos2unix \
    && rm -rf /var/lib/apt/lists/*

# Configurar la zona horaria de Canarias
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ | tee /etc/timezone

# Crear usuario sin privilegios
RUN useradd -ms /bin/bash appuser

# Configurar credenciales de GitHub
RUN git config --global user.name "${GITHUB_USERNAME}" && \
    git config --global user.email "${GITHUB_GMAIL}"

# Copiar archivos y configurar permisos
COPY . ${WORKDIR}
RUN chown -R appuser:appuser ${WORKDIR} && \
    chmod -R 770 ${WORKDIR} && \
    chmod 600 ${WORKDIR}/.env

# Copiar script para Instalar Chrome y chromedriver
# Al script se le ejecuta el comando dos2unix para eliminar caracteres de Windows
COPY ./bash/install_chrome_chromedriver.sh /usr/local/bin/
RUN chmod +x /usr/local/bin/install_chrome_chromedriver.sh && \
    dos2unix /usr/local/bin/install_chrome_chromedriver.sh
RUN install_chrome_chromedriver.sh

# Cambiar al usuario sin privilegios
USER appuser

# Instalar dependencias
COPY requirements.txt requirements.txt
RUN pip install --upgrade pip && pip install -r requirements.txt

# Comando de arranque
CMD ["/bin/bash"]
