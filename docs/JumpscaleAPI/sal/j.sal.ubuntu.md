<!-- toc -->
## j.sal.ubuntu

- /opt/jumpscale8/lib/JumpScale/sal/ubuntu/Ubuntu.py
- Properties
    - logger
    - installedPackageNames

### Methods

#### apt_find1_installed(*packagename*) 

#### apt_find_all(*packagename*) 

#### apt_find_installed(*packagename*) 

#### apt_get(*name*) 

#### apt_get_cache_keys(**) 

#### apt_get_installed(**) 

#### apt_init(**) 

#### apt_install(*packagename*) 

#### apt_install_check(*packagenames, cmdname*) 

```
@param packagenames is name or array of names of ubuntu package to install e.g. curl
@param cmdname is cmd to check e.g. curl

```

#### apt_install_version(*packageName, version*) 

```
Installs a specific version of an ubuntu package.

@param packageName: name of the package
@type packageName: str

@param version: version of the package
@type version: str

```

#### apt_sources_list(**) 

#### apt_sources_uri_add(*url*) 

#### apt_sources_uri_change(*newuri*) 

#### apt_update(*force=True*) 

#### apt_upgrade(*force=True*) 

#### check(*die=True*) 

```
check if ubuntu or mint (which is based on ubuntu)

```

#### checkroot(**) 

#### deb_download_install(*url, removeDownloaded, minspeed=20*) 

```
will download to tmp if not there yet
will then install

```

#### deb_install(*path, installDeps=True*) 

#### get_installed_package_names(**) 

#### is_pkg_installed(*pkg*) 

#### pkg_list(*pkgname, regex=''*) 

```
list files of dpkg
if regex used only output the ones who are matching regex

```

#### pkg_remove(*packagename*) 

#### service_disable_start_boot(*servicename*) 

#### service_enable_start_boot(*servicename*) 

#### service_install(*servicename, daemonpath, args='', respawn=True, pwd, env, reload=True*) 

#### service_restart(*servicename*) 

#### service_start(*servicename*) 

#### service_status(*servicename*) 

#### service_stop(*servicename*) 

#### service_uninstall(*servicename*) 

#### sshkeys_generate(*passphrase='', type='rsa', overwrite, path='/root/.ssh/id_rsa'*) 

#### version_get(**) 

```
returns codename,descr,id,release
known ids" raring, linuxmint

```

#### whoami(**) 

