# X-Wing: The LARPAn1 Egress Node

<div align="center">
  <p><i>A highly stealthy, non-blocking asynchronous bridge connecting the LARPAn1 cognitive engine to the X ecosystem.</i></p>
  
  [![Python](https://img.shields.io/badge/Python-3.11%2B-blue?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
  [![MongoDB](https://img.shields.io/badge/MongoDB-Motor-47A248?style=for-the-badge&logo=mongodb&logoColor=white)](https://www.mongodb.com/)
  [![DSPy](https://img.shields.io/badge/DSPy-AI-FF4B4B?style=for-the-badge)](https://dspy.ai/)
</div>

---

## Architecture Overview

**X-Wing** is an autonomous, stealth-focused ingress/egress node designed to interface with the LARPAn1 core engine without triggering modern anti-bot heuristics. 

It operates completely out-of-band from official developer APIs, utilizing a multi-layered pipeline of open-source intelligence gathering, edge-node cognitive filtering, asynchronous background processing, and enterprise-partner webhooks to deliver payloads seamlessly.

---

## Technical Pipeline

The bridge multiplexes across four independent subsystems, orchestrated by a central `asyncio` event loop.

### 1. Ingress Layer (Nitter RSS Polling)
To avoid headless browser fingerprinting (Selenium/Playwright) and API rate limits, the bridge passively scrapes public data through unstable Nitter instances via `feedparser` and `httpx`.
* **Resiliency:** The configuration accepts a comma-separated array of fallback Nitter domains. If an instance throws a `502 Bad Gateway` or timeouts, the bridge shifts the pointer to the next instance instantly.
* **State Management:** Intercepted Tweet IDs are immediately committed to a MongoDB Atlas cluster using the asynchronous `motor` driver. A unique database index guarantees mathematical impossibility of duplicate processing, even under high concurrency or unexpected container restarts.

### 2. The Cognitive Gatekeeper (NVIDIA NIM)
Before invoking the heavy LARPAn1 engine, the bridge runs a local triage using `mistralai/mistral-large-3-675b-instruct-2512` via an NVIDIA NIM endpoint.
* **JSON Enforcement:** The gatekeeper parses the raw tweet text against a strict prompt matrix, forced to return a Pydantic-compliant boolean JSON payload. It filters out mundane chatter, routing only high-value, highly controversial, scammy, or inauthentic posts to the core engine.

### 3. Tactical Delay Matrix (DSPy & Groq)
If the Gatekeeper authorizes engagement, the bridge pings the LARPAn1 core API (`/psi09`) to generate the psychological profile and response text.
* **Algorithmic Humanization:** Instead of fixed cron-job cadences, the bridge uses a `dspy.TypedPredictor` powered by `openai/gpt-oss-120b` via Groq. The model evaluates the context of the tweet and the generated response to calculate a hyper-specific, unbounded stealth delay (in minutes). It mimics the unpredictable response latency of a human user evaluating an argument.

### 4. Egress Layer (IFTTT Stealth Workers)
The calculated delay and generated text are handed off to a detached `asyncio` background task.
* **Memory Safety:** The orchestration loop retains hard references to all sleeping background tasks in a `Set`, safeguarding the daemon threads from aggressive Python 3.7+ garbage collection during hours-long sleep cycles.
* **Delivery:** Upon waking, the worker fires the payload to an IFTTT Webhook. The text is automatically formatted to append the original, cleaned `x.com` status URL. IFTTT's enterprise OAuth handles the final hop to X, forcing the platform to render a native Quote Tweet without exposing the server's IP or triggering bot-detection scripts.

---

## Environment Setup

X-Wing requires Python 3.11+ and is designed for headless containerized deployment (Render, PM2, or Docker).

### Dependencies
```bash
git clone https://github.com/larp-analyser/An1-x-wing.git
cd An1-x-wing
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### Configuration
Create your `.env` file from the provided example template.

```env
# LARPAn1 Target
LARPAN1_URL="https://your-larpan1-app.onrender.com/psi09"

# MongoDB Database State
MONGO_URI="mongodb+srv://user:pass@cluster.mongodb.net/larpan1_bridge"

# Nitter Configuration
NITTER_INSTANCES="https://nitter.net,https://nitter.cz,https://nitter.privacydev.net"
NITTER_TOPICS="tech,ai,larp"

# Polling Interval (in minutes)
POLL_INTERVAL_MINUTES=15

# DSPy Delay Calculation (Groq)
GROQ_API_KEY="gsk_..."

# NVIDIA Gatekeeper API Key
NVIDIA_API_KEY="nvapi-..."

# Outbound IFTTT Webhook
IFTTT_WEBHOOK_KEY="..."
IFTTT_EVENT_NAME="post_to_twitter"
```

### Execution
Run the orchestrator as a module to enforce absolute import boundaries:
```bash
python -m src.main
```
