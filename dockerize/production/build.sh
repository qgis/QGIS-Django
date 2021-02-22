#!/usr/bin/env bash
if [ -z "$REPO_NAME" ]; then
	REPO_NAME=kartoza
fi

if [ -z "$IMAGE_NAME" ]; then
	IMAGE_NAME=qgis-plugins-uwsgi
fi

if [ -z "$TAG_NAME" ]; then
	TAG_NAME=latest
fi

if [ -z "$BUILD_ARGS" ]; then
	BUILD_ARGS="--pull --no-cache"
fi

# Build Args Environment

if [ -z "$BRANCH_TAG" ]; then
	BRANCH_TAG=dockerize
fi

echo "BRANCH_TAG: ${BRANCH_TAG}"
echo "Build: $REPO_NAME/$IMAGE_NAME:$TAG_NAME"

docker build -t ${REPO_NAME}/${IMAGE_NAME} \
	--build-arg BRANCH_TAG=${BRANCH_TAG} \
	${BUILD_ARGS} .
docker tag ${REPO_NAME}/${IMAGE_NAME}:latest ${REPO_NAME}/${IMAGE_NAME}:${TAG_NAME}
docker push ${REPO_NAME}/${IMAGE_NAME}:${TAG_NAME}
