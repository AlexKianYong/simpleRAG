# 🧩 TNGD FAQ Chunking Strategy

This document defines the data preprocessing and chunking strategy used for the Touch 'n Go eWallet RAG (Retrieval-Augmented Generation) system.

## 1. Strategy Overview
We employ a **Fixed-Size Character Chunking with Sliding Window Overlap**. This ensures that the local AI model (Ollama) receives contextually rich snippets without exceeding its context window.



## 2. Configuration Parameters
The following parameters are implemented in the `DocumentChunker` class:

| Parameter | Value | Purpose |
| :--- | :--- | :--- |
| **Chunk Size** | 300 Characters | Controls the granularity of the information. |
| **Chunk Overlap** | 50 Characters | Prevents loss of context at the boundaries of a split. |
| **Split Type** | Word-safe | Uses `.split()` to ensure we don't cut in the middle of a word. |

## 3. The Logic Flow
1. **Source Data**: The system takes the `answer` field from the `faq_data.json` (scraped from TNGD).
2. **Word Accumulation**: Words are added to a buffer until the character count reaches `300`.
3. **Overlapping**: To start the next chunk, the system "looks back" approximately 10 words (50 chars) to repeat the end of the previous chunk.
4. **Metadata Mapping**: Every individual chunk is tagged with its original TNGD URL and Category.

## 4. Why this strategy?
* **Semantic Continuity**: Overlapping ensures that if a user's answer is split between two chunks, the vector search (ChromaDB) can still find a match in either one.
* **Memory Efficiency**: By keeping chunks at 300 characters, we can retrieve the "Top 5" most relevant results and stay well within the LLM's prompt limits.
* **Accuracy**: Smaller chunks prevent the "dilution" of relevance—ensuring the bot answers the specific question without talking about unrelated FAQ topics.

## 5. Metadata Structure
Stored in `ChromaDBStore`:
- `question`: Type of data (e.g., question_answer)
- `summary`: Summary or short solution
- `full_answer`: A preview of the original text for verification.
- `url`: Direct link to the TNGD Help Center article.
