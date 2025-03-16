<h1 align="center">OpenRouter Proxy for Janitor AI</h1>

<p align="center">Self Hosted method using Docker and Cloudflare.</p>

<hr>
  
## How to use it?

First things first, clone the repository.
```
git clone https://github.com/YoungLordAce/OpenRouter-Proxy.git
```

### Method 1 - Docker Desktop (Windows)

[Download DockerDesktop](https://app.docker.com/)

Install and set it up, enable WSL if needed.


Before you continue,
Navigate to the folder you just downloaded and create a .env file.
In the .env file, make sure your OpenRouter key is pasted inside. If you don't have a key, make an OpenRouter account and create one.

On Docker Desktop, open the terminal and navigate to the repo you just cloned.

Run this command:
```
docker-compose up -d
``` 
This will build and start the containers, it might take a while so be patient.

Once the containers are built and running, click on Containers, stack name and you'll see the logs. A cloudflare link will have been generated, it will look something like this:
```https://biological-emphasis-bidder-highways.trycloudflare.com```

This is a temporary link and it will expire once you stop the container for any reason, every time you restart the container you will have to copy the newly generated link again.

Copy that link and paste it on JanitorAI making sure to add /v1/chat/completions at the end or the requests will fail. For example: ```https://biological-emphasis-bidder-highways.trycloudflare.com/v1/chat/completions```

Paste your OpenRouter Key on JanitorAI.

Done.



