# Introduction
To secure the controller/agent communication, the agent was built with SSL client certificate support. 

# Configuring the agent.
Open `agent2.toml` file (located under `/opt/jumpscale8/apps/agent2`) and change the following:
* change `main.agent_controllers` to `["https://localhost/controller/"]
* set `security.client_certificate` to `/path/to/generated/client-testagent.crt`
* set `security.client_certificate_key` to `/path/to/generated/client-testagent.key`
* set `security.certificate_authority` to `/path/to/generated/server.crt` (This is only needed because we are using a self-signed certificate so we all telling the agent to trust this certificate, if this is not set agent will refuse to connect to the controller because it doesn't provide a trusted certificate)

Restart the agent.

