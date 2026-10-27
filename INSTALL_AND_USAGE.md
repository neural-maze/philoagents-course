<table style="border-collapse: collapse; border: none;">
  <tr style="border: none;">
    <td width="20%" style="border: none;">
      <a href="https://theneuralmaze.substack.com/" aria-label="The Neural Maze">
        <img src="https://avatars.githubusercontent.com/u/151655127?s=400&u=2fff53e8c195ac155e5c8ee65c6ba683a72e655f&v=4" alt="The Neural Maze Logo" width="150"/>
      </a>
    </td>
    <td width="80%" style="border: none;">
      <div>
        <h2>📬 Stay Updated</h2>
        <p><b><a href="https://theneuralmaze.substack.com/">Join The Neural Maze</a></b> and learn to build AI Systems that actually work, from principles to production. Every Wednesday, directly to your inbox. Don't miss out!
</p>
      </div>
    </td>
  </tr>
</table>

<p align="center">
  <a href="https://theneuralmaze.substack.com/">
    <img src="https://img.shields.io/static/v1?label&logo=substack&message=Subscribe%20Now&style=for-the-badge&color=black&scale=2" alt="Subscribe Now" height="40">
  </a>
</p>

<table style="border-collapse: collapse; border: none;">
  <tr style="border: none;">
    <td width="20%" style="border: none;">
      <a href="https://decodingml.substack.com/" aria-label="Decoding ML">
        <img src="https://github.com/user-attachments/assets/f2f2f9c0-54b7-4ae3-bf8d-23a359c86982" alt="Decoding ML Logo" width="150"/>
      </a>
    </td>
    <td width="80%" style="border: none;">
      <div>
        <h2>📬 Stay Updated</h2>
        <p><b><a href="https://decodingml.substack.com/">Join Decoding ML</a></b> for proven content on designing, coding, and deploying production-grade AI systems with software engineering and MLOps best practices to help you ship AI applications. Every week, straight to your inbox.</p>
      </div>
    </td>
  </tr>
</table>

<p align="center">
  <a href="https://decodingml.substack.com/">
    <img src="https://img.shields.io/static/v1?label&logo=substack&message=Subscribe%20Now&style=for-the-badge&color=black&scale=2" alt="Subscribe Now" height="40">
  </a>
</p>

------

# 🚀 Installation and Usage Guide

This guide will help you set up and run a ...

# 📑 Table of Contents

