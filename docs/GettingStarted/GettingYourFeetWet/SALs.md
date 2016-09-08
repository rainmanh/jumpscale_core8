# SALs

SALs are system abstraction layers. They provide a unified interface to system operations. You can use the different available SALs to create powerful scripts that can monitor and manage your services.

<!-- @todo: Provide simple example of how to use SALS, just to introduce the concept   -->

 - For example you can use SALs to check if the .ssh directory exists and create it if not:
    ```
    if not j.sal.fs.exists("/root/.ssh"):
        j.sal.createDir("/root/.ssh")
    ```

For a detailed discussion of SALs go to the [SALs documentation](../../SAL/SAL.md).
