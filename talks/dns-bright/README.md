# DNS: how a name becomes an address, in the bright style

The same talk as `talks/dns`, presented on paper white instead of near-black: this folder holds a `.theme` naming
`bright`, a symlink to that talk's `scenes` and one to its `script.md`, and nothing else. There is one copy of the
drawing, so the two styles cannot drift apart. Render and present it like any other talk:

```bash
bin/render.sh dns-bright ql      # qh when it is going into a room
bin/serve.sh dns-bright
```
