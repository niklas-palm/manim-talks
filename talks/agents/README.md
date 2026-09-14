# How an agent works: a model, a list of messages, and a loop

A twelve-minute talk for engineers who have used chat assistants and want to see what an agent actually is. One
picture grows for the whole talk: a user, an application holding a list of messages and some tool functions, a model
the list goes into, and the devices the tools reach. The spine: an agent is a model called in a loop over a growing
list of messages, where the model may answer with a request to run a tool instead of an answer, and the application
runs it, appends the result and calls the model again.

| Move | Scene | Clicks | Minutes |
|---|---|---|---|
| Opening | `Opening` | 1 | 1 |
| 1. One model call can only talk | `OneCall` | 3 | 2 |
| 2. Tools, and the loop | `TheLoop` | 6 | 4 |
| 3. The same loop as code, and where to intercept it | `TheCode` | 4 | 3 |
| 4. The list is the only state | `TheState` | 4 | 3 |

```bash
bin/render.sh agents ql      # preview; qh for the talk itself
bin/serve.sh agents          # presenter and audience windows
```

Sources and simplifications are in `script.md`; speaker notes live next to the steps in `scenes/`. The example
(a home surveillance assistant) follows the author's earlier slide deck on agents; every drawing is new.

## Decisions

Tool cards carry three lines (name 15 pt, description 13 pt, schema 12 pt) in a 2.2 by 0.8 card, below the 15 pt
guideline on purpose: larger text does not fit three lines beside the message list, the name is the line the audience
must read, and the description is read aloud in the note.
