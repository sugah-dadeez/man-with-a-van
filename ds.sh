#!/bin/sh

case "$1" in
  build)
    echo "building"
    docker build -t cs5357 .
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
    docker run -d -p 8080:8080 cs5357
    ;;

  interact)
    echo "start interact"
    ./ds.sh kill
    ./ds.sh build
    docker run --rm -it cs5357 bash
    ;;

  *)
    echo "Usage: "$1" {build|kill|start|interact}"
    exit 1
esac

exit 0