- [📋 Prerequisites](#-prerequisites)
- [🎯 Getting Started](#-getting-started)
- [📁 Project Structure](#-project-structure)
- [🏗️ Set Up Your Local Infrastructure](#-set-up-your-local-infrastructure)
- [⚡️ Running the Code for Each Module](#️-running-the-code-for-each-module)
- [🔧 Utlity Commands](#-utility-commands)

# 📋 Prerequisites

## Local Tools

For all the modules, you'll need the following tools installed locally:

| Tool | Version | Purpose | Installation Link |
|------|---------|---------|------------------|
| Python | 3.11 | Programming language runtime | [Download](https://www.python.org/downloads/) |
| uv | ≥ 0.4.30 | Python package installer and virtual environment manager | [Download](https://github.com/astral-sh/uv) |
| GNU Make | ≥ 3.81 | Build automation tool | [Download](https://www.gnu.org/software/make/) |
| Git | ≥2.44.0 | Version control | [Download](https://git-scm.com/downloads) |
| Docker | ≥27.4.0 | Containerization platform | [Download](https://www.docker.com/get-started/) |

<details>
<summary><b>📌 Windows users also need to install WSL (Click to expand)</b></summary>

We will be using Unix commands across the course, so if you are using Windows, you will need to **install WSL**, which will install a Linux kernel on your Windows machine and allow you to use the Unix commands from our course (this is the recommended way to write software on Windows). 

🔗 [Follow this guide to install WSL](https://www.youtube.com/watch?v=YByZ_sOOWsQ).
</details>

## Cloud Services

Also, the course requires access to these cloud services. The authentication to these services is done by adding the corresponding environment variables to the `.env` file:

| Service | Purpose | Cost | Environment Variable | Setup Guide | Starting with Module |
|---------|---------|------|---------------------|-------------| ---------------------|
| Qwen (Aliyun DashScope) | LLM API that powers the agents, through the OpenAI-compatible endpoint | Pay-per-use | `QWEN_API_KEY` | [控制台开通](https://bailian.console.aliyun.com/) | Module 1 |
| [Opik](https://rebrand.ly/philoagents-opik) | LLMOps | Free tier (Hosted on Comet - same API Key) | `COMET_API_KEY` | [Quick Start Guide](https://rebrand.ly/philoagents-opik-quickstart) | Module 5 |
| [OpenAI API](https://openai.com/index/openai-api/) | LLM API used for evaluation | Pay-per-use | `OPENAI_API_KEY` | [Quick Start Guide](https://platform.openai.com/docs/quickstart) | Module 5 |

This fork replaced the course's Groq calls with Qwen, so `GROQ_API_KEY` is only needed by the
legacy `evaluation/` scripts, which still import `ChatGroq`. Without `COMET_API_KEY` the API
still runs: prompts fall back to the local `prompts.py` and Opik tracing stays off.

When working locally, the infrastructure is set up using Docker. Thus, you can use the default values found in the [config.py](philoagents-api/src/philoagents/config.py) file for all the infrastructure-related environment variables.

But, in case you want to deploy the code, you'll need to setup the following services with their corresponding environment variables:

| Service | Purpose | Cost | Required Credentials | Setup Guide |
|---------|---------|------|---------------------|-------------| 
| [MongoDB](https://rebrand.ly/philoagents-mongodb) | Document database | Free tier | `MONGODB_URI` | 1. [Create a free MongoDB Atlas account](https://rebrand.ly/philoagents-mongodb-setup-1) <br> 2. [Create a Cluster](https://rebrand.ly/philoagents-mongodb-setup-2) </br> 3. [Add a Database User](https://rebrand.ly/philoagents-mongodb-setup-3) </br> 4. [Configure a Network Connection](https://rebrand.ly/philoagents-mongodb-setup-4) |

### Deploy notes for this fork

* The app reads `MONGO_URI`, not `MONGODB_URI`. `docker-compose.yml` already uses the right name.
* **Set `SESSION_SECRET` before publishing anywhere reachable.** With it the API signs a session
  token at `POST /session` and takes the player's identity from that signature, so `/chat`,
  `/chat-history`, `/reset-memory` and `/ws/chat` answer `401` without one. With it empty every
  endpoint is open and the per-player limit below is decoration: the browser picks its own
  `player_id`, so a script just keeps picking new ones. The UI caches the token in
  `localStorage` and re-mints it when the server rejects it, so rotating the secret only signs
  players out. There are still no accounts: anyone who knows a player's UUID can claim it at
  `/session` and inherit that save game.
* `CORS_ORIGINS` must list the origin the game is actually served from, or the browser blocks every call.
* The UI resolves the API origin from `window.PHILOAGENTS_API_URL` / `window.PHILOAGENTS_WS_URL`,
  set in `philoagents-ui/index.html` **before** the bundle loads (no trailing slash); it falls
  back to `localhost:8000` only on plain http. Because the token rides in an `Authorization`
  header, `allow_headers` lists that header explicitly instead of `*`. Keep the UI on the same
  scheme as its socket: `wss://` needs a TLS-terminating proxy.
* `/reset-memory` clears the authenticated caller and ignores any `player_id` in the body, so one
  player can no longer wipe another by naming them.
* Per player the API takes `RATE_LIMIT_MAX_MESSAGES` messages per `RATE_LIMIT_WINDOW_SECONDS`
  and rejects anything longer than `MAX_MESSAGE_CHARS` with a 422. Session minting is limited
  per client IP by `RATE_LIMIT_MAX_SESSIONS` - raise it behind a reverse proxy, where every
  visitor shares one address.
* Hard stop, independent of this code: set a spending cap and an alert in the DashScope console.

# 🎯 Getting Started

## 1. Clone the Repository

Start by cloning the repository and navigating to the `philoagents-api` project directory:
```
git clone https://github.com/neural-maze/philoagents-course.git
cd philoagents-course/philoagents-api
```

Next, we have to prepare your Python environment and its dependencies.

## 2. Installation

Inside the `philoagents-api` directory, to install the dependencies and activate the virtual environment, run the following commands:

```bash
uv venv .venv
. ./.venv/bin/activate # or source ./.venv/bin/activate
uv pip install -e .
```

Test that you have Python 3.11.9 installed in your new `uv` environment:
```bash
uv run python --version
# Output: Python 3.11.9
```

This command will:
- Create a virtual environment with the Python version specified in `.python-version` using `uv`
- Activate the virtual environment
- Install all dependencies from `pyproject.toml`

## 3. Environment Configuration

Before running any command, inside the `philoagents-api` directory, you have to set up your environment:
1. Create your environment file:
   ```bash
   cp .env.example .env
   ```
2. Open `.env` and configure the required credentials following the inline comments and the recommendations from the [Cloud Services](#-prerequisites) section.

# 📁 Project Structure

The project follows a clean architecture structure commonly used in production Python projects:

```bash
philoagents-api/
    ├── data/                  # Data files
    ├── notebooks/             # Notebooks
    ├── src/philoagents/       # Main package directory
    │   ├── application/       # Application layer
    │   ├── domain/            # Domain layer
    │   ├── infrastructure/    # Infrastructure layer
    │   └── config.py          # Configuration settings
    ├── tools/                 # Entrypoint scripts that use the Python package
    ├── .env.example           # Environment variables template
    ├── .python-version        # Python version specification
    ├── Dockerfile             # API Docker image definition
    ├── Makefile               # Project commands
    └── pyproject.toml         # Project dependencies
```

### 💻 Installation for Windows Users (using `make`)

If you are a Windows user and need to use the `make` command, you'll need to install GnuWin32.

#### Step 1: Install GnuWin32

1.  **Download GnuWin32:** Go to the official GnuWin32 website. 
2.  **Run the installer:** Follow the on-screen instructions to install GnuWin32. The default installation path is typically `C:\Program Files (x86)\GnuWin32`.

#### Step 2: Configure the `PATH`

After installation, you need to temporarily add the GnuWin32 `bin` directory to your system's `PATH` variable for the current terminal session. This allows your terminal to find the `make.exe` executable.

1.  Open **PowerShell** or **Command Prompt**.
2.  Navigate to the directory where the `Makefile` is located.
3.  Execute the following command to add GnuWin32 to your `PATH`:

    ```powershell
    $env:PATH += ";C:\Program Files (x86)\GnuWin32\bin"
    ```

    **Note:** This command only modifies the `PATH` for the current session. If you close the terminal, you will need to run this command again the next time you want to use `make`.

#### Step 3: Run the `Makefile`

With the `PATH` configured, you can now run the `make` command from the same terminal session.

```bash
make infrastructure-up
```















# 🏗️ Set Up Your Local Infrastructure

We use Docker to set up the local infrastructure (Game UI, Agent API, MongoDB).

> [!WARNING]
> Before running the command below, ensure you do not have any processes running on ports `27017` (MongoDB), `8000` (Agent API) and `8088` (Game UI). The UI used to be published on `8080`; change that in `docker-compose.yml` and in `CORS_ORIGINS` together.

From the root `philoagents-course` directory, to start the Docker infrastructure, run:
```bash
make infrastructure-up
```

From the root `philoagents-course` directory, to stop the Docker infrastructure, run:
```bash
make infrastructure-stop
```

From the root `philoagents-course` directory, to build the Docker images (without running them), run:
```bash
make infrastructure-build
```

# ⚡️ Running the Code for Each Lesson

After you have set up your environment (through the `.env` file) and local infrastructure (through Docker), you are ready to run and test out the game simulation.

## Modules 1, 2, 3, 4 and 6

As most of the modules are coupled, you must test them all at once.

First, from the root `philoagents-course` directory, populate the long term memory within your MongoDB instance (required for agentic RAG) with the following command:
```bash
make create-long-term-memory
```

> [!NOTE]
> To visualize the raw and RAG data from MongoDB, we recommend using [MongoDB Compass](https://rebrand.ly/philoagents-mongodb-compass) or Mongo's official IDE plugin (e.g., `MongoDB for VS Code`). To connect to the working MongoDB instance, use the `MONGODB_URI` value from the `.env` file or found inside the [config.py](philoagents-api/src/philoagents/config.py) file.

Next, you can access the game by typing in your browser:
```
http://localhost:8088
```
Which will open the game UI, similar to the screenshot below:

![Philosopher Town](static/game_starting_page.png)

To see the instructions for playing the game, you can click on the `Instructions` button. Click the `Let's Play!` button to start the game.

Now you can start playing the game, wander around the town and talk to our philosophers, as seen in the screenshot below:

![Philosopher Town](static/game_socrates_example.png)

You can also access the API documentation by typing in your browser:
```
http://localhost:8000/docs
```

If you want to **directly call the agent bypassing the backend and UI logic**, you can do that by running:
```bash
make call-agent
```

To delete the long term memory from your MongoDB instance, you can run the following command:
```bash
make delete-long-term-memory
```

## Module 5

Only module 5 on evaluation and monitoring has its own instructions.

First, to visualize the prompt traces, as seen in the screenshot below, visit [Opik](https://rebrand.ly/philoagents-opik-dashboard).

![Opik](static/opik_monitoring_example.png)

To evaluate the agents, from the root `philoagents-course` directory, you can run the following command:
```bash
make evaluate-agent
```

To visualize the evaluation results, as seen in the screenshot below, you also have to visit [Opik](https://rebrand.ly/philoagents-opik-dashboard).

![Opik](static/opik_evaluation_example.png)

We already generated a dataset for you found at [data/evaluation_dataset.json](philoagents-api/data/evaluation_dataset.json), but in case you want to generate a new one (to override the existing one), you can run the following command:
```bash
make generate-evaluation-dataset
```
