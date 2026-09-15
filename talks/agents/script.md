# How an agent works: an application, a tool, a model, a list of messages, and a loop

Spine: an agent is a model called in a loop over a growing list of messages, where the model may answer with a request
to run a tool instead of an answer, and the application runs the tool, appends the result, and calls the model again.
Audience: engineers who have used chat assistants and want to see what an agent actually is; no prior agent framework
knowledge. Afterwards they should be able to turn one of their own API calls into a tool, read any agent framework's
loop, say where guardrails attach, explain why long agent conversations need managing, and see a coding agent as the
same loop with generic tools.
Length: 16 minutes, 32 clicks, 6 scenes. Every scene opens on a still picture and the mechanism starts on the next click.

One picture throughout, on the library grid: the user at the left margin; the application as a box holding the list of
messages, which grows downward and is the only state; the model top right, which the list goes into and one reply
comes out of; the tools in a column under the model, each card carrying the device it reaches; two counters at the
bottom, model calls and tool calls. One accent slot per meaning: the user, the model, the tools, what came back from
the world, and a wall.

The red thread, in one paragraph: a plain application answers questions about a camera with one model call, and its
code decides what to fetch. Look at that code as one process and name it: it is a tool, and then there can be several.
Now something must choose a tool per step; the model can, if it is told what the tools are, and then the application
has to run the choice and ask again, so the application ends up running a loop in its own code. A framework hides that
loop behind one `Agent(...)` call; under the hood it is eight lines, and because the framework owns them it can offer
hooks at the places the loop has (Strands names an event for each). The loop only appends, so the list grows until it
hits the context window, and two remedies shorten it. And every agent in use today is this loop with tools generic
enough that the agent makes its own.

## 1. An application with one model call (TheApi, 3 clicks, 2 min)
- Still: user, application whose whole code is three lines, model, a camera API the code calls (dashed link).
- A question: the code fetches the latest frame and puts it into the user's message beside the question (one message,
  two content blocks, drawn as two lines), the list goes to the model, one reply in words. Model calls: 1. This is how
  applications used models before agents.
- A question the code cannot serve: the code fetches a frame again into the message, the model cannot read a temperature
  from it; a thermometer exists with no code path to it. The wall: the code decided what to fetch, not the model.

## 2. The whole process becomes a tool (ToolFromApi, 4 clicks, 2.5 min)
- Still: the same picture, the conversation cleared, the three lines moved up to be read as one process.
- A decorator and a docstring are added; a highlight walks the code while the tool card fills in beside the model:
  name from the function name, description from the docstring, input schema from the signature; the camera API box
  becomes the card's device tag.
- Two more functions become two more cards. What crosses to the model: name, description, schema. What stays: code,
  API, credentials.
- The new problem, named and left standing: which tool does a question need? The note says the model can choose if it
  is told what the tools are; the next move shows it, so nothing is drawn here that the loop will draw properly.

## 3. The application runs the loop itself (TheLoop, 6 clicks, 3 min)
- Still: three cards in place, empty list; the arrow into the model reads system prompt + tools + messages.
- The question that failed: the reply is a tool call (stop_reason tool_use), chosen from the descriptions.
- The application runs it against the thermometer; the model never does.
- The result comes back into the list as a message in the user's role. Its own click, the first time: the protocol has
  two roles, and a tool result is the other side answering the model's request.
- Called again with the longer list: the answer in words, stop_reason end_turn. Two model calls, one tool call.
- The backyard question runs through the same loop at speed; the code no longer decides what to look at.

## 4. The loop behind a framework call, and the hooks into it (TheCode, 12 clicks, 5 min)
- Still: the picture small on the left (model, empty list, tools: a new agent); the Strands definition on the right,
  `Agent(model, system_prompt, tools)` and one call. No loop in the code.
- The call runs once at speed with nothing to read: four messages, two model calls, one tool call, inside the Agent.
- Under the hood: the definition opens into the eight lines the framework runs; the list rewinds to the question.
- The same call walked one line per click: the list into the model; the reply appended; the test and the tool run; the
  result appended; the loop calls itself. Then a second pass at speed and the third call's return.
- Hooks, as this SDK's feature: an event at each place the loop has, as dots on the lines; other frameworks expose some
  of the same places under other names.
- A before-tool-call hook cancels a deletion; the refusal becomes the tool result.
- The eight lines fold back into the definition, which has gained one line: `hooks=[...]`.

## 5. The list is the only state (TheState, 4 clicks, 2 min)
- Still: the eight messages from move three inside a dashed frame, the context window (drawn as messages, counted in tokens).
- Every call sends the whole list; a 40,000-token tool result overflows the window and the call is refused.
- Sliding window: the oldest exchange leaves, a tool call and its result together.
- Summarisation: the oldest messages become one; the most recent stay verbatim. Sessions and memory are the next talk.

## 6. Every agent today works like this (EveryAgent, 3 clicks, 1.5 min)
- Still: the same stage; the three surveillance cards become bash, read_file, write_file.
- A coding task runs through the same loop at speed: find the function, write the change, run the tests, answer.
- Generic tools: the agent makes the tool it needs, on demand. That is a coding agent.

