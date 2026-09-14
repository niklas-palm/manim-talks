# How an agent works: an application, a tool, a model, a list of messages, and a loop, in the bright style

The same talk as `talks/agents`, presented on paper white instead of near-black: this folder holds a `.theme` naming
`bright`, a symlink to that talk's `scenes` and one to its `script.md`; a render adds its own
`media/` and its two pages. There is one copy of the drawing, so the two styles cannot drift apart. Render and present it like any other talk:

```bash
bin/render.sh agents-bright ql      # qh when it is going into a room
bin/serve.sh agents-bright
```
