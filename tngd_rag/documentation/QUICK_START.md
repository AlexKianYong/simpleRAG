# Quick Reference - TNGD RAG Bot

## 🎯 What is This?

A RAG (Retrieval-Augmented Generation) system that answers Touch 'n Go FAQ questions using:
- **ChromaDB** for vector storage
- **Ollama** for embeddings and LLM
- **Python** for orchestration

---

## ⚡ Quick Commands

### First Time Setup (5 minutes)
```powershell
# 1. Install Ollama from https://ollama.ai
# 2. Start Ollama in one terminal
ollama serve

# 3. In another terminal, download model
ollama pull mistral

# 4. In project directory
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
# python initialize.py
```

**Web Interface**
```powershell

(Optional Step) cd scripts
- go to tngd_rag\scripts and launch the web scraper script

(Optional Step) python .\scrape_tngd_faq.py 
- this step will launch a  web scraper and grab all the FaQ content and save into json
- the output store in ### tngd_rag\data\faq_data.json ###

(Optional Step) rm -r chromadb_store
- clear chromaDB 

python .\ui\app.py

- when the app.py start knowledgeBase will be loaded into ChromaDB autimatically

# Open: http://localhost:5000
```

**In Your Code**
```python
from bot import initialize_bot, ask_tngd_bot

initialize_bot()
result = ask_tngd_bot("How do I reload my eWallet?")
print(result['final_answer'])
```

---

## 📁 Important Files

| File | Purpose |
|------|---------|
| `bot.py` | Main interface - use `ask_tngd_bot()` here |
| `rag_pipeline.py` | RAG processing logic |
| `guardrails.py` | Safety checks |
| `cli.py` | Command-line interface |
| `ui/app.py` | Web server |
| `initialize.py` | Setup script |
| `data/faq_data.json` | FAQ knowledge base |

---

## 🔧 Customization

### Use Different Model
```powershell
# Available models: mistral, llama2, neural-chat, orca-mini
python cli.py --model llama2
```

### Adjust Chunk Size
Edit `rag_pipeline.py`:
```python
RAGPipeline(chunk_size=500)  # Larger chunks
```

### Add More FAQ Data
Edit `data/faq_data.json` with your own Q&A pairs, then:
```powershell
python initialize.py
```

### Block Custom Patterns
Edit `guardrails.py`:
```python
self.injection_patterns.append(r'your.*pattern')
```

---

## 🆘 Common Issues

| Issue | Solution |
|-------|----------|
| "Connection refused" | Run `ollama serve` in separate terminal |
| "Model not found" | Run `ollama pull mistral` |
| "Port in use" | Change port in code or use different one |
| "Out of memory" | Use smaller model: `ollama pull orca-mini` |
| "Slow responses" | Check CPU/RAM, use faster model |

---

## 📊 System Overview

```
Question
    ↓
Guardrails Check
    ↓
Embed & Retrieve
    ↓
Build Context
    ↓
Generate Answer
    ↓
Return Result
```

---

## 🎯 Key Features

✅ Adversarial prompt blocking
✅ Semantic search via ChromaDB
✅ Local LLM via Ollama
✅ Multiple interfaces (CLI, Web, Code)
✅ Production-ready code
✅ Well-documented

---

## 📚 Docs

- **README.md** - Full documentation
- **SETUP_GUIDE.md** - Step-by-step setup
- **IMPLEMENTATION_SUMMARY.md** - Technical details
- **test_bot.py** - Test suite

---

**Status**: ✅ Ready to Use
**Created**: January 2026
