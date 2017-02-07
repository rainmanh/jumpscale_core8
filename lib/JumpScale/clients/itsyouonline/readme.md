# ItsYouOnline client

Simply get the api client by calling
```
client = j.clients.itsyouonline.get()
```

## Authentication

### Via Client Credentials

You can use your user API key which you can get from https://itsyou.online/#home/
under the settings tab.

```python
applicationid = 'YYYYYY'
apikey = 'XXXXXXXXX'
client.oauth.LoginViaClientCredentials(client_id=applicationid, client_secret=apikey)
```

### Manually by setting oauth token

```python
client.api.session.headers['Authorization'] = 'token <oauth token>'
```

### Manually by setting jwt key

```python
client.api.session.headers['Authorization'] = 'bearer <jwt key>'
```


## Example methods

After authenticating

```python
client.api.GetUserPhonenumberByLabel('Home', 'John').json()
Out[17]: {'label': 'Home', 'phonenumber': '+15551234'}

...
```


## to get updated version of the client

- copy from https://github.com/itsyouonline/identityserver/tree/master/clients/python/itsyouonline