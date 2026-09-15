# How an agent works: an application, a tool, a model, a list of messages, and a loop

A 16-minute talk for engineers who have used chat assistants and want to see what an agent is, in the machinery. A plain
application answers questions about a camera with one model call, and its code decides what to fetch. That whole
process, named, is a tool, and then there are several; the model chooses among them, and the application ends up running
a loop in its own code. A framework hides that loop behind one `Agent(...)` call; under the hood it is eight lines, with
hooks at the places the loop has. The list of messages as the only state, with its window and the two remedies. And
every agent in use today: the same loop, with tools generic enough that the agent makes its own. One picture throughout,
growing.

| Move | Scene | Clicks | Minutes |
|---|---|---|---|
| 1. An application with one model call | `TheApi` | 3 | 2 |
| 2. The whole process becomes a tool | `ToolFromApi` | 4 | 2.5 |
| 3. The application runs the loop itself | `TheLoop` | 6 | 3 |
| 4. The loop behind a framework call, and the hooks into it | `TheCode` | 12 | 5 |
| 5. The list is the only state | `TheState` | 4 | 2 |
| 6. Every agent today works like this | `EveryAgent` | 3 | 1.5 |

```bash
bin/render.sh agents ql      # preview; qh for the talk itself
bin/serve.sh agents          # presenter and audience windows
.venv/bin/python bin/export_pptx.py agents qh # optional PowerPoint, one autoplaying clip per step (generated, not committed)
```

Sources and simplifications are in `script.md`; speaker notes live next to the steps in `scenes/`.

## Decisions

The deck opens on the plain application, not on an agent: the audience must see the code decide what to fetch before the
tool, the choice and the loop mean anything. The three-line application and the decorated tool function are the same
process; the camera API box of move one becomes the device tag on the first tool card in move two, so the audience sees
the same thing change role rather than a new thing appear. The loop is run first by the application's own code (move
three); then the framework call that hides it is shown and run once with nothing to read, and only then is the call
opened into the eight lines and walked one line per click (move four). Hooks come after the framework is named, because
they are the framework's feature, not the loop's; the move closes by folding the code back into the definition with the
hook as one more line, so the audience sees what the framework took and what it gave. The plain application's question is one message that grows a line when the frame comes back, not a second user message:
the protocol's shape (a picture is a content block beside the text) is drawn where it is true and not explained until it
matters, which is when a tool result arrives in the user's role in move three, and that arrival gets a click of its own.
Move two ends on the named problem, which tool a question needs, without a preview of the cards going into the model; the
loop scene draws that properly on its first call. Tool cards carry three lines (name
17, description 14, schema 13) in a 3.6 by 0.95 card. The context window is drawn as eight messages because tokens
cannot be drawn; the label and the note say so. Every label one scene leaves for the next is a constant in `objects.py`,
and the window is one builder, so the seams cannot drift.