FROM ubuntu:18.04

ENV DOWNLOAD_URL http://download.knime.org/analytics-platform/linux/knime_3.6.2.linux.gtk.x86_64.tar.gz
ENV INSTALLATION_DIR /usr/local
ENV KNIME_DIR $INSTALLATION_DIR/knime
ENV HOME_DIR /home/knime

# Install everything
# HACK: Install tzdata at the beginning to not trigger an interactive dialog later on
RUN apt-get update \
    && apt-get install -y software-properties-common curl tzdata \
    && apt-get update \
    && apt-get install -y \
         openjdk-8-jdk libgtk2.0-0 libxtst6 \
         libwebkitgtk-3.0-0 \
         python python-dev python-pip \
         r-base r-recommended wget

# Download KNIME
RUN curl -L "$DOWNLOAD_URL" | tar vxz -C $INSTALLATION_DIR \
    && mv $INSTALLATION_DIR/knime_* $INSTALLATION_DIR/knime

# Clean up
RUN apt-get --purge autoremove -y software-properties-common curl \
 && apt-get clean

# Install pandas and protobuf so KNIME can communicate with Python
RUN pip install pandas && pip install protobuf

# Install Rserver so KNIME can communicate with R
RUN R -e 'install.packages(c("Rserve"), repos="http://cran.rstudio.com/")'

# Build argument for the workflow directory
ONBUILD ARG WORKFLOW_DIR="workflow/"
# Build argument for additional update sites
ONBUILD ARG UPDATE_SITES

# Create workflow directory and copy from host
ONBUILD RUN mkdir -p /payload
ONBUILD COPY $WORKFLOW_DIR /payload/workflow

# Create metadata directory
ONBUILD RUN mkdir -p /payload/meta

# Copy necessary scripts onto the image
COPY docker_conf/getversion.py /scripts/getversion.py
COPY docker_conf/listvariables.py /scripts/listvariables.py
COPY docker_conf/listplugins.py /scripts/listplugins.py
COPY docker_conf/run.sh /scripts/run.sh

# Let anyone run the workflow
RUN chmod +x /scripts/run.sh

# Add KNIME update site and trusted community update site that fit the version the workflow was created with
ONBUILD RUN full_version=$(python /scripts/getversion.py /payload/workflow/) \
&& version=$(python /scripts/getversion.py /payload/workflow/ | awk '{split($0,a,"."); print a[1]"."a[2]}') \
&& echo "http://update.knime.org/analytics-platform/$version" >> /payload/meta/updatesites \
&& echo "http://update.knime.org/community-contributions/trusted/$version" >> /payload/meta/updatesites \
# Add user provided update sites
&& echo $UPDATE_SITES | tr ',' '\n' >> /payload/meta/updatesites

# Save the workflow's variables in a file
ONBUILD RUN find /payload/workflow -name settings.xml -exec python /scripts/listplugins.py {} \; | sort -u | awk '!a[$0]++' > /payload/meta/features

ONBUILD RUN python /scripts/listvariables.py /payload/workflow

# Install required features
ONBUILD RUN "$KNIME_DIR/knime" -application org.eclipse.equinox.p2.director \
-r "$(cat /payload/meta/updatesites | tr '\n' ',' | sed 's/,*$//' | sed 's/^,*//')" \
-p2.arch x86_64 \
-profileProperties org.eclipse.update.install.features=true \
-i "$(cat /payload/meta/features | tr '\n' ',' | sed 's/,*$//' | sed 's/^,*//')" \
-p KNIMEProfile \
-nosplash

# Cleanup
ONBUILD RUN rm /scripts/getversion.py && rm /scripts/listvariables.py && rm /scripts/listplugins.py

#FROM ibisba/knime-base:3.6.2

############################### JOAN rpData ##############################

#stable version
#ENV RETROPATH_VERSION 8
#new version
ENV RETROPATH_VERSION 9
ENV RETROPATH_URL https://myexperiment.org/workflows/4987/download/RetroPath2.0_-_a_retrosynthesis_workflow_with_tutorial_and_example_data-v${RETROPATH_VERSION}.zip
# NOTE: Update sha256sum for each release
#TODO: update the SHA356 for the new version of RetroPath2
#version 8
#ENV RETROPATH_SHA256 7d81b42f6eddad2841b67c32eeaf66cb93227d6c2542938251be6b77b49c0716
#version 9
ENV RETROPATH_SHA256 79069d042df728a4c159828c8f4630efe1b6bb1d0f254962e5f40298be56a7c4

RUN apt-get --quiet update && \
	apt-get --quiet --yes dist-upgrade && \
	apt-get --quiet --yes install curl

# Download RetroPath2.0
WORKDIR /home/
RUN echo "$RETROPATH_SHA256 RetroPath2_0.zip" > RetroPath2_0.zip.sha256
RUN cat RetroPath2_0.zip.sha256
RUN echo Downloading $RETROPATH_URL
RUN curl -v -L -o RetroPath2_0.zip $RETROPATH_URL && sha256sum RetroPath2_0.zip && sha256sum -c RetroPath2_0.zip.sha256
RUN unzip RetroPath2_0.zip && mv RetroPath2.0/* /home/
RUN rm RetroPath2_0.zip

#####################################################################

#install the additional packages required for running retropath KNIME workflow
RUN /usr/local/knime/knime -application org.eclipse.equinox.p2.director -nosplash -consolelog \
-r http://update.knime.org/community-contributions/trunk,\
http://update.knime.com/analytics-platform/3.6,\
http://update.knime.com/community-contributions/trusted/3.6 \
-i org.knime.features.chem.types.feature.group,\
org.knime.features.datageneration.feature.group,\
jp.co.infocom.cheminfo.marvin.feature.feature.group,\
org.knime.features.python.feature.group,\
org.rdkit.knime.feature.feature.group \
-bundlepool /usr/local/knime/ -d /usr/local/knime/
