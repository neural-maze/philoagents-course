# PhiloAgents Course - Complete File Structure Analysis

## 📖 Project Overview

**PhiloAgents** is an open-source course teaching how to build an AI-powered game simulation engine that impersonates historical philosophers like Plato, Aristotle, and Turing. This is a collaboration between The Neural Maze and Decoding ML with sponsors MongoDB, Opik, and Groq.

## 🏗️ High-Level Architecture

```
philoagents-course/
├── 🎮 philoagents-ui/        # Frontend game interface (Phaser.js)
├── 🤖 philoagents-api/       # Backend AI agents (Python/FastAPI)
├── 📊 static/                # Documentation assets and diagrams
└── 🐳 Docker setup           # Containerized deployment
```

**Tech Stack:**
- **Frontend:** Phaser 3 (HTML5 game framework), Webpack, JavaScript
- **Backend:** Python 3.11, FastAPI, LangGraph, LangChain
- **AI:** Groq API, OpenAI API, RAG with vector embeddings
- **Database:** MongoDB (documents + vector storage)
- **DevOps:** Docker, Docker Compose, uv (Python package manager)

---

## 📁 Complete File Structure Analysis

### 🔧 Root Configuration Files

| File | Purpose | Key Details |
|------|---------|-------------|
| **README.md** | Main project documentation | Course outline with 6 modules, installation guide, learning objectives |
| **docker-compose.yml** | Multi-container orchestration | Defines 3 services: MongoDB, API (port 8000), UI (port 8080) |
| **Makefile** | Build automation | Commands for infrastructure, memory management, agent evaluation |
| **INSTALL_AND_USAGE.md** | Setup instructions | Prerequisites, cloud services setup, module-by-module running guide |
| **CONTRIBUTING.md** | Contribution guidelines | Open-source contribution process for bug fixes |
| **LICENSE** | MIT License | Open-source project licensing |
| **.gitignore** | Git ignore rules | Standard Python/Node.js ignores plus virtual environments |

### 🤖 philoagents-api/ (Backend - Python/FastAPI)

**Main Configuration:**
- **pyproject.toml** - Modern Python project config with dependencies (FastAPI, LangChain, LangGraph, MongoDB drivers)
- **Dockerfile** - Production container setup using Python 3.11 and uv package manager
- **Makefile** - Development commands (formatting, linting, testing)
- **.env/.env.example** - Environment variables for API keys (Groq, OpenAI, MongoDB)
- **langgraph.json** - LangGraph configuration for agent workflow
- **.python-version** - Python version specification (3.11)

**Source Code Structure (src/philoagents/):**

#### 🏛️ Domain Layer (`domain/`)
- **philosopher.py** - Core philosopher entity definitions and behaviors
- **philosopher_factory.py** - Factory pattern for creating different philosopher agents
- **prompts.py** - System prompts that define philosopher personalities and behaviors
- **evaluation.py** - Models for agent evaluation and performance metrics
- **exceptions.py** - Custom exception classes for error handling

