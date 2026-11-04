# llm-brainstem

Your [RAPP Brainstem](https://github.com/kody-w/rapp-installer) as a model inside [`llm`](https://llm.datasette.io).
Every agent you dropped into your Brainstem's `agents/` folder answers from the `llm` prompt; memory, journal and
fragments stay on your device. The plugin only talks to the Brainstem's public `POST /chat` door.

```bash
llm install llm-brainstem                       # or: llm install git+https://github.com/kody-w/llm-brainstem
llm -m brainstem "remember this as a fragment: trash goes out Tuesday night"
llm chat -m brainstem                           # keeps one Brainstem session for the whole chat
```

Env: `BRAINSTEM_URL` (default `http://127.0.0.1:7071`), `BRAINSTEM_SECRET` (only for a Brainstem on another machine).

The Brainstem is the grail: install it with one line from the link above. This plugin never changes it.
