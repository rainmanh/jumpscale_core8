# Ubuntu

Ubuntu SAL helps to manage the packages, services in ubuntu > 14
 
* You can Access it via
```
j.sal.ubuntu
```

## Service Management
* You can control the installation/removal of services via `service_install`, `service_remove`
* You can control if it's enabled/disabled at boot  `service_enable_start_boot`, `service_disable_start_boot`

```python
service_install(servicename, daemonpath, args='', respawn=True, pwd=None,env=None,reload=True)
service_uninstall(servicename)
service_enable_start_boot(servicename)
service_disable_start_boot(servicename)
```
* You can control the service life cycle (Start, Stop, Restart, Status) via `service_start`, `service_stop`, `service_restart`, `service_status`
```python
  service_start(servicename)
  service_stop(servicename)
  service_restart(servicename)
  service_status(servicename)
```

## Package management
 `j.sal.ubuntu` helps with package management:
 
* `apt_install` to install a new package.
* `apt_install_version` to install a specific version of a package.
* `pkg_remove` to remove a certain package.
* `pkg_list` to list all files of a package.
* `get_installed_package_names` to get a list of installed packages.
* `is_pkg_installed` to find if a certain package is already installed on the system. 
* `apt_update` to update your packages list.
* `apt_upgrade` to upgrade your packages.

## Other helpers
* `sshkeys_generate` Generate SSH-keys
```python
sshkeys_generate(passphrase='', type="rsa", overwrite=False, path="/root/.ssh/id_rsa"):
```
* `checkroot` asserting the current user is root.
* `whoami` to print effective user id.
*  `version_get` : returns a tuple of `CODENAME`, `Description`, `ID`, `RELEASE` 
```python
j.sal.ubuntu.version_get()
('xenial', 'Ubuntu 16.04 LTS', 'ubuntu', '16.04')

```
