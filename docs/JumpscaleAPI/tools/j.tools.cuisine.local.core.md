<!-- toc -->
## j.tools.cuisine.local.core

- /opt/jumpscale8/lib/JumpScale/tools/cuisine/CuisineCore.py
- Properties
    - cd
    - cuisine
    - logger
    - sudomode

### Methods

#### args_replace(*text*) 

```
replace following args (when jumpscale installed it will take the args from there)
dirs:
- $base
- $appDir
- $tmplsDir
- $varDir/
- $binDir
- $codeDir
- $cfgDir
- $homeDir
- $jsLibDir
- $libDir
- $logDir
- $pidDir
- $tmpDir/
system
- $hostname

```

#### command_check(*command*) 

```
Tests if the given command is available on the system.

```

#### command_ensure(*command, package*) 

```
Ensures that the given command is present, if not installs the
package with the given name, which is the same as the command by
default.

```

#### command_location(*command*) 

```
return location of cmd

```

#### createDir(*location, recursive=True, mode, owner, group*) 

```
Ensures that there is a remote directory at the given location,
optionally updating its mode / owner / group.

If we are not updating the owner / group then this can be done as a single
ssh call, so use that method, otherwise set owner / group after creation.

```

#### dir_attribs(*location, mode, owner, group, recursive, showout*) 

```
Updates the mode / owner / group for the given remote directory.

```

#### dir_ensure(*location, recursive=True, mode, owner, group*) 

```
Ensures that there is a remote directory at the given location,
optionally updating its mode / owner / group.

If we are not updating the owner / group then this can be done as a single
ssh call, so use that method, otherwise set owner / group after creation.

```

#### dir_exists(*location*) 

```
Tells if there is a remote directory at the given location.

```

#### dir_remove(*location, recursive=True*) 

```
Removes a directory

```

#### download(*source, dest=''*) 

```
@param source is on remote host (on the ssh node)
@param dest is on local (where we run the cuisine)
will replace $varDir, $codeDir, ...
- in source but then using cuisine.core.args_replace(dest) (so for cuisine host)
- in dest using j.dirs.replaceTxtDirVars (is for local cuisine)

@param dest, if empty then will be same as source very usefull when using e.g. $codeDir

```

#### execute_bash(*script, die=True, profile, tmux, args_replace=True, showout=True*) 

#### execute_jumpscript(*script, die=True, profile, tmux, args_replace=True, showout=True*) 

```
execute a jumpscript(script as content) in a remote tmux command, the stdout will be
    returned

```

#### execute_python(*script, die=True, profile, tmux, args_replace=True, showout=True*) 

#### execute_script(*content, die=True, profile, interpreter='bash', tmux=True, args_replace=True, showout=True*) 

```
generic exection of script, default interpreter is bash

```

#### file_append(*location, content, mode, owner, group*) 

```
Appends the given content to the remote file at the given
location, optionally updating its mode / owner / group.

```

#### file_attribs(*location, mode, owner, group*) 

```
Updates the mode/owner/group for the remote file at the given
location.

```

#### file_attribs_get(*location*) 

```
Return mode, owner, and group for remote path.
Return mode, owner, and group if remote path exists, 'None'
otherwise.

```

#### file_backup(*location, suffix='.orig', once*) 

```
Backups the file at the given location in the same directory, appending
the given suffix. If `once` is True, then the backup will be skipped if
there is already a backup file.

```

#### file_base64(*location*) 

```
Returns the base64 - encoded content of the file at the given location.

```

#### file_copy(*source, dest, recursive, overwrite=True*) 

#### file_download(*url, to, overwrite=True, retry=3, timeout, login='', passwd='', minspeed, multithread, expand*) 

```
download from url
@return path of downloaded file
@param to is destination
@param minspeed is kbytes per sec e.g. 50, if less than 50 kbytes during 10 min it will
    restart the download (curl only)
@param when multithread True then will use aria2 download tool to get multiple threads

```

#### file_download_binary(*local, remote*) 

#### file_download_local(*remote, local*) 

