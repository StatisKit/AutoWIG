set +x
set -e

DEFAULT_DOCKER_TAGS="14.04 16.04"

if [[ -z $DOCKER_TAGS ]]; then
    DOCKER_TAGS=$DEFAULT_DOCKER_TAGS;
else
    echo "Tags to build: "$DOCKER_TAGS;
fi

if [[ -z $DOCKER_CHANNEL ]]; then
    DOCKER_CHANNEL="statiskit";
else
    echo "Using docker channel: "$DOCKER_CHANNEL;
fi

set -x

for DOCKER_TAG in $DOCKER_TAGS; do
    docker pull statiskit/ubuntu:$DOCKER_TAG
    docker tag statiskit/ubuntu:$DOCKER_TAG statiskit/ubuntu
    docker build -t $DOCKER_CHANNEL/autowig:$DOCKER_TAG .
done

set +xe