#Jenkins confiurations 

Steps:
- **Creating the Job**:

 - **Source Code Management**:
   - **Git**, to make Jenkins pull the repo before starting execution of the job

     - **Repository URL**, refrenciing the repo  url with the proper docker files and images 

     - **Credentials**,  have to be supplied in order to pull 

     - **The branch**, where to pull from syntax is `<branch name`>


 - **Build Triggers**, to set when the job is executed 
   - **build periodically**, to allow building of the job on a periodic base , syntax such as  @daily, @weekly are accepted 
   - **build after other projects are built**, specify next build , build only if build is stable 


 - **Build**, The actual building of the docker, needs to be triggered using certain commands this is 
 done by using the docker command line syntax to run inside an bash script which is run on the jenkins machine
 for example the JS8_ubuntu1604_buildall project uses this for its build :  
 ```
docker exec builder bash -c " docker run -d -i -t --privileged --name=buildall jumpscale/ubuntu1604_js8 'sbin/my_init' "

docker exec builder bash -c " docker exec buildall bash -c \" export LC_ALL=C.UTF-8; export LANG=C.UTF-8; js 'j.core.db.flushall(); j.tools.cuisine.local.builder.all(start=True)' \" "
 ``` 
 - **post build**, post build execute script is usually used for clean up , remaining containers should be removed 
 unless the container is needed in downstream projects later on , to avoid build fails later on.
 to clean up use :  
   ```docker rm -fv <container_name> ```  