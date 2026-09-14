# How an agent works: an API, a tool, a model, a list of messages, and a loop

A thirteen-minute talk for engineers who have used chat assistants and want to see what an agent actually is. It starts
where teams start, with an application whose own code calls a camera API and asks a model about the frame; shows the
wall (the code decided what to fetch); turns that same function into a tool by adding a decorator and a docstring;
runs the loop; writes the loop down as eight lines with a highlight walking them while the picture does each step; marks
the hooks; and ends with the list of messages as the agent's only state and the two ways of keeping it inside the
context window. The spine: a model called in a loop over a growing list of messages, where the model may answer with a
request to run a tool, and the application runs it, appends the result and calls again.

| Move | Scene | Clicks | Minutes |
|---|---|---|---|
| Opening | `Opening` | 1 | 1 |
| 1. An application, an API, and one model call | `TheApi` | 3 | 2 |
| 2. From an API to a tool | `ToolFromApi` | 3 | 2 |
| 3. The loop | `TheLoop` | 5 | 3 |
| 4. The same loop as code, and where to intercept it | `TheCode` | 4 | 3 |
| 5. The list is the only state | `TheState` | 4 | 3 |

```bash
bin/render.sh agents ql        # preview; qh for the talk itself
bin/serve.sh agents            # presenter and audience windows
```

Sources and simplifications are in `script.md`; speaker notes live next to the steps in `scenes/`. One picture is
drawn throughout on the library grid: user, application (list of messages plus the functions column), model, devices;
each tool card sits on the row of the device it reaches, so a tool call is a horizontal line.

## Decisions

Tool cards carry three lines (name 15 pt, description 13 pt, schema 12 pt) in a 2.1 by 0.7 card, below the 15 pt
guideline on purpose: three lines must fit beside the message list, the name is the line the audience must read, and the
description is read aloud in the note. Message blocks are 15 pt in a 3.1 by 0.38 block, ten of which fit the application
box; the tenth crossing the box's bottom edge is the overflow the state scene is about.
