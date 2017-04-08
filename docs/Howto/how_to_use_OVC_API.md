# How to use the OpenvCloud APIs

TODO: check

## Using Python

```python
import requests


BASE_URL = "https:/$urlofmachine/restmachine/"

# note empty authkey
# fill in your username and password
params = {'username': {username}, 'password': {password}, 'authkey': ''}

auth_key = requests.post(BASE_URL + 'cloudapi/users/authenticate', params).json()
```

## Using cURL

```shell
curl -d username={username} -d password={password} https://mothership1.com/restmachine/cloudapi/users/authenticate
```

## Using JavaScript

```javascript
var url = "https://mothership1.com/restmachine/cloudapi/users/authenticate";
var params = {
    'username': <username>, //your username
    'password': <password>, //your password
    'authkey': ''
};
$.ajax({
    type: "GET",
    dataType: "jsonp",
    data: params,
    url: url,
    jsonp: '_jsonp',
    success: function (authkey) {
        console.log(authkey); //This is the returned authkey 
    }
});
```

```
!!!
title = "How To Use OVC API"
date = "2017-04-08"
tags = ["howto"]
```
