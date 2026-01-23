# 🚀 Potential Improvements for TNGD RAG Bot

This document outlines the roadmap to transition from a local prototype to a production-ready customer support assistant.

## 1. Data Ingestion & Quality (Priority #1)
Currently, the system relies on a manual JSON with many missing answers (`"-"`).
* **Automated Scraper with Error Handling**: Upgrade the scraper to dynamically extract content from the TNGD Support portal, handling dynamic JavaScript elements (using Selenium or Playwright) to avoid empty `"-"` fields.
* **Multi-format Support**: Enable the bot to read PDF manuals (e.g., TNG Visa Card terms) and images using **Multimodal RAG** (GPT-4o or Llava) to explain flowcharts or fee tables.
* **Semantic Chunking**: Instead of cutting text every 300 characters, use an LLM to find logical "breaking points" (e.g., after a complete instruction step) so context isn't lost.

## 2. Retrieval Optimization (The "Search" Engine)
* **Hybrid Search**: Combine **Vector Search** (meaning-based) with **Keyword Search** (BM25). This is critical for TNGD terms like "RFID" or "PayDirect" where exact word matching is often better than "similar meaning."
* **Re-ranking**: After retrieving the Top-5 chunks from ChromaDB, use a "Cross-Encoder" model to re-order them. This ensures the *best* answer is at the very top before giving it to the LLM.
* **Query Expansion**: If a user asks a short question like "Toll?", have the LLM rewrite it to "How do I pay highway tolls using Touch 'n Go eWallet?" to get better search results.

## 3. Conversation & User Experience
* **Chat Memory**: Currently, the bot forgets the last message. Adding **ConversationBufferMemory** will allow follow-up questions (e.g., User: "How to apply?" -> Bot: "Explain steps" -> User: "Is it free?" -> Bot understands 'it' means the application).
* **Source Citations**: Modify the UI to show the specific TNGD URL used for the answer so users can verify the information directly on the official site.
* **Streaming Responses**: Update the Flask UI to show words as they are generated (like ChatGPT), making the local Ollama model feel faster.

## 4. Evaluation & Guardrails (Safety)
* **Hallucination Detection**: Implement a "Groundedness" check. If the LLM's answer contains facts not found in the TNGD FAQ, the system should block the response.
* **TNGD Domain Guardrails**: Prevent the bot from answering non-TNGD questions (e.g., "How do I cook rice?").
* **Latency Monitoring**: Track how long Mistral takes to respond to ensure the local hardware isn't becoming a bottleneck for the user.

## 5. Logging feature
* **Debugging Feature**: Logging for debugging and tracing

## 6. Add Image
* **图片**: 
---
*Roadmap Version: 2026.01.22*