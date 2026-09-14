# Serving open-weight LLMs: what the GPU is doing, and what that decides, in the bright style

The same talk as `talks/llm-serving`, presented on paper white instead of near-black: this folder holds a `.theme` naming
`bright`, a symlink to that talk's `scenes` and one to its `script.md`; a render adds its own
`media/` and its two pages. There is one copy of the drawing, so the two styles cannot drift apart. Render and present it like any other talk:

```bash
bin/render.sh llm-serving-bright ql      # qh when it is going into a room
bin/serve.sh llm-serving-bright
```