#### 🔄 Application Layer (`application/`)
- **conversation_service/** - Main conversation handling logic
  - **workflow/** - LangGraph workflow implementation
    - **graph.py** - Main workflow graph definition
    - **nodes.py** - Individual workflow nodes (reasoning, retrieval, response)
    - **edges.py** - Workflow transitions and routing logic
    - **state.py** - Conversation state management
    - **chains.py** - LangChain chain definitions
    - **tools.py** - Agent tools and function calling
  - **generate_response.py** - Response generation orchestration
  - **reset_conversation.py** - Conversation reset functionality
- **rag/** - RAG (Retrieval Augmented Generation) system
  - **embeddings.py** - Vector embeddings using Hugging Face models
  - **retrievers.py** - Document retrieval from MongoDB vector store
  - **splitters.py** - Text chunking and document processing
- **data/** - Data processing pipeline
  - **extract.py** - Wikipedia and Stanford Encyclopedia data extraction
  - **deduplicate_documents.py** - Document deduplication using MinHash
- **evaluation/** - Agent evaluation system
  - **evaluate.py** - Performance evaluation using LLM-as-judge
  - **generate_dataset.py** - Evaluation dataset generation
  - **upload_dataset.py** - Dataset upload to evaluation platforms
- **long_term_memory.py** - Long-term memory management for philosophers

#### 🏗️ Infrastructure Layer (`infrastructure/`)
- **api.py** - FastAPI application setup with WebSocket support
- **mongo/** - MongoDB integration
  - **client.py** - MongoDB client with vector search capabilities
  - **indexes.py** - Database indexes for performance optimization
- **opik_utils.py** - Opik integration for LLMOps monitoring
- **config.py** - Configuration management using Pydantic Settings

**Tools Directory (`tools/`):**
- **call_agent.py** - Direct agent invocation script
- **create_long_term_memory.py** - Memory population from external sources
- **delete_long_term_memory.py** - Memory cleanup utility
- **evaluate_agent.py** - Agent performance evaluation
- **generate_evaluation_dataset.py** - Evaluation dataset creation

**Data Files (`data/`):**
- **evaluation_dataset.json** - Pre-generated evaluation questions and answers
- **extraction_metadata.json** - Metadata for data extraction process

### 🎮 philoagents-ui/ (Frontend - Phaser.js Game)

**Configuration Files:**
- **package.json** - Node.js dependencies (Phaser 3.88.2, Webpack toolchain)
- **Dockerfile** - Frontend container for development server
- **webpack/** - Build configuration
  - **config.js** - Development Webpack config with hot reload
  - **config.prod.js** - Production build optimization
- **.babelrc** - Babel transpilation configuration
- **log.js** - Development logging utility

**Source Code (src/):**
- **main.js** - Game entry point and Phaser configuration
- **scenes/** - Game scenes using Phaser Scene system
  - **MainMenu.js** - Start screen with game instructions
  - **Game.js** - Main gameplay scene with philosopher town
  - **Preloader.js** - Asset loading screen
  - **PauseMenu.js** - Pause/settings overlay
- **classes/** - Game object classes
  - **Character.js** - NPC philosopher character behaviors and movement
  - **DialogueBox.js** - Chat interface for conversations
  - **DialogueManager.js** - Dialogue state and flow management
- **services/** - API communication
  - **ApiService.js** - HTTP API calls to backend
  - **WebSocketApiService.js** - Real-time WebSocket communication

### 📊 static/ (Documentation Assets)
- **diagrams/** - System architecture and module diagrams
- **thumbnails/** - Video lesson thumbnails
- **sponsors/** - Sponsor logos (MongoDB, Opik, Groq)
- **game_screenshot.png** - UI demonstration images

### 🔧 Development Environment
- **.vscode/** - VS Code configuration
  - **launch.json** - Python debugger configurations
  - **settings.json** - Editor settings and extensions

---

## 🎯 Learning Modules Overview

| Module | Focus | Key Files |
|--------|-------|-----------|
| **1** | System Architecture | Documentation, design patterns |
| **2** | RAG Agent Development | `workflow/`, `rag/`, LangGraph implementation |
| **3** | Memory Systems | `long_term_memory.py`, MongoDB integration |
| **4** | API Deployment | `api.py`, FastAPI + WebSocket implementation |
| **5** | LLMOps & Evaluation | `evaluation/`, Opik monitoring |
| **6** | Production Setup | Docker, modern Python tooling (uv, ruff) |

## 🛠️ Key Technologies & Patterns

**AI/ML Stack:**
- **LangGraph** for agent workflow orchestration
- **LangChain** for LLM integration and RAG pipelines
- **Vector embeddings** for semantic search
- **MongoDB** as vector database
- **Groq API** for fast LLM inference

**Software Engineering:**
- **Clean Architecture** (domain/application/infrastructure layers)
- **Factory Pattern** for philosopher creation
- **WebSocket** for real-time communication
- **Docker Compose** for local development
- **Modern Python tooling** (uv, ruff, pyproject.toml)

**Game Development:**
- **Phaser 3** HTML5 game engine
- **Pixel art** assets and sprite animations
- **Real-time dialogue** system
- **Character AI** movement and interactions

## 🚀 Getting Started Commands

```bash
# Start entire system
make infrastructure-up

# Populate knowledge base
make create-long-term-memory

# Test agent directly
make call-agent

# Run evaluation
make evaluate-agent

# Access game UI
http://localhost:8080

# Access API docs
http://localhost:8000/docs
```

This project demonstrates production-ready AI agent development combining game development, LLMOps, and modern software engineering practices.