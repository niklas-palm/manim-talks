"""Move 6: every agent today works like this. The same stage; the three tools become generic ones, a shell, a file
reader, a file writer, and a coding task runs through the same loop at speed. The agent builds its own tools on demand
out of those three; that is the whole difference between our surveillance assistant and a coding agent."""
from lib.palette import *
from objects import *


class EveryAgent(TalkSlide):
    def construct(self):
        # --- the last frame of move five, rebuilt: the compacted list inside its window, the three cards, five and three
        t = title_still(self, *TITLES["state"])
        st = stage()
        user, app, model, arrows, calls, tools = st["user"], st["app"], st["model"], st["arrows"], st["calls"], st["tools"]
        cards = tool_cards()
        agent = agent_frame()
        msgs = put_history(messages(AGENT_LIST_TOP), HIST_STATE)
        calls.tracker.set_value(5); tools.tracker.set_value(3)
        window = context_window(AGENT_LIST_TOP)
        sm = under_app(SUMMARY_LABEL, app=app)
        self.add(user, app, agent, model, arrows, calls, tools, cards, msgs, window, sm)
        # --- the first change: the surveillance tools become the tools of a coding agent; the list clears for a new task
        generic = VGroup(*[tool_card(*g) for g in GENERIC_TOOLS])
        t = retitle(self, t, *TITLES["every"], extra=[FadeOut(window), FadeOut(sm), FadeOut(msgs), calls.to(0), tools.to(0),
                                                      *[ReplacementTransform(a, b) for a, b in zip(cards, generic)]])
        who = under_app("Claude Code, Codex, and every coding agent: this loop, these tools", 15, TEXT, app=app)
        self.play(FadeIn(who), run_time=0.4)
        self.next_slide("""Last move. Keep everything and change only the three cards. A coding agent, Claude Code, Codex, the agent in your
        editor, is exactly this picture: an application with an agent inside it that runs the loop and keeps the list, and a model. The difference is what the
        tools are. Ours knew about one house. Theirs are generic: run a shell command, read a file, write a file. Three tools
        that can do almost anything, because with a shell and a file system the agent can make whatever tool it needs on the
        spot: write a script, run it, read the output.""")
        # --- a coding task through the same loop, at speed
        msgs = messages(AGENT_LIST_TOP)
        self.add(msgs)
        msgs.append(self, message("user", "user · add a retry to the upload function"), frm=user, run_time=0.5)
        call_model(self, msgs, model, extra=generic, run_time=0.5)
        tu = reply(self, msgs, model, "tool_use", 'assistant · tool_use: bash("grep -rn upload src/")', run_time=0.35)
        self.play(calls.to(1), run_time=0.15)
        travel(self, tu, generic[0], TOOL, edges=True, run_time=0.3)
        msgs.append(self, message("tool_result", "user · tool_result: src/client.py:88 def upload(path):"), frm=generic[0], run_time=0.4)
        self.play(tools.to(1), run_time=0.15)
        call_model(self, msgs, model, extra=generic, run_time=0.4)
        tu2 = reply(self, msgs, model, "tool_use", 'assistant · tool_use: write_file("src/client.py", …)', run_time=0.3)
        self.play(calls.to(2), run_time=0.15)
        travel(self, tu2, generic[2], TOOL, edges=True, run_time=0.3)
        msgs.append(self, message("tool_result", "user · tool_result: written"), frm=generic[2], run_time=0.4)
        self.play(tools.to(2), run_time=0.15)
        call_model(self, msgs, model, extra=generic, run_time=0.4)
        tu3 = reply(self, msgs, model, "tool_use", 'assistant · tool_use: bash("pytest tests/test_upload.py")', run_time=0.3)
        self.play(calls.to(3), run_time=0.15)
        travel(self, tu3, generic[0], TOOL, edges=True, run_time=0.3)
        msgs.append(self, message("tool_result", "user · tool_result: 3 passed"), frm=generic[0], run_time=0.4)
        self.play(tools.to(3), run_time=0.15)
        call_model(self, msgs, model, extra=generic, run_time=0.4)
        reply(self, msgs, model, "assistant", "assistant · added a retry with backoff; tests pass", run_time=0.4)
        self.play(calls.to(4), run_time=0.2)
        self.next_slide("""A coding task through the same loop, at speed. The user asks for a retry in the upload function. The model does
        not know the code, so it asks for a shell command to find it, writes the change, runs the tests, and only then
        answers in words. Four model calls, three tool calls, no code path in the harness that knew anything about
        uploads or retries. Every decision was the model's; the harness ran the loop and kept the list. Read the last move
        again with this in mind: the list grew by eight messages for one task, and a real session does this hundreds of times,
        which is why every coding agent compacts its context.""")
        # --- the closing picture
        own = label("generic tools: the agent makes the tool it needs, on demand", 15, TOOL).move_to(who, aligned_edge=LEFT)
        self.play(FadeOut(who), FadeIn(own), run_time=0.5)
        self.finish("""So the whole talk is one picture. A plain application with one model call, whose code decided what to fetch.
        The same process named as a tool, then several tools, and the model choosing among them. The application running the
        loop: call, run, append, call again, until the model answers in words. A framework hiding that loop behind one call.
        The list of messages as the only state, with its window and the two ways to keep it short. And every agent you will
        use or build this year: the same loop, with tools generic enough that the agent builds its own. That is what an agent
        is.""")
