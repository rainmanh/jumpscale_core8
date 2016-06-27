##*The Docker images being Tested are*:

- The  [2_ubuntu1604](https://github.com/Jumpscale/dockers/tree/build_test/js8/x86_64/2_ubuntu1604) a fusion image of ubuntu.15.10 with very basic utilities installed.

 - sets up some useful utilites such as tmux , a processmanager , and others by editing 
 in .sh files that are run throught the docker file which is used to build the image. 

 - sets up some important configurations , most importantly enables and configures the image 
 for ssh.

- The [3_ubuntu1604_python3](https://github.com/Jumpscale/dockers/tree/build_test/js8/x86_64/3_ubuntu1604_python3) an image build on the ,, by refrencing it in the dockerfile using FROM <imagename>. 
This image is created to build python3.5 and setup its enviroment. In addition, to adding all the 
dependencies required:

 - all the python modules needed for jumpscale to funcitons properly are added using
 the same method as the previous build, through .sh files  and then running them in docker file
 at build.

 - before that, all the system packages and more elaborate utilities needed are installed 
 and configured.This includes pip3, git and other required packages.

- The [4_ubuntu1604_js8](https://github.com/Jumpscale/dockers/tree/build_test/js8/x86_64/4_ubuntu1604_js8) the final image:

 - this installs jumpscale, configures it and sets up the enviroment varaibles and other relevant 
 system configurations for jumpscale to work properly. 

 - this also, runs two important commands
    - first cleanning the cache to allow the cuisine to run properly.
    ```
    RUN js 'j.core.db.flushall()'
    ``` 
    - second the actual running of the command method the builds and starts the cuisine methods 
    ```
    RUN js 'j.tools.cuisine.local.builder.all(start=True)'
    ```

```

```