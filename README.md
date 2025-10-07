<h1 align="center">
  Caching-Proxy
</h1>

<h4 align="center">
    Simple HTTP caching proxy server built in Python
</h4>

<p align="center">
    <a href="#introduction">Intro</a> •
    <a href="#tech-stack">Tech Stack</a> •
    <a href="#setup">Setup</a> •
    <a href="#usage">Usage</a> •
    <a href="#contact">Contact</a>
</p>

---

## Introduction

Caching-Proxy is a lightweight proxy that allows you to cache HTTP responses to improve performance by reducing repeated requests to the origin server.

I built this project to learn more about caching logic and working with Redis.

---

## Tech Stack

- Python
- FastAPI
- Redis
- HTTPX

---

## Setup

### 1. Clone the Repository

```bash
git clone https://github.com/NikolenkoRostislav/caching-proxy.git
cd caching-proxy
```

### 2. Environment Variables

Create a `.env` file in the root folder with the following variables:
```env
REDIS_PORT
REDIS_HOST
REDIS_PASSWORD
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Run the Proxy

```bash
python main.py -o <origin url>
```
Replace <origin_url> with the URL you want to proxy requests to.

Optional flags:

-p <port>: Change the proxy port (default: 8000)

-c: Clear all or stale cached responses

---

## Usage
After starting the proxy, point your HTTP client to:

```bash
http://localhost:8000/<path>
```

Cached responses are served directly from Redis

New or expired responses are fetched from the origin and stored in cache

### Example

```bash
curl http://localhost:8000/posts/1
```

---

## Contact

You can contact me via:  
Work Email: rostislavnikolenkowork@gmail.com  
Personal Email: rostislav160307@gmail.com  
LinkedIn: [linkedin.com/in/rostyslav-nikolenko-58b069348](https://www.linkedin.com/in/rostyslav-nikolenko-58b069348)  
Telegram: @RSlavNV  