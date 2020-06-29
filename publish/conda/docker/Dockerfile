FROM continuumio/miniconda3

# install requirements
RUN conda install -y  \
      anaconda-client \
      conda-build     \
      conda-verify    \
 && conda config --set anaconda_upload no

# Make this once so that no need to download when run later on
ARG PKG
RUN conda skeleton pypi ${PKG} \
 && conda build ${PKG} \
 && rm -rf ${PKG} /opt/conda/conda-bld/linux-64/${PKG}*
