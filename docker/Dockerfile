FROM brsynth/knime

RUN apt-get update \
 && apt-get install -y \
      python3

# For KNIME
RUN ln -sf /usr/bin/python3 /usr/bin/python

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

# Copy workflow
RUN apt-get install -y unzip
ENV RETROPATH_VERSION 9
ENV RETROPATH_URL https://myexperiment.org/workflows/4987/download/RetroPath2.0_-_a_retrosynthesis_workflow_with_tutorial_and_example_data-v${RETROPATH_VERSION}.zip
# version 8
# ENV RETROPATH_SHA256 7d81b42f6eddad2841b67c32eeaf66cb93227d6c2542938251be6b77b49c0716
# version 9
ENV RETROPATH_SHA256 79069d042df728a4c159828c8f4630efe1b6bb1d0f254962e5f40298be56a7c4
WORKDIR /home/workflows
RUN echo "$RETROPATH_SHA256 /tmp/RetroPath2_0.zip" > /tmp/RetroPath2_0.zip.sha256
RUN cat /tmp/RetroPath2_0.zip.sha256
RUN echo Downloading $RETROPATH_URL
RUN curl -v -L -o /tmp/RetroPath2_0.zip $RETROPATH_URL && sha256sum /tmp/RetroPath2_0.zip && sha256sum -c /tmp/RetroPath2_0.zip.sha256
RUN unzip /tmp/RetroPath2_0.zip RetroPath2.0/* -d . && mv RetroPath2.0 $RETROPATH_VERSION
RUN rm -f /tmp/RetroPath2_0.zip*

WORKDIR /home/src
# Copy code
COPY src .

ENTRYPOINT python3 RetroPath2.py
