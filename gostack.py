import webview
import requests
import json
import os

API_KEY = "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"
CHAT_FILE = "chats.json"

class API:
    def save_state(self, state_json):
        with open(CHAT_FILE, 'w') as f:
            json.dump(state_json, f)
        return True

    def load_state(self):
        if os.path.exists(CHAT_FILE):
            with open(CHAT_FILE, 'r') as f:
                return json.load(f)
        return {"chats": {}, "currentId": None}

    def get_ai_response(self, prompt, model):
        headers = {"Authorization": f"Bearer {API_KEY}"}
        try:
            res = requests.post("https://api.groq.com/openai/v1/chat/completions", json={
                "model": model, "messages": [{"role": "user", "content": prompt}]
            }, headers=headers)
            return res.json()['choices'][0]['message']['content']
        except:
            return "Error connecting to AI."

html = """
<!DOCTYPE html>
<html>
<head>
    <script src="https://cdn.tailwindcss.com"></script>
    <style>
        body { background: #0c0c0c; color: #d1d1d1; font-family: sans-serif; }
        .code-container { background: #000; border: 1px solid #333; border-radius: 6px; margin: 10px 0; overflow: hidden; }
        .code-header { background: #1a1a1a; padding: 4px 10px; display: flex; justify-content: space-between; font-size: 10px; color: #888; border-bottom: 1px solid #333; }
        .code-body { display: flex; font-family: monospace; font-size: 13px; }
        .line-numbers { padding: 10px 8px; color: #555; border-right: 1px solid #333; text-align: right; user-select: none; background: #050505; }
        .code-content { padding: 10px; overflow-x: auto; color: #d1d1d1; }
        pre { margin: 0; white-space: pre-wrap; }
    </style>
</head>
<body class="flex h-screen">
    <div class="w-64 border-r border-[#222] p-4 flex flex-col gap-4 bg-[#0f0f0f]">
        <button onclick="newChat()" class="text-sm font-bold flex items-center gap-2 hover:text-white">+ New Chat</button>
        <div id="history" class="flex-1 overflow-y-auto space-y-1 text-sm"></div>
    </div>
    <div class="flex-1 flex flex-col items-center p-8">
        <div id="chat-window" class="w-full max-w-2xl flex-1 overflow-y-auto space-y-6"></div>
        <div class="w-full max-w-2xl bg-[#161616] border border-[#2a2a2a] p-3 rounded-xl flex items-center gap-2">
            <input id="in" class="flex-1 bg-transparent px-2 outline-none text-sm" placeholder="Message GoStack..." onkeydown="if(event.key==='Enter') send()">
            <select id="model" class="bg-transparent text-[10px] text-gray-400 outline-none"><option value="llama-3.3-70b-versatile">llama-3.3</option></select>
            <button onclick="send()" class="bg-white text-black px-4 py-1 rounded-lg font-bold text-sm">Send</button>
        </div>
    </div>
    <script>
        let state = { chats: {}, currentId: null };
        window.onload = async () => { 
            state = await pywebview.api.load_state(); 
            renderHistory(); 
        };
        async function send() {
            const input = document.getElementById('in'), prompt = input.value;
            if(!prompt.trim()) return;
            if(!state.currentId) { state.currentId = 'c'+Date.now(); state.chats[state.currentId] = { title: prompt.slice(0,15), msgs: [] }; }
            addMsg('You', prompt);
            input.value = '';
            addMsg('AI', '<span class="italic animate-pulse">Thinking...</span>', true);
            const res = await pywebview.api.get_ai_response(prompt, document.getElementById('model').value);
            document.querySelector('.animate-pulse').parentElement.innerHTML = '<b>AI:</b> ' + formatCode(res);
            state.chats[state.currentId].msgs.push({s: 'AI', m: res});
            await pywebview.api.save_state(state);
            renderHistory();
        }
        function formatCode(text) {
            return text.replace(/```([\\s\\S]*?)```/g, (m, c) => {
                const lines = c.trim().split('\\n');
                const lineNums = lines.map((_, i) => i + 1).join('\\n');
                const content = lines.join('\\n');
                return `<div class='code-container'><div class='code-header'><span>CODE</span><button onclick='copyMe(this)'>COPY</button></div><div class='code-body'><pre class='line-numbers'>${lineNums}</pre><pre class='code-content'><code>${content}</code></pre></div></div>`;
            });
        }
        function copyMe(btn) {
            const container = btn.closest('.code-container');
            const codeText = container.querySelector('code').innerText;
            navigator.clipboard.writeText(codeText).then(() => {
                btn.innerText = "COPIED!";
                setTimeout(() => btn.innerText = "COPY", 2000);
            });
        }
        function addMsg(s, m, isTemp=false) {
            if(!isTemp) state.chats[state.currentId].msgs.push({s: s, m: m});
            document.getElementById('chat-window').innerHTML += `<div class='text-sm mb-4'><b>${s}:</b> ${formatCode(m)}</div>`;
            document.getElementById('chat-window').scrollTop = document.getElementById('chat-window').scrollHeight;
        }
        function renderHistory() {
            document.getElementById('history').innerHTML = Object.keys(state.chats).map(id => 
                `<div class='p-2 cursor-pointer hover:bg-[#1a1a1a] rounded' onclick='loadChat("${id}")'>${state.chats[id].title}</div>`).join('');
        }
        function loadChat(id) {
            state.currentId = id;
            document.getElementById('chat-window').innerHTML = state.chats[id].msgs.map(m => `<div class='text-sm mb-4'><b>${m.s}:</b> ${formatCode(m.m)}</div>`).join('');
        }
        function newChat() { state.currentId = null; document.getElementById('chat-window').innerHTML = ''; }
    </script>
</body>
</html>
"""

# Change this line in gostack.py:
window = webview.create_window('GoStack', url='website.html', js_api=API(), width=1100, height=800)
webview.start()