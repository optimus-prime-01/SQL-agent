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

```
## 📊 Sample Output

```bash
> Action: sql_db_list_tables
> Observation: ['Employee', 'Customer', 'Invoice', ...]

> Action: sql_db_schema
> Observation: Table: Invoice, Columns: InvoiceId, CustomerId, InvoiceDate, Total...

> Action: sql_db_query
> Query: 
SELECT E.FirstName || ' ' || E.LastName AS SalesAgent, SUM(I.Total) AS TotalSales
FROM Invoice I
JOIN Customer C ON I.CustomerId = C.CustomerId
JOIN Employee E ON C.SupportRepId = E.EmployeeId
WHERE strftime('%Y', I.InvoiceDate) = '2009'
GROUP BY E.EmployeeId
ORDER BY TotalSales DESC
LIMIT 1;

> Final Answer: Jane Peacock was the top sales agent in 2009 with $19,772.46 in sales.

```
## ▶️ Run on Google Colab

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)]([https://colab.research.google.com/drive/1VKXKP6u9cnTjC0t0I2b8GlLRp7QwGT3m?usp=sharing](https://colab.research.google.com/drive/1-4Cq6-GDvTs8kKqjbiu6dbmDCzALxxpT?usp=sharing))

🔗 **Launch in Google Colab**  
*(This includes everything: Gemini setup, SQL agent code, DB download, and test query)*


