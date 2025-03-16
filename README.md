<h1 align="center">OpenRouter Proxy for Janitor AI</h1>

<p align="center">Self Hosted method using Docker and Cloudflare.</p>

<hr>
  
## How to use it?

### Step 1:

First things first, clone the repository.
```
git clone https://github.com/YoungLordAce/OpenRouter-Proxy.git
```

### Step 2:

[Download DockerDesktop (Windows)](https://app.docker.com/)

Install and set it up, enable WSL if needed. NOTE: If you're on Linux, you can skip this step entirely.

### Step 3: 

Navigate to the folder you just downloaded and create a .env file.
In the .env file, find your OpenRouter key and paste it inside. If you don't have a key, make an OpenRouter account and create one. Keep note of your key as you will need it again later.
The inside of your .env file should look like this: 
```
OPENROUTER_API_KEY={Your OpenRouter key goes here}
```
Make sure the .env file is not a .txt file or it won't work. It must be .env and nothing else.

### Step 4: 

On Docker Desktop/Linux, open the terminal and navigate to the repo you just cloned.

Run this command:
```
docker-compose up -d
``` 
This will build and start the containers, it might take a while so be patient.

### Step 5: 

Once the containers are built and running, click on Containers, stack name and you'll see the logs. If you're on Linux use the command: ```docker logs cloudflared```. 
A cloudflare link will have been generated, it will look something like this:
```https://biological-emphasis-bidder-highways.trycloudflare.com```

This is a temporary link and it will expire once you stop the container for any reason, every time you restart the container you will have to copy the newly generated link again.

Copy that link and paste it on JanitorAI making sure to add /v1/chat/completions at the end or the requests will fail. For example: ```https://biological-emphasis-bidder-highways.trycloudflare.com/v1/chat/completions```

Paste your OpenRouter Key on JanitorAI.

Done.



