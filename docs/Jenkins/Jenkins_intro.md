# Jenkins configurations and files 

*The Project was [setup](Jenkins_config.md) on jenkins to test*: 

- The building of the required docker images for a node with jumpscale
each depending on the other. [Docker_builds](Docker_builds.md).

- The testing of jumpscale cuisine's build and start methods. This is 
done  by adjusting a docker file contained in the final image build.This allows it to run the 
j.cuisine.local.builder.all() method when building.