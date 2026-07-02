## What is simpletd?

Simplified tdarr inspired distributed transcoding software. 
Aiming for simplicity, minimal configuration, and reliable.


## How to use simpletd
simpletd bundles 2 software, a server and a node. 
The server keeps track of what to transcode, and what is finished.
The node receives jobs from the server, transcode them, and sends them back.
We can have as many nodes as we want.

The only way currently is to clone the repo and run it manually. uv is required.
```shell
git clone https://github.com/HK51503/simpletd.git
cd simpletd
```

### Setting up a server
```shell
cd services/server
cp config.template.toml config.toml
```
Set host, port, and video directory in `config.toml`.
```shell
# In services/server, 
uv run main.py
```

### Setting up a node
```shell
cd services/node
cp config.template.toml config.toml
```
Set host and port of the server, optionally set the node name and tmp folder location.
```shell
# In services/node,
uv run main.py start
```

### Configuring https
Please keep in mind that although https is supported, there are no security measures to prevent a malicious user from downloading videos. 
The links are really easy to guess (e.g. https://mydomain.com/videos/14). Do not use for really important stuff. I'm planning to implement a way to secure/encrypted connection.

## Roadmap / To-Do
Some (Most) are AI generated, please don't bash me :)

### Core Architecture & User Ideas
- [x] Implement https/wss
- [ ] Add codec templates (remove hardcoded videotoolbox)
- [ ] Make deployable as a container or an executable
- [ ] Add error handling

### Security
- [ ] Node Authentication & API Security (API keys, JWT, or secret key)
- [ ] Job Recovery & Heartbeats (retry limits, node tracking)
- [ ] Resource Checks & Disk Space Management (prevent out-of-space crashes, clean up tmp files)
- [ ] Resumable Downloads & Uploads (handle network hiccups)

### Features??
- [ ] Add network storage
- [ ] Real-time FFmpeg Progress Tracking (send progress via WebSocket)
- [ ] Pre-transcode Metadata Checks (use ffprobe to skip already transcoded files)
- [ ] Web UI / Dashboard (view pending jobs, active nodes, and progress)
- [ ] Automated Watch Folder (detect new files instantly via file system events)
- [ ] Node Capability Tags (route jobs based on node hardware/GPU support)
