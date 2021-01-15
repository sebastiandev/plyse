# Build container with all the dependencies installed
# during the build process synopsys  blackduck hub detect is installed to scan all
# the open source dependencies and uploaded to the specified Blackduck URL
#
# Usage:
# export BLACKDUCK_PSWD="xxxxxx";
# docker build --file oss_scan/Dockerfile --tag="sentinel:oss_scan" --build-arg BLACKDUCK_PSWD=${BLACKDUCK_PSWD} .
# docker image rm sentinel:oss_scan

FROM python:3.7.6

ARG BLACKDUCK_URL="https://blackduck-hub.cudaops.com/"
ARG BLACKDUCK_USER="Sentinel_Service_Accounnt"
ARG BLACKDUCK_PROJECT="Sentinel"
ARG BLACKDUCK_VERSION="Latest"
ARG BLACKDUCK_PSWD

RUN mkdir /code
WORKDIR /code
ADD . /code/

# Synopsis blackduck hub detect can not parse github urls in requirements.txt
# hence commenting out github.com lines in requirement.txt
RUN sed -e '/github.com/s/^/#/g' -i requirements.txt

# Install all the dependencies (default-jre is for blackduck hub)
RUN apt-get update \
    && apt-get -q -y install default-jre \
    && python -m pip install --upgrade pip \
    && pip install virtualenv \
    && pip install -r requirements.txt \
    && python setup.py install --verbose

# Download and run Blackduck hub detect.
RUN curl -s -O -L -k https://detect.synopsys.com/detect.sh
RUN bash detect.sh \
    --blackduck.url=${BLACKDUCK_URL} \
    --blackduck.username=${BLACKDUCK_USER} --blackduck.password=${BLACKDUCK_PSWD} \
    --detect.project.name=${BLACKDUCK_PROJECT} --detect.project.version.name=${BLACKDUCK_VERSION} \
    --detect.detector.search.depth=3 \
    --detect.pip.requirements.path=/code/requirements.txt \
    --logging.level.com.synopsys.integration=DEBUG
