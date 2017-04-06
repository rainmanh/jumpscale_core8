# Installing the JumpScale On Docker Container for a branch

The Ubuntu Docker container is available on [Docker Hub](https://hub.docker.com/): [jumpscale/ubuntu1604_js_development](https://hub.docker.com/r/jumpscale/ubuntu1604).

First make sure you have a Docker Installed on your machine

Download the **Ubuntu Docker image**:

```
docker pull jumpscale/ubuntu1604
```

Run a Docker container using the image, and start an interactive session:

```
docker run -t -i --name=js jumpscale/ubuntu1604
```

```
export TMPDIR=/tmp
cd $TMPDIR
rm -f install.sh
export JSBRANCH="8.2.0"
curl -k https://raw.githubusercontent.com/Jumpscale/jumpscale_core8/$JSBRANCH/install/install.sh?$RANDOM > install.sh
bash install.sh
```
