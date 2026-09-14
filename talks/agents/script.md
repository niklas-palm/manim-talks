# How an agent works: an API, a tool, a model, a list of messages, and a loop

Spine: an agent is a model called in a loop over a growing list of messages, where the model may answer with a request
to run a tool instead of an answer, and the application runs the tool, appends the result, and calls the model again.
Audience: engineers who have used chat assistants and want to see what an agent actually is; no prior agent framework
knowledge. Afterwards they should be able to turn one of their own API calls into a tool, read any agent framework's
loop, say where guardrails attach, and explain why long agent conversations need managing.
Length: 13 minutes, 20 clicks, 6 scenes.

One picture throughout, on the library grid: the user at the left column line; the application, a box holding the
list of messages and, in a second column, the functions it can run; the model, a box top right that the list goes into
and one reply comes out of; the devices at the right margin, each on the row of the function that reaches it. Colours:
user blue, model violet, tool yellow, what came back from the world teal, red for a wall.

## 1. An application, an API, and one model call (3 clicks, 2 min)
- **TheApi.** A user asks whether anyone is in the backyard. The application's own function calls the camera API
  (GET /cameras/2/frame), the frame and the question go into the prompt after a system prompt, the model answers in words.
  -> A different question (warm enough to open the door?): the same code fetches the same frame, the model cannot read a
  temperature from it; a thermometer exists and no code path reaches it: the code decides what to fetch, not the model.
  -> What a call carries: system prompt plus every message so far, resent in full; the model has no memory; the only
  place to change the answer is inside the call.

## 2. From an API to a tool (3 clicks, 2 min)
- **ToolFromApi.** The function the application already has, three lines, as highlighted code; a request travels to the
  camera API and a frame comes back as the bar walks the lines. -> Two additions, a decorator and a docstring; the tool
  definition fills in from the code: name from the function name, description from the first paragraph of the docstring,
  input schema from the type hints and the Args section. -> Three functions become three tool cards, each facing its
  device; what crosses to the model is the cards, what stays is the code, the API and the credentials.

## 3. The loop (5 clicks, 3 min)
- **TheLoop.** The cards take the plain function's place, each on the row of its device, and join the call next to the
  system prompt and the messages. -> The reply is a tool call: a structured request naming query_temperature, stop reason
  tool_use; the model chose from the descriptions. -> The application runs the function against the real thermometer and
  appends the result as a message in the user's role. -> Called again with the longer list, the model answers in words,
  stop reason end_turn, and the loop ends; the same question that failed in move one now succeeds. -> The loop drawn; the
  backyard question from move one runs through it at speed.

## 4. The same loop as code, and where to intercept it (4 clicks, 3 min)
- **TheCode.** The loop as eight highlighted lines. -> It runs against the picture: a bar walks the lines while the
  picture does each step, two passes. -> The hook points marked on the lines: before/after invocation, before/after model
  call, before/after tool call, message added; inspect, modify, cancel. -> A before-tool-call hook refuses a deletion;
  the refusal becomes the tool result and the model tells the user.

## 5. The list is the only state (4 clicks, 3 min)
- **TheState.** Every call sends the whole list; the list column framed as the context window; one more turn fills it.
  -> A long tool result overflows the window; the next call is refused. -> Sliding window: the oldest messages leave, a
  tool call and its result together. -> Summarisation: the oldest messages become one summary message, the most recent
  stay. Sessions and memory named in the note as the next talk.

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
- Strands Agents docs, "Hooks": BeforeInvocationEvent, AfterInvocationEvent, MessageAddedEvent, BeforeModelCallEvent,
  AfterModelCallEvent, BeforeToolCallEvent, AfterToolCallEvent (and batch variants); inspect, modify, cancel.
  https://strandsagents.com/docs/user-guide/concepts/agents/hooks/
- Strands Agents docs, "Conversation management": sliding window removes the oldest messages and dangling tool
  request/result pairs, trims on context overflow; SummarizingConversationManager defaults summary_ratio 0.3 and
  preserve_recent_messages 10. https://strandsagents.com/docs/user-guide/concepts/agents/conversation-management/
- Strands Agents docs, "Custom tools": the @tool decorator takes the name from the function, the description from the
  first paragraph of the docstring and the parameter descriptions from its Args section, the schema from type hints.
  https://strandsagents.com/docs/user-guide/concepts/tools/custom-tools/
- Strands Agents docs, "State": conversation history contains all user and assistant messages including tool calls and
  results and is passed to the model on each inference; agent state is not. https://strandsagents.com/docs/user-guide/concepts/agents/state/
- The narrative (a home surveillance assistant; a camera API that becomes a tool; thermometer and history tools; the
  loop as code; hooks) follows the author's own earlier PowerPoint deck slide for slide in its order; the drawings are new.

## Simplifications
- Messages are drawn as one line each; a real message can hold several content blocks (text and tool_use together).
- The context window is drawn as room for eight messages and labelled so; real windows are measured in tokens (the note
  gives 200k and 1M).
- One tool call per turn is drawn; models can request several in one reply (parallel tool use), noted in the notes.
- The tool code is the shape of the real thing: an API client call and a vision-model question; `camera_api` and
  `vision` stand for whatever those are in a given stack.
- Hook names are one framework's; the note says the points are general and the names differ.
- The loop code is the loop reduced to its shape; real implementations add streaming, retries, budgets and logging.