#### file_ensure(*location, mode, owner, group*) 

```
Updates the mode/owner/group for the remote file at the given
location.

```

#### file_exists(*location*) 

```
Tests if there is a *remote* file at the given location.

```

#### file_expand(*path, to*) 

#### file_get_tmp_path(*basepath=''*) 

#### file_is_dir(*location*) 

#### file_is_file(*location*) 

#### file_is_link(*location*) 

#### file_link(*source, destination, symbolic=True, mode, owner, group*) 

```
Creates a (symbolic) link between source and destination on the remote host,
optionally setting its mode / owner / group.

```

#### file_md5(*location*) 

```
Returns the MD5 sum (as a hex string) for the remote file at the given location.

```

#### file_move(*source, dest, recursive*) 

#### file_read(*location, default*) 

#### file_remove_prefix(*location, prefix, strip=True*) 

#### file_sha256(*location*) 

```
Returns the SHA - 256 sum (as a hex string) for the remote file at the given location.

```

#### file_unlink(*path*) 

#### file_update(*location, updater=<function CuisineCore.<lambda> at 0x7f448d508730>*) 

```
Updates the content of the given by passing the existing
content of the remote file at the given location to the 'updater'
function. Return true if file content was changed.

For instance, if you'd like to convert an existing file to all
uppercase, simply do:

>   file_update("/etc/myfile", lambda _: _.upper())

Or restart service on config change:

> if file_update("/etc/myfile.cfg", lambda _: text_ensure_line(_, line)):
    self.run("service restart")

```

#### file_upload_binary(*local, remote*) 

#### file_upload_local(*local, remote*) 

#### file_write(*location, content, mode, owner, group, check, sudo, replaceArgs, strip=True, showout=True, append*) 

```
@param append if append then will add to file and check if each line exists, if not will
    remove

```

#### fs_find(*path, recursive=True, pattern='', findstatement='', type='', contentsearch='', extendinfo*) 

```
@param findstatement can be used if you want to use your own find arguments
for help on find see http: // www.gnu.org / software / findutils / manual / html_mono /
    find.html

@param pattern e.g. * / config / j*
    *   Matches any zero or more characters.
    ?   Matches any one character.
    [string] Matches exactly one character that is a member of the string string.

@param type
    b    block(buffered) special
    c    character(unbuffered) special
    d    directory
    p    named pipe(FIFO)
    f    regular file
    l    symbolic link

@param contentsearch
    looks for this content inside the files

@param extendinfo: this will return [[$path, $sizeinkb, $epochmod]]

```

#### getenv(*refresh*) 

#### joinpaths(**args*) 

#### locale_check(*locale*) 

#### locale_ensure(*locale*) 

#### pprint(*text, lexer='bash'*) 

```
@format py3, bash

```

#### pwd() 

#### run(*cmd, die=True, debug, checkok, showout=True, profile, replaceArgs=True, shell*) 

```
@param profile, execute the bash profile first

```

#### setIDs(*name, grid, domain='aydo.com'*) 

#### set_sudomode() 

#### shell_safe(*path*) 

#### sudo(*cmd, die=True, showout=True*) 

#### sudo_cmd(*command*) 

#### system_uuid() 

```
Gets a machines UUID (Universally Unique Identifier).

```

#### system_uuid_alias_add() 

```
Adds system UUID alias to /etc/hosts.
Some tools/processes rely/want the hostname as an alias in
/etc/hosts e.g. `127.0.0.1 localhost <hostname>`.

```

#### touch(*path*) 

#### upload(*source, dest=''*) 

```
@param source is on local (where we run the cuisine)
@param dest is on remote host (on the ssh node)

will replace $varDir, $codeDir, ... in source using j.dirs.replaceTxtDirVars (is for local
    cuisine)
will also replace in dest but then using cuisine.core.args_replace(dest) (so for cuisine
    host)

@param dest, if empty then will be same as source very usefull when using e.g. $codeDir

upload happens using rsync

```

#### upload_from_local(*local, remote*) 

