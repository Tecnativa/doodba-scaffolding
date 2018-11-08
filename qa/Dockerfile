ARG CI_IMAGE
ARG CI_PIPELINE_ID
FROM $CI_IMAGE:$CI_PIPELINE_ID

USER root

ENV ADDON_CATEGORIES="--private" \
    CONTAINER_PREFIX="ci" \
    LANG=C.UTF-8 \
    LINT_DISABLE="manifest-required-author" \
    LINT_ENABLE="" \
    QA_VOLUME="" \
    REPOS_FILE="odoo/custom/src/repos.yaml" \
    SHARED_NETWORK=inverseproxy_shared \
    VERBOSE=0

RUN pip install --no-cache-dir coverage click flake8 pylint-odoo \
        && npm install --loglevel error eslint \
        && mkdir -p /qa/artifacts \
        && chown -R 1000:1000 /qa/artifacts \
        && chmod a=rwX /qa/artifacts \
        && git clone --depth 1 https://github.com/OCA/maintainer-quality-tools.git /qa/mqt

COPY --chown=root:1000 test-scripts /qa/insider

WORKDIR /usr/local/bin

RUN for f in $(ls /qa/insider); do ln -s /qa/insider/$f $f; done; sync

USER odoo

WORKDIR /opt/odoo

ENTRYPOINT ["/bin/bash"]
