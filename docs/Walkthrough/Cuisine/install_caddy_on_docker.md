##__Installing Caddy through cuisine__

This is a continuation on the previous example of creating a docker container using jumpscale , start with that from [here]().  
Now that you have created the docker container through jumpscale you have , the object wrapper of that container
which includes a cuisine property. This property is a cuisine remote executor from your current host onto the container.
This allows the you to manage the machine, execute commands, and most importantly build and install services.

to install caddy through the cuisine object:  
##__- Recap__
<!-- #todo add recap portion whne docker section is created  -->
So in the previous section a cuisine container object was created lets call that object container1.

##__- Step One__
A neat feature wich almost all our wrapper objects provide, is that any VM or docker created through jumpscale will
automatically have a remote executor (cuisine) to the instance. This allows us to run, install, or manage any node created through our framework.  
In this case we will set it to a variable called conatainer1_cuisine it will be available inside conatainer1 at :
```
container1_cuisine = conatainer1.cuisine
```  

##__- Step Two__
As stated before cuisine has the ability to install services, in this case for example we want to install caddy.
the install method of caddy has 5 parameters :
 - **ssl**, this tells the fire wall to allow port 443 as well as 80 and 22 to support ssl.

 - **start**, after installing the service this option is true will add the service to the default proccess manager an strart it .  

 - **dns**,  default address to run caddy on.

 - **reset**, if True this will install even if the service is already installed.
to do that we run :  
```
conatainer1_cuisine.apps.caddy.install()
```

###Now you have caddy running on the docker created through jumpscale.