## Sources (read 2026-09-14)
- Anthropic, "Building effective agents": agents versus workflows; the augmented LLM (retrieval, tools, memory); agents
  gain ground truth from tool results at each step and stop on completion or a stopping condition such as a maximum
  number of iterations; tool descriptions "as a great docstring for a junior developer".
  https://www.anthropic.com/research/building-effective-agents
- Claude platform docs, "Tool use with Claude" and "How tool use works": a tool is name, description, input_schema (JSON
  Schema); the model returns a tool_use block with id, name, input and stop_reason "tool_use"; the application runs the
  tool and returns a tool_result with the tool_use_id in a user message; the loop repeats while stop_reason is
  "tool_use" and exits on "end_turn" (or max_tokens, stop_sequence, refusal); the model never executes anything.
  https://platform.claude.com/docs/en/agents-and-tools/tool-use/overview and
  https://platform.claude.com/docs/en/agents-and-tools/tool-use/how-tool-use-works
- Claude platform docs, "Models overview": context windows 1M tokens (Claude Fable 5.1, Opus 5, Sonnet 5), 200K tokens
  (Claude Haiku 4.5). https://platform.claude.com/docs/en/about-claude/models/overview
- Model Context Protocol specification, "Tools": a tool definition is name, description, inputSchema (JSON Schema),
  optional annotations; tools are model-controlled; a human should be able to deny invocations.
  https://modelcontextprotocol.io/docs/concepts/tools
- Strands Agents docs, "Agent loop": invoke the model, check for tool use, execute, append results, invoke again until a
  final response; termination on end turn, budgets, cancellation. https://strandsagents.com/docs/user-guide/concepts/agents/agent-loop/
- Strands Agents docs, Python quickstart: `Agent(tools=[...])`, `Agent(model="...")`, the `@tool` decorator on a typed
  function with a docstring; "the agent automatically determines when to use tools".
  https://strandsagents.com/docs/user-guide/quickstart/python/
- Strands Agents docs, "Hooks": BeforeInvocationEvent, AfterInvocationEvent, MessageAddedEvent, BeforeModelCallEvent,
  AfterModelCallEvent, BeforeToolCallEvent, AfterToolCallEvent (and batch variants); inspect, modify, cancel a tool call
  with a message from BeforeToolCallEvent; registered with `Agent(hooks=[...])` or `agent.hooks.add_hook(...)`, a
  HookProvider implementing `register_hooks`.
  https://strandsagents.com/docs/user-guide/concepts/agents/hooks/
- Strands Agents docs, "Conversation management": sliding window removes the oldest messages and dangling tool
  request/result pairs, trims on context overflow; SummarizingConversationManager defaults summary_ratio 0.3 and
  preserve_recent_messages 10. https://strandsagents.com/docs/user-guide/concepts/agents/conversation-management/
- Strands Agents docs, "Custom tools": the @tool decorator takes the name from the function, the description from the
  first paragraph of the docstring and the parameter descriptions from its Args section, the schema from type hints.
  https://strandsagents.com/docs/user-guide/concepts/tools/custom-tools/
- Strands Agents docs, "State": conversation history contains all user and assistant messages including tool calls and
  results and is passed to the model on each inference; agent state is not. https://strandsagents.com/docs/user-guide/concepts/agents/state/
- Claude Code docs, tools reference: the built-in tools include Bash ("executes shell commands in your environment"),
  Read ("reads the contents of files"), Write ("creates or overwrites files"), Edit, Glob, Grep, Agent, WebFetch.
  https://code.claude.com/docs/en/tools-reference
- OpenAI, Codex CLI: "a coding agent from OpenAI that runs locally on your computer"; "inspect code, make changes, run
  commands, and automate repeatable work without leaving your terminal"; sandbox and approval modes decide when it may
  edit files or run commands without asking. https://github.com/openai/codex and https://learn.chatgpt.com/docs/codex/cli
- The narrative (a home surveillance assistant; the camera process that becomes a tool; thermometer and history tools;
  the Strands `Agent(...)` call; the loop as code; hooks; the bash tool of a code agent) follows the author's own
  earlier PowerPoint deck (`agents-funnel.pptx`, "How an agent works" and "Tool-calling agents vs code agents") in its
  order; the drawings are new.

## Simplifications
- Messages are drawn as one line each, except the plain application's questions, which show their two content blocks
  (the question and the frame) as two lines; a real message can hold several blocks (text and tool_use together).
- The context window is drawn as room for eight messages and labelled so; real windows are measured in tokens (the note
  gives 200k and 1M).
- One tool call per turn is drawn; models can request several in one reply (parallel tool use), noted in the notes.
- The plain application's code is the shape of the real thing: a camera client call and a model call with the frame in
  the message. The tool code likewise: `camera_api` and `vision` stand for whatever those are in a given stack.
- The hooks are drawn and named as Strands has them; the note says other frameworks expose some of the same places under
  other names. `RefuseDeletions()` stands for a HookProvider that cancels a BeforeToolCallEvent by policy.
- The loop code is the loop reduced to its shape; real implementations add streaming, retries, budgets and logging.
- A coding agent's tool set is drawn as three cards (shell, read, write); real ones have a dozen or more, and the note
  says so.
