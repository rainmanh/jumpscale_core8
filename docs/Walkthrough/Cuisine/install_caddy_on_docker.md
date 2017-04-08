# Installing Caddy using Cuisine

This is a continuation on the walkthrough documentation on [Working with Docker using the Docker SAL](../SAL/Docker.md).  

Now that you have created the Docker container through JumpScale you have the object wrapper of that container which includes a Cuisine property. This property is a Cuisine remote executor from your current host onto the container. This allows you to manage the machine, execute commands, and most importantly build and install services.  

To install Caddy through the Cuisine object is done in 3 steps:
* Step 1: Get the Docker container up and running
* Step 2: Get the Cuisine remote executor property
* Step 3: Install Caddy


<a id="step-1"></a>
## Step 1: Get the Docker container up and running
To get the Docker container up and running we run the same commands as before, but this time with different parameters:

```
container1 = j.sal.docker.create( name="container1", myinit=False,  base="jumpscale/ubuntu1604" )
```


<a id="step-3"></a>
## Step 2: Get the Cuisine remote executor property
A neat feature which almost all the wrapper objects provide, is that any virtual machine or Docker container created through JumpScale will automatically have a remote executor property (`cuisine`). This allows us to run, install, and manage any node created through Cuisine.

```
cuisine = conatainer1.cuisine
```  


<a id="step-3"></a>
## Step 3: Install Caddy
As stated above Cuisine has the ability to install services. In this case for example we want to install Caddy.

The install method of Caddy takes 5 optional parameters:

 - **ssl**, this tells the firewall to allow port 443 as well as ports 80 and 22 to support SSL

 - **start**, if True, the service will be added to the default process manager and start it, after installing the service  

 - **dns**, default address to run Caddy on

 - **reset**, if True this will install even if the service is already installed

So to run Caddy:  

```
cuisine.apps.caddy.install()
```

Now you have Caddy running on the Docker container created through JumpScale.

```
!!!
title = "Install Caddy On Docker"
date = "2017-04-08"
tags = []
```
