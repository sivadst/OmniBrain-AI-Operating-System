<div align="center">

# 🧠 OmniBrain AI Operating System

### Autonomous Multi-Agent AI Platform with Memory, Planning, Reflection & Self-Healing

[![Python](https://img.shields.io/badge/Python-3.12-blue.svg)]()
[![FastAPI](https://img.shields.io/badge/FastAPI-Latest-009688.svg)]()
[![LangGraph](https://img.shields.io/badge/LangGraph-Multi--Agent-orange.svg)]()
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16-blue.svg)]()
[![Redis](https://img.shields.io/badge/Redis-7-red.svg)]()
[![Qdrant](https://img.shields.io/badge/Qdrant-VectorDB-purple.svg)]()
[![Docker](https://img.shields.io/badge/Docker-Compose-2496ED.svg)]()
[![License](https://img.shields.io/badge/License-MIT-green.svg)]()

**Enterprise-grade autonomous AI operating system built with LangGraph, FastAPI, LiteLLM, PostgreSQL, Redis, and Qdrant.**

*Designed for long-running intelligent workflows, multi-agent orchestration, persistent memory, tool execution, and human-in-the-loop approval.*

</div>

---

# ✨ Overview

OmniBrain is a production-oriented AI operating system that coordinates multiple specialized AI agents to solve complex tasks autonomously.

Instead of relying on a single LLM prompt, OmniBrain creates an execution graph where expert agents collaborate through planning, execution, critique, self-repair, memory retrieval, and optional human approval.

The architecture emphasizes scalability, observability, reliability, and modularity, making it suitable for enterprise AI applications.

---

# 🚀 Core Features

## 🤖 Multi-Agent Intelligence

- Planner Agent
- Executor Agent
- Critic Agent
- Self-Healing Agent
- Human Approval Node

---

## 🧠 Long-Term Memory

- Semantic Vector Memory (Qdrant)
- Relational Memory (PostgreSQL)
- Working Memory (Redis)
- Knowledge Graph Support
- Context Retrieval
- Persistent Conversations

---

## 🔄 LangGraph Orchestration

- Stateful execution
- Graph checkpoints
- Interrupt & resume
- Conditional routing
- Reflection loops
- Self-correcting execution

---

## ⚡ LLM Routing

Supports intelligent routing across providers using LiteLLM.

Examples include:

- GPT models
- Claude models
- Local Ollama models
- Custom OpenAI-compatible endpoints

Automatic fallback to local inference is supported when configured.

---

## 🛠 Tool Execution

Integrated tool framework including:

- Python execution
- Filesystem access
- Web scraping
- MCP-compatible tools
- External tool registry

---

## 📡 Real-Time Streaming

- FastAPI
- WebSockets
- Live execution updates
- Task streaming
- Progress monitoring

---

## 📊 Observability

- Structured logging
- Agent tracing
- Execution metrics
- Token usage
- Cost tracking
- Latency monitoring

---

# 🏗 Architecture

```
                 User Request
                       │
                       ▼
                FastAPI Gateway
                       │
         ┌─────────────┴─────────────┐
         │                           │
         ▼                           ▼
    Task Manager              WebSocket Stream
         │
         ▼
      LangGraph
         │
 ┌───────┴─────────────────────────────┐
 │                                     │
 ▼                                     ▼
Planner → Executor → Critic → Healer
             ▲               │
             └───────────────┘
                    │
            Human Approval
                    │
                    ▼
             Final Response
                    │
                    ▼
       PostgreSQL • Redis • Qdrant
```

---

# 📂 Repository Structure

```
.
├── app/
│   ├── agents/
│   ├── api/
│   ├── core/
│   ├── db/
│   ├── llm/
│   ├── memory/
│   ├── observability/
│   ├── schemas/
│   └── tools/
│
├── tests/
├── docker-compose.yml
├── worker.py
├── pyproject.toml
└── .env.example
```

---

# 🧠 Multi-Agent Workflow

```
User Task
    │
    ▼
Planner
    │
    ▼
Memory Retrieval
    │
    ▼
Executor
    │
    ▼
Tool Calls
    │
    ▼
Critic
    │
 ┌──┴─────────────┐
 │                │
Pass           Fail
 │                │
 ▼                ▼
Finish        Healer
                  │
                  ▼
             Execute Again
```

---

# 🛠 Tech Stack

### Backend

- FastAPI
- Python 3.12
- SQLAlchemy 2
- Pydantic V2
- AsyncIO

### AI

- LangGraph
- LiteLLM
- Ollama
- Sentence Transformers

### Databases

- PostgreSQL
- Redis
- Qdrant

### Infrastructure

- Docker
- Docker Compose

---

# 🔥 Key Capabilities

- Autonomous planning
- Persistent memory
- Reflection loops
- Self-healing execution
- Human approval workflows
- Tool orchestration
- Vector search
- Knowledge graph integration
- WebSocket streaming
- Enterprise API architecture

---

# 🚀 Quick Start

## Clone

```bash
git clone <repository>
cd omnibrain
```

---

## Configure

```bash
cp .env.example .env
```

Update your environment variables as needed.

---

## Start Services

```bash
docker compose up --build
```

---

## Launch API

```bash
uvicorn main:app --reload
```

---

# 🌐 API Overview

| Method | Endpoint | Description |
|----------|----------|-------------|
| POST | `/tasks` | Create a new AI task |
| POST | `/tasks/{id}/resume` | Resume interrupted workflow |
| GET | `/memory` | Query long-term memory |
| WS | `/tasks/{id}/stream` | Live execution events |

---

# 🧪 Testing

Run all tests:

```bash
pytest
```

Run with coverage:

```bash
pytest --cov=app
```

---

# 🔐 Security

- Environment-based configuration
- Async database access
- Structured exception handling
- Input validation
- JWT-ready architecture
- Secure secret management
- Tool execution isolation

---

# 📈 Future Roadmap

- Multi-workspace support
- Multi-user authentication
- Distributed agent clusters
- GPU inference workers
- Advanced planning algorithms
- Enterprise RBAC
- Kubernetes deployment
- OpenTelemetry dashboards
- Plugin marketplace
- Autonomous workflow marketplace

---

# 🤝 Contributing

Contributions are welcome.

Please:

1. Fork the repository
2. Create a feature branch
3. Add tests
4. Submit a pull request

---

# 📄 License

Released under the MIT License.

---

<div align="center">

## ⭐ If you found this project useful, consider giving it a star!

**Building the future of autonomous AI systems.**

</div>
