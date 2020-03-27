ARG WORKFLOWS_INSTALL=/home/workflows

FROM alpine AS workflows

RUN apk update \
 && apk add \
      unzip \
      curl
ENV RETROPATH_VERSION 9
ENV RETROPATH_URL https://myexperiment.org/workflows/4987/download/RetroPath2.0_-_a_retrosynthesis_workflow_with_tutorial_and_example_data-v${RETROPATH_VERSION}.zip
# version 8
# ENV RETROPATH_SHA256 7d81b42f6eddad2841b67c32eeaf66cb93227d6c2542938251be6b77b49c0716
# version 9
ENV RETROPATH_SHA256 79069d042df728a4c159828c8f4630efe1b6bb1d0f254962e5f40298be56a7c4
RUN echo "$RETROPATH_SHA256  RetroPath2_0.zip" > RetroPath2_0.zip.sha256
RUN curl -L -o RetroPath2_0.zip $RETROPATH_URL \
 && sha256sum RetroPath2_0.zip \
 && sha256sum -c RetroPath2_0.zip.sha256
ARG WORKFLOWS_INSTALL
RUN mkdir -p $WORKFLOWS_INSTALL \
 && unzip -qq RetroPath2_0.zip RetroPath2.0/* -d $WORKFLOWS_INSTALL \
 && mv $WORKFLOWS_INSTALL/RetroPath2.0 $WORKFLOWS_INSTALL/$RETROPATH_VERSION

# # Copy retrorules
# ENV RETRORULES_URL https://retrorules.org/dl/preparsed/rr02/rp2/hs
# RUN wget --quiet $RETRORULES_URL -O rules_rall_rp2.tar.gz \
#  && tar -C /home/src xzf rules_rall_rp2.tar.gz retrorules_rr02_rp2_hs/retrorules_rr02_rp2_flat_retro.csv


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

# Copy workflows
ARG WORKFLOWS_INSTALL
COPY --from=workflows $WORKFLOWS_INSTALL /home/workflows

WORKDIR /home/src
# Copy code
COPY src .

#ENTRYPOINT python3 RetroPath2.py
