# Agent Controller config

## Used environment arguments

### need to be set by us before lauching agent

- TMPDIR

### set by agent

- JUMPSCRIPTS_HOME
- SOCKET

  - is unix_sock_path

- AGENT_CONTROLLER_URL

- AGENT_GID
- AGENT_NID
- AGENT_CONTROLLER_NAME
- AGENT_CONTROLLER_CA
- AGENT_CONTROLLER_CLIENT_CERT
- AGENT_CONTROLLER_CLIENT_CERT_KEY
- SYNCTHING_URL
- AGENT_HOME

  - e.g. '/opt/jumpscale8/apps/agent2'

## Example configuration

```bash
[main]
redis_host =  "127.0.0.1:6379"
redis_password = ""

#Default http
[[listen]]
  address = ":8966"

#Example for https with multiple virtual hosts and clientcertificates
[[listen]]
  address = ":8443"
  [[listen.tls]]
    cert = "/path/to/domain1_certificate.cert"
    key = "/path/to/domain1_keyfile.key"
  [[listen.tls]]
    cert = "/path/to/domain2_certificate.cert"
    key = "/path/to/domain2_keyfile.key"
  [[listen.clientCA]]
    cert = "/path/to/CAcert1.cert"
  [[listen.clientCA]]
    cert = "/path/to/CAcert2.cert"

[influxdb]
host = "127.0.0.1:8086"
db   = "main"
user = "root"
password = "root"

########################################
# Advanced configuration, don't change #
########################################
[events]
enabled = true
module = "handlers"
python_path = "./extensions:/opt/jumpscale8/lib"
    [events.settings]
    syncthing_url = "http://localhost:18384/"
    redis_address = "localhost"
    redis_port = "6379"
    redis_password = ""

[processor]
enabled = true
module = "processor"
python_path = "./extensions:/opt/jumpscale8/lib"

[jumpscripts]
enabled = true
module = "jumpscript"
python_path = "./extensions:/opt/jumpscale8/lib"
    [jumpscripts.settings]
    jumpscripts_path = "./jumpscripts"


##### The following 2 sections are supportive for syncthing operation
##### Please don't remove or edit unless you know what you are doing
##### This will get replace once we implement local transport for hubbble.
[syncthing]
port=9066

[[listen]]
address="127.0.0.1:9066"
##### END SECTION.
```

## listen

The agencontroller can listen on multiple addresses. Specify a `[[listen]]` block for every address to listen on.

Each listen block must specify an `address` in the form of `ip:port` (if _IP_ is missing it's assumed `0.0.0.0`)

Example

```toml
[[listen]]
   address = ":8066"
```

## TLS

A `[[listen.tls]]` block enables HTTPS connections on the address supplied in the parent `[[listen]]` block. On production environments this should always be configured.

- **cert** is the certificate file. If the certificate is signed by a CA, this certificate file should be a concatenation of the server's certificate followed by the CA's certificate.
- **key** is the server's private key file which matches the certificate file.

The cert and key files must contain PEM encoded data.

Multiple `[[listen.tls]]` blocks may be specified to allow multiple dns entries and corresponding certificates to be served from the same address.

### Client certificates

If tls is enabled by specifying a `[[listen.tls]]` block, client certificates can be configured by adding `[[listen.clientCA]]` configurations.

- **cert** is a CA certificate file. Must be PEM encoded.

Clients connecting to this endpoint will then be required to provide a client certificate. The certificate will be verified against the CA certificate. Multiple `[[listen.clientCA]]` blocks may be specified and a client certificate will be accepted if it is accepted by at least 1 of the CA's.

### Advanced config

In the example configuration file above, a section has been marked as `ADVANCED` this section you don't usually change unless you really know what you are doing. this include the `events` `processors` and `jumpscripts` section. This section are mainly used to fine tune the integration between the controller and the underlying python modules extensions.

> Usually you don't need to modify the advanced section for everyday use.

#### [events] section

Instructs the controller how to handle events from the agent controller (basically the startup event) by handing the controller the events.py file. So handling of events can be customized without the need to rebuild the controller.

#### [processors] section

Instructs the controller how to intercept `commands` and `results`. If the section is gone this means the controller will not intercept the messages for more processing. By default this section is configured to pass the messages to a python module to store in mongodb using jumpsale extensions. So we create a `Command` and a `Job` for each sent/received message.

#### [jumpscripts] section

Another python extension to monitor the jumpscripts directly and auto adjust the scheduling of repeated tasks if the jumpscripts `period` tags has been modified.
