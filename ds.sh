#!/bin/sh

#IMG_NAME=gcr.io/$PROJECT_ID/sugah_dadeez_api:v1
IMG_NAME=sugah_dadeez_api

case "$1" in
  build)
    echo "building"
    docker build -t $IMG_NAME .
    if [[ ! -z $(docker images -f "dangling=true" -q) ]]
    then
      echo "Deleting dangling images"
      docker rmi $(docker images -f "dangling=true" -q)
    fi
    ;;

  kill)
    echo "killing"
    if [[ ! -z $(docker ps -aq) ]]
    then
      echo "Deleting running containers"
      docker kill $(docker ps -aq)
      docker rm $(docker ps -aq)
    fi
    ;;

  start)
    echo "starting"
    ./ds.sh kill
    ./ds.sh build
    docker run -d -p 8080:8080 $IMG_NAME
    ;;

  interact)
    echo "start interact"
    ./ds.sh kill
    ./ds.sh build
    docker run --rm -it $IMG_NAME bash
    ;;

  *)
    echo "Usage: "$1" {build|kill|start|interact}"
    exit 1
esac

exit 0
