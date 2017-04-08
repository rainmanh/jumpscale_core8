# Send Mail

## Install

```
ays install -n mailclient
```

This will ask for appropriate info about mail server.

## Usage

```
j.clients.email.send(self, recipients, sender, subject, message, files=None, mimetype=None)
Docstring:
@param recipients: Recipients of the message
@type recipients: mixed, string or list
@param sender: Sender of the email
@type sender: string
@param subject: Subject of the email
@type subject: string
@param message: Body of the email
@type message: string
@param files: List of paths to files to attach
@type files: list of strings
@param mimetype: Type of the body plain, html or None for autodetection
@type mimetype: string
```

## Example

```
import JumpScale.baselib.mailclient
j.clients.email.send("kristof@incubaid.com","kristof@incubaid.com","test","test")
```

```
!!!
title = "How To Send Mail"
date = "2017-04-08"
tags = ["howto"]
```
