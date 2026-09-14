# How an agent works: an API, a tool, a model, a list of messages, and a loop

Spine: an agent is a model called in a loop over a growing list of messages, where the model may answer with a request
to run a tool instead of an answer, and the application runs the tool, appends the result, and calls the model again.
Audience: engineers who have used chat assistants and want to see what an agent actually is; no prior agent framework
knowledge. Afterwards they should be able to turn one of their own API calls into a tool, read any agent framework's
loop, say where guardrails attach, and explain why long agent conversations need managing.
Length: 13 minutes, 21 clicks, 6 scenes. Every scene opens on a still picture and the mechanism starts on the next click.

One picture throughout, on the library grid: the user at the left margin; the application as a box holding the list of
messages, which grows downward and is the only state; the model top right, which the list goes into and one reply
comes out of; the tools in a column under the model, each card carrying the device it reaches; two counters at the
bottom, model calls and tool calls. Colours: user blue, model violet, tools yellow, what came back from the world teal,
red for a wall.

## 1. An application, an API, and one model call (TheApi, 4 clicks, 2.5 min)
- Still: user, application with an empty list, model, a camera API the application's own code calls (dashed link).
- A question: it becomes the first message; the code calls the camera API, the frame joins the list, the whole list goes
  to the model, one reply in words. Model calls: 1. This is how applications used models before agents.
- A second question the code cannot serve: the code fetches a frame again, the model cannot read a temperature from it;
  a thermometer exists with no code path to it. The wall: the code decided what to fetch, not the model.
- What every call carries: the whole list, again; the list is the only memory.

## 2. From an API to a tool (ToolFromApi, 3 clicks, 2.5 min)
- Still: the same picture, and inside the application the three-line function that called the camera API, as code.
- A decorator and a docstring are added; a highlight walks the code while the tool card fills in beside the model:
  name from the function name, description from the docstring, input schema from the signature; the camera API box
  becomes the card's device tag.
- Two more functions become two more cards. What crosses to the model: name, description, schema. What stays: code,
  API, credentials. The model never executes anything.

## 3. The loop (TheLoop, 5 clicks, 3 min)
- Still: three cards in place, empty list; the arrow into the model reads system prompt + tools + messages.
- The question that failed: the reply is a tool call (stop_reason tool_use), chosen from the descriptions.
- The application runs it against the thermometer and appends the result as a message in the user's role.
- Called again with the longer list: the answer in words, stop_reason end_turn. Two model calls, one tool call.
- The backyard question runs through the same loop at speed; the code no longer decides what to look at.

## 4. The same loop as code, and where to intercept it (TheCode, 4 clicks, 3 min)
- Still: the loop as eight highlighted lines, right; a reminder picture (model, list, tools), left.
- It runs against the picture: a bar walks the lines, slowly once, then fast, then the return.
- The eight hook points as dots on the lines: before/after invocation, model call, tool call; message added.
- A before-tool-call hook refuses a deletion; the refusal becomes the tool result.

## 5. The list is the only state (TheState, 4 clicks, 2 min)
- Still: the nine messages from move three inside a dashed frame, the context window (drawn as messages, counted in tokens).
- Every call sends the whole list; a 40,000-token tool result overflows the window and the call is refused.
- Sliding window: the oldest exchange leaves, a tool call and its result together.
- Summarisation: the oldest messages become one; the most recent stay verbatim. Sessions and memory are the next talk.

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
