# How an agent works: an API, a tool, a model, a list of messages, and a loop

A 13-minute talk for engineers who have used chat assistants and want to see what an agent is, in the machinery: an
application that calls an API and one model call, and why that is not enough; the API turned into a tool by a
decorator and a docstring; the loop in which the model asks and the application runs; the same loop as eight lines of
code with the eight places to intercept it; and the list of messages as the only state, with its limit and the two
remedies. One picture throughout, growing.

| Move | Scene | Clicks | Minutes |
|---|---|---|---|
| Opening | `Opening` | 1 | 0.5 |
| 1. An application, an API, and one model call | `TheApi` | 4 | 2.5 |
| 2. From an API to a tool | `ToolFromApi` | 3 | 2.5 |
| 3. The loop | `TheLoop` | 5 | 3 |
| 4. The same loop as code, and where to intercept it | `TheCode` | 4 | 3 |
| 5. The list is the only state | `TheState` | 4 | 2 |

```bash
bin/render.sh agents ql      # preview; qh for the talk itself
bin/serve.sh agents          # presenter and audience windows
```

Sources and simplifications are in `script.md`; speaker notes live next to the steps in `scenes/`.

## Decisions

Tool cards carry three lines (name 17, description 14, schema 13) in a 3.6 by 0.95 card; the description is read aloud
in the note. The context window is drawn as nine messages because tokens cannot be drawn; the label and the note say so.
The camera API box of move one becomes the device tag on the first tool card in move two, so the audience sees the same
thing change role rather than a new thing appear.
