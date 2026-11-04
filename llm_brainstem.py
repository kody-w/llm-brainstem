"""llm-brainstem: your Brainstem (and every agent in it) as a model inside Simon Willison's `llm` CLI.

    llm install llm-brainstem
    llm -m brainstem "what did I ask about the garage last week"
    llm -m brainstem --no-stream "..."       # same door
    llm chat -m brainstem                    # conversation keeps the Brainstem session

It talks to a running Brainstem only through POST /chat (the kernel's public door); the Brainstem picks its own
agents, so every tool you dropped into agents/ is available from the llm prompt. Journal, memory and fragments
stay on your device. Env: BRAINSTEM_URL (default http://127.0.0.1:7071), BRAINSTEM_SECRET (only when the
Brainstem is on another machine; sent as X-Brainstem-Secret).

Who did this before: llm's own plugin wire (register_models) and the OpenAI-compatible shims every local server
offers. Lesson applied: a sidecar talks through the public door only; nothing in the kernel changes.
"""
import json
import os
import urllib.request

import llm

__version__ = "0.1.0"
URL = os.environ.get("BRAINSTEM_URL", "http://127.0.0.1:7071").rstrip("/")


@llm.hookimpl
def register_models(register):
    register(Brainstem())


class Brainstem(llm.Model):
    model_id = "brainstem"
    can_stream = False
    supports_conversation = True

    def execute(self, prompt, stream, response, conversation):
        body = {"user_input": prompt.prompt}
        if prompt.system:
            body["user_input"] = f"{prompt.system}\n\n{prompt.prompt}"
        session, history = None, []
        if conversation is not None:  # the kernel is stateless: the conversation rides in the body every turn
            for prev in conversation.responses:
                session = (prev.response_json or {}).get("session_id") or session
                history.append({"role": "user", "content": prev.prompt.prompt})
                history.append({"role": "assistant", "content": prev.text_or_raise()})
        if session:
            body["session_id"] = session
        if history:
            body["conversation_history"] = history
        headers = {"Content-Type": "application/json"}
        secret = os.environ.get("BRAINSTEM_SECRET")
        if secret:
            headers["X-Brainstem-Secret"] = secret
        req = urllib.request.Request(URL + "/chat", data=json.dumps(body).encode(), headers=headers, method="POST")
        try:
            with urllib.request.urlopen(req, timeout=300) as r:
                data = json.loads(r.read().decode("utf-8"))
        except Exception as e:
            raise llm.ModelError(f"Brainstem at {URL} did not answer: {e}. Is it running? (curl {URL}/health)")
        response.response_json = {"session_id": data.get("session_id"), "model": data.get("model"),
                                  "agents": [a for a in (data.get("agent_logs") or [])] if isinstance(data.get("agent_logs"), list) else None}
        yield data.get("response") or ""
