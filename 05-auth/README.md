# Secure the MCP server with authentication

Let's cover authentication and authorization for your MCP server. This is important to ensure that only authorized clients can access your tools and data.

## Generate a token

We need a token that the client can send to the server to grant access.

```bash
uv run util.py
```

## Run the server with auth

Now, let's run our server

```python
uv run server.py # 
```

## Run the client with the token

```python
uv run client.py
```

If everything works, you should see the client successfully call the protected tool and get a response. If you try to call the tool without a valid token, you'll get an unauthorized error.


**In the terminal window**

```text
Valid token, proceeding...
User exists, proceeding...
User has required scope, proceeding...
```

