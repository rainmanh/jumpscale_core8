# Cuisine

Cuisine makes it easy to automate server installations and create configuration recipes by wrapping common administrative tasks, such as installing packages and creating users and groups, in Python functions.
To use cuisine you first need to get an executor that can be local or remote
1. to get local executor
```
executor = j.tools.executor.getLocal()
cuisine = j.tools.cuisine.get(executor)
```
2. To get remote executor
```
executor = j.tools.executor.getSSHBased(addr, port, login, passwd)
cuisine = j.tools.cuisine.get(executor)
```
## Examples to use cuisine

1. To print the environment variables on a remote machine
```
executor = j.tools.executor.getSSHBased(addr, port, login, passwd)
cuisine = j.tools.cuisine.get(executor)
print (cuisine.bash.environment)
```
2. To install mongodb
```
cuisine.apps.mongodb.install
```
3. To copy file
```
cuisine.core.file_copy("/opt/code/file1", "/opt/code/file2")
```

For more information in Cuisine check the [Cuisine documentation](../../Cuisine/Cuisine.md).
