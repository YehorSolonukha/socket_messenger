# Socket Messenger

## Description
**Socket Messenger** is a simple client–server messaging application written in Python using low-level sockets.

### Current features
- Multiple clients can connect to a central server
- Authentication using usernames and passwords
- Persistency via a text file
- Direct client-to-client messaging (no broadcast)  
- Concurrent connections handled via threading 

### Technologies used
- Python (`socket`, `threading`, `os`, `dotenv`)
- Docker & Docker Compose
- Linux-based containers (Ubuntu / official Python images)

---

## Requirements
- Docker Desktop (required docker engine to enable containerization)
- WSL2 (required on Windows to provide Linux kernel)

## Usage
### Docker 
#### Automatic (recommended)
This method automatically builds images and starts the server and clients.
1. clone the repository:
```
git clone https://github.com/YehorSolonukha/socket_messenger
cd socket_messenger
```
2. start Docker Desktop
3. after Docker Desktop is fully running, execute:
```
.\windows_docker_setup.ps1
```
#### Manual
This method provides full control over container configuration.
1. verify Docker installation
- Open a new terminal and run:
```
docker run hello-world
```
- If Docker is set up correctly, you should see a confirmation message and the container will exit automatically.
2. clone the repository:
```
git clone https://github.com/YehorSolonukha/socket_messenger
cd socket_messenger
```
3. manually remove the last line in compose.yaml - "command: sleep infinity"
4. build Docker images
```
docker compose build
```
This builds both the server and client images using their respective Dockerfiles.
You can verify that the server is running with ```docker compose ps```
5. open a new terminal for the first client and start a client container
```
docker compose run --it client
```
6. open a new terminal for the second client and start a client container
```
docker compose run --it client 
```
