# simpletd

A simplified tdarr clone.

## Roadmap / To-Do

### Core Architecture & User Ideas
- [ ] Implement wss/https
- [ ] Add codec templates (remove hardcoded videotoolbox)
- [ ] Make deployable as a container or an executable
- [ ] Add robust error handling

### Security & Stability
- [ ] Node Authentication & API Security (API keys or JWT)
- [ ] Job Recovery & Heartbeats (retry limits, node tracking)
- [ ] Resource Checks & Disk Space Management (prevent out-of-space crashes, clean up tmp files)
- [ ] Resumable Downloads & Uploads (handle network hiccups)

### New Features
- [ ] Real-time FFmpeg Progress Tracking (send progress via WebSocket)
- [ ] Pre-transcode Metadata Checks (use ffprobe to skip already-transcoded files)
- [ ] Web UI / Dashboard (view pending jobs, active nodes, and progress)
- [ ] Automated Watch Folder (detect new files instantly via file system events)
- [ ] Node Capability Tags (route jobs based on node hardware/GPU support)
