#Jenkins confiurations 

Steps:
- Creating the Job:

 - Source Code Management
   - Git, to make Jenkins pull the repo before starting execution of the job

     - Repository URL, refrenciing the repo  url with the proper docker files and images 

     - Credentials,  have to be supplied in order to pull 

     - The branch, where to pull from syntax is */<branch name>

 - Build Triggers, to set when the job is executed 
   - build periodically, to allow building of the job on a periodic base , in this case @daily 


 - Build, The actual building of the docker, needs to be triggered using certain commands this is 
 done by using the docker command line syntax to run the build and also to clean up the containers after each start
 but the first lines should be commented in the first execution as there is nothing to cleanup 
 ```
docker rm -v $(docker ps -a -q -f status=exited)
docker rmi $(docker images -f "dangling=true" -q)
docker build js8/x86_64/2_ubuntu1510/
docker build js8/x86_64/3_ubuntu1510_python3/
docker build js8/x86_64/4_ubuntu1510_js8/
 ``` 