# Lecture 1 Answers

## Exercises

- Model response to a course-specific question (one of the three homework levels; a summary is fine):
- What I noticed when comparing the response with the correct glossary definition:
- Number of tokens displayed (input / output):

## Homework

- Level attempted: Basic / Implementation / Advanced
- What I did:
- Results:
- Observations / questions:

### Basic
- Level attempted: Basic
- What I did: I changed the model three times: gemini-3.5-flash-lite, gemini-3.5-flash, gemini-3.1-flash-lite
- Results: Each models answer perfectly in different approach. 
- Observations / questions: What is MCP server? Each model answers in different approach although the core concepts are same.

@aam-bd ➜ /workspaces/lecture-ai-engineering-2026 (main) $  source /workspaces/lecture-ai-engineering-2026/.venv/bin/activate
(aie2026-exercises) @aam-bd ➜ /workspaces/lecture-ai-engineering-2026 (main) $ uv run python -m app.ask "What is MCP Server?"
[model] gemini-3.5-flash-lite
[質問] What is MCP Server?

An **MCP Server** (Model Context Protocol Server) is a program that exposes data, tools, and capabilities to AI models (like Claude, ChatGPT, or local LLMs) using Anthropic’s open-source **Model Context Protocol (MCP)**. 

Think of it as a **standardized "USB port" or API for AI**. Instead of developers writing custom integrations every time an AI needs to access a database, a file system, or a third-party app (like GitHub or Slack), they write an MCP Server. The AI client (an MCP Client) can then instantly connect to it.

Here is a breakdown of how it works and why it matters:

---

### 1. The Core Components of MCP
The Model Context Protocol operates on a client-server architecture:
*   **MCP Client:** The AI application you are interacting with (e.g., Claude Desktop app, an IDE like Cursor, or a custom AI agent).
*   **MCP Server:** A lightweight program that sits between the AI and your local machine, database, or cloud services.
*   **Data Sources:** What the server connects to (e.g., your local hard drive, a PostgreSQL database, Google Drive, etc.).

### 2. What Can an MCP Server Do?
An MCP server typically exposes three main things to an AI:
1.  **Resources (Data In):** Files, database schemas, API responses, or documents that the AI can read to get context (e.g., *"Read this log file and explain the error"*).
2.  **Tools (Actions Out):** Functions the AI can run. Unlike standard chat where the AI just generates text, an MCP tool lets the AI *do* something, like execute a SQL query,send an email, or create a file.
3.  **Prompts (Templates):** Pre-written prompt templates that users can easily trigger within their AI interface.

### 3. Why are MCP Servers Useful?
*   **No More Context Window Limits:** Instead of pasting massive codebases or documents into the chat, an MCP server lets the AI search and fetch *only* the relevant data it needs on demand.
*   **Security & Local Control:** You can run an MCP server locally on your computer. This means an AI can interact with your local files or private databases securely withoutyour sensitive data being unnecessarily uploaded to third-party servers.
*   **Standardization:** Before MCP, every AI platform had its own proprietary plugin system. With MCP, developers write *one* server, and any AI client that supports MCP can use it.

### 4. Real-World Examples
*   **Filesystem MCP Server:** Allows Claude to read, write, and search through folders on your local computer.
*   **GitHub MCP Server:** Allows the AI to search your repositories, read issues, and review pull requests.
*   **PostgreSQL MCP Server:** Allows the AI to inspect your database schema, write queries, and analyze your data.

### Summary
An **MCP Server** is a bridge that gives AI models secure, standardized access to external tools and data sources, transforming an AI from a simple chatbot into an active agent that can interact with your actual digital environment.

(aie2026-exercises) @aam-bd ➜ /workspaces/lecture-ai-engineering-2026 (main) $ uv run python -m app.ask "What is MCP Server?"
[model] gemini-3.5-flash
[質問] What is MCP Server?

An **MCP Server** (Model Context Protocol Server) is a lightweight application that acts as a bridge between an Artificial Intelligence model (like Claude, ChatGPT, or a localLLM) and external data sources, applications, or systems. 

Introduced as an open standard by **Anthropic** in November 2024, the **Model Context Protocol (MCP)** is often described as the **"USB-C for AI."**

---

### The Problem MCP Solves

Before MCP, if you wanted an AI model to read your local files, query your database, or interact with GitHub, developers had to write custom, fragmented code for every combination of AI app and external tool. 

* **Without MCP:** 5 AI clients × 10 tools = 50 custom integrations needed.
* **With MCP:** 5 AI clients + 10 MCP Servers = standard connection for everything.

---

### How an MCP Server Works

The architecture uses a traditional **Client-Server model**:

1. **MCP Client (The AI Application):** This is the user interface where the AI lives (e.g., Claude Desktop, Cursor IDE, or a custom AI agent framework).
2. **MCP Server (The Connector):** A program that runs locally or remotely to expose specific capabilities to the AI.
3. **The Data/Tool:** The actual system being accessed (e.g., a PostgreSQL database, Google Drive, or the local filesystem).

