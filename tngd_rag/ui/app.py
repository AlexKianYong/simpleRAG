from flask import Flask, render_template, request, jsonify
import sys
import os
import asyncio
from mcp import ClientSession
from mcp.client.sse import sse_client

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import existing functions and the internal pipeline object
from bot import initialize_bot, load_knowledge_base, ask_tngd_bot, _pipeline

app = Flask(__name__)

# --- CONFIGURATION ---
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FAQ_PATH = os.path.join(BASE_DIR, 'data', 'faq_data.json')
MCP_SERVER_URL = "http://localhost:8000/sse"

# --- INITIALIZATION ---
try:
    initialize_bot()
    load_knowledge_base(FAQ_PATH)
    print("✅ Bot initialized. Dynamic Routing active via _pipeline.llm")
except Exception as e:
    print(f"❌ Setup failed: {e}")

# --- MCP HELPERS ---
import requests # Add this at the top

async def handle_mcp_logic(question):
    try:
        async with sse_client(MCP_SERVER_URL) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()
                tools_data = await session.list_tools()
                
                # 1. Format tools for a clean prompt
                tool_list = "\n".join([f"- {t.name}: {t.description}" for t in tools_data.tools])

                # 2. Call Ollama DIRECTLY (Bypassing the RAG pipeline)
                # This ensures no "FAQ Assistant" instructions interfere.
                ollama_payload = {
                    "model": "mistral",
                    "prompt": (
                        f"You are a TNGD Decision Engine. Your ONLY job is to classify the user's intent into ONE category.\n\n"
                        f"CATEGORIES:\n"
                        f"1. fetch_balance: Use ONLY if the user wants to check/get their current balance or money.\n"
                        f"2. sys_status: Use ONLY if the user wants to check if the server or system is down/working.\n"
                        f"3. ask_dify: Use ONLY if user want to check backend platform data requests.\n"
                        f"4. FAQ: Use for ANY question starting with 'How', 'What', 'Why', 'Where', or requests for information/explanation.\n\n"
                        
                        f"EXAMPLES:\n"
                        f"- 'Check my balance' -> fetch_balance\n"
                        f"- 'How do I top up?' -> FAQ\n"
                        f"- 'What is RFID?' -> FAQ\n"
                        f"- 'Is the system down?' -> sys_status\n"
                        f"- 'Explain the refund policy' -> FAQ\n\n"
                        
                        f"USER QUESTION: {question}\n"
                        f"DECISION (Output only the category name):"
                    ),
                    "stream": False,
                    "options": {"temperature": 0} # Strictness
                }

                response = requests.post("http://localhost:11434/api/generate", json=ollama_payload)
                intent = response.json().get("response", "FAQ").strip().lower()

                print(f"🤖 Direct Ollama Router Decided: [{intent}]")

                # 3. Execution
                for tool in tools_data.tools:
                    if tool.name.lower() in intent:
                        result = await session.call_tool(tool.name, arguments={"query": question})
                        return {"type": "mcp", "answer": result.content[0].text}
                
                return {"type": "rag"}
    except Exception as e:
        print(f"⚠️ Direct Route Error: {e}")
        return {"type": "rag"}
    
# --- ROUTES ---
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/ask', methods=['POST'])
def ask_api():
    try:
        data = request.get_json()
        question = data.get('question', '').strip()
        if not question:
            return jsonify({'error': 'Question is empty'}), 400

        # Step 1: Run the Dynamic Router + MCP logic
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        decision = loop.run_until_complete(handle_mcp_logic(question))
        loop.close()

        # Step 2: Return MCP data or Fallback to RAG
        if decision["type"] == "mcp":
            return jsonify({'answer': decision["answer"], 'type': 'mcp'})

        # Standard RAG fallback
        result = ask_tngd_bot(question)
        return jsonify({
            'answer': result['final_answer'],
            'type': 'rag',
            'chunk_count': len(result.get('retrieved_chunks', []))
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, host='localhost', port=5000)