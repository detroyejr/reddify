Reddify
-------
Get notified with [pushover](https://pushover.net/) when a keyword is mentioned
in a subreddit. 

Create a toml file and place it in the project, home, or .config directory. You
can use the `reddify.toml.template` file for starters.


```
# Reddify.toml

[pushover]
USER_ID = ""
API_KEY = ""

[reddit]
CLIENT_ID = ""
CLIENT_SECRET = ""
USER_AGENT = "username/app-name/description"

[submissions]

homelabsales = [
  "free"
]

[comments]

homelabsales = [
  "free"
]
```

Run it:

```python reddify.py```


or build and run with docker.

```
docker build --tag reddify .
docker run -v $PWD/reddify.toml:/app/reddify.toml --restart on-failure:5 reddify
```
