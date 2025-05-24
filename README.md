# 🧠 SQL Agent with LangGraph + Gemini + LangChain + Chinook DB

This project builds a fully working **multi-step SQL Query Agent** using:

- [LangGraph](https://docs.langgraph.dev) (for agent workflows)
- [LangChain](https://www.langchain.com)
- [Gemini 1.5 Flash](https://ai.google.dev) (via `langchain-google-genai`)
- [Chinook SQLite DB](https://github.com/lerocha/chinook-database) (sample music store schema)

It creates an intelligent agent capable of:
- Understanding natural language questions
- Auto-generating SQL queries
- Validating those queries for correctness
- Executing them on a SQLite database
- Streaming answers interactively

---

## 📦 Installation

```bash
pip install -U langgraph langchain_community "langchain[openai]"
pip install -q langchain-google-genai