```
[ AI Model ] <---> [ MCP Client ] <--- (MCP Protocol) ---> [ MCP Server ] <---> [ Database / API / Files ]
```

---

### What Does an MCP Server Expose to AI?

An MCP Server provides three main primitives to the AI:

1. **Tools:** Functions the AI can execute.
   * *Example:* "Create a GitHub Issue", "Send a Slack message", "Run a SQL query."
2. **Resources:** Read-only data sources the AI can inspect.
   * *Example:* File contents, database schemas, server logs.
3. **Prompts:** Pre-designed templates that help users interact with specific workflows.
   * *Example:* A predefined prompt to analyze a specific git repository.

---

### Practical Examples of MCP Servers

* **GitHub MCP Server:** Allows an AI client to read repositories, search code, create pull requests, and manage issues.
* **PostgreSQL MCP Server:** Allows an AI to read your database schema, run safe SELECT queries, and explain database relationships.
* **Filesystem MCP Server:** Gives an AI secure access to read, write, or search through specific folders on your computer.
* **Web Search MCP Server (e.g., Brave Search):** Enables an offline LLM to fetch real-time search results from the web.

---

### Key Benefits

* **Security & Control:** The MCP Server runs on *your* controlled environment. You decide which folders, databases, or API keys the AI can touch, keeping your sensitive data safe.
* **Reusability:** Anyone can write an MCP Server once, and it will work with *any* MCP-compliant AI application.
* **Modularity:** You can attach multiple MCP Servers to a single AI application at the same time (e.g., letting Claude connect to GitHub, Google Drive, and Postgres all at once).
(aie2026-exercises) @aam-bd ➜ /workspaces/lecture-ai-engineering-2026 (main) $ uv run python -m app.ask "What is MCP Server?"
[model] gemini-3.1-flash-lite
[質問] What is MCP Server?

**MCP** stands for the **Model Context Protocol**. It is an open-standard protocol created by **Anthropic** (the company behind Claude) to solve a fundamental problem in AI development: **how AI models connect to external data and tools.**

Before MCP, if you wanted to connect an AI model (like Claude) to a database, a local file system, or a development tool (like GitHub), you had to write custom, one-off integration code for every single tool. This was inefficient, hard to maintain, and fragmented the ecosystem.

---

### What is an MCP Server?
An **MCP Server** is a lightweight piece of software that acts as a **standardized bridge** between an AI application (the "Client") and a specific data source or tool.

Instead of writing a custom integration for every tool, you write an **MCP Server** for the tool once. Once it follows the MCP standard, any AI application that supports the MCP protocol can connect to it instantly.

### How it works (The Architecture)
The MCP ecosystem consists of three parts:

1.  **MCP Host (The Client):** The AI application (e.g., Claude Desktop, an IDE like Cursor, or an AI-powered agent).
2.  **MCP Server:** A small program that exposes specific capabilities (e.g., a "Postgres MCP Server" or a "Google Drive MCP Server").
3.  **MCP Protocol:** The common language they use to talk to each other.

### Key Capabilities of an MCP Server
An MCP server generally exposes three things to the AI:

*   **Resources:** These are like files. The AI can "read" these (e.g., logs, database tables, or document content).
*   **Prompts:** These are pre-defined templates that help the user interact with the tool more effectively.
*   **Tools:** These are functions the AI can "execute." For example, a "GitHub MCP Server" might provide a `create_issue` tool that the AI can call to actually perform an action on your behalf.

---

### Why is this a big deal?

1.  **"Write Once, Run Anywhere":** If a developer builds an MCP server for a specific CRM or database, any AI app that speaks MCP can use it immediately without extra configuration.
2.  **Security and Control:** Because the connection is standardized, users can manage permissions locally. You can tell your AI application exactly which MCP servers it is allowed to talk to.
3.  **Local Context:** MCP allows AI models to securely access your local files, private databases, and internal company tools without you having to upload sensitive data to the cloud. You keep the data on your machine/server, and the AI just "queries" it through the MCP bridge.

### A Practical Example
Imagine you are using the **Claude Desktop app**:

*   **Without MCP:** You have to manually copy and paste code from your local project files into the Claude chat window.
*   **With MCP:** You install the "Filesystem MCP Server." Now, you can simply ask Claude, "Fix the bug in `auth.py`," and Claude can use the MCP server to read the file, analyze the code, and suggest the fix directly.

### Is it just for Claude?
While Anthropic launched it, they have made the protocol **open-source**. The goal is for it to become the industry standard for AI integrations, similar to how USB became thestandard for connecting peripherals to computers. Other AI platforms and tools are expected to adopt it to ensure their agents can communicate with the same ecosystem of servers.

**In short:** An MCP Server is the "connector" that allows AI models to safely and easily talk to your local files, databases, and third-party services.
(aie2026-exercises) @aam-bd ➜ /workspaces/lecture-ai-engineering-2026 (main) $ 


### Implementation

- Level attempted: Basic / Implementation / Advanced
- What I did:
- Results:
- Observations / questions: