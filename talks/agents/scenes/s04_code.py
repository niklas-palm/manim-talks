"""Move 4: what a framework hides, and how. The picture of move three shrinks to the left and the framework's agent
definition appears: the loop the application just ran by hand, behind one call. The call runs once at speed with nothing
to read. Then under the hood: the definition opens into the eight lines the framework runs, walked one line per click
against the picture. Then the hooks, which are this SDK's events at the places the loop has; one hook refuses a call.
Then the eight lines fold back into the definition, with the hook as one more line."""
from lib.palette import *
from objects import *

SRC = '''def agent_loop(msgs, tools):
    reply = model(system, tools, msgs)
    msgs.append(reply)

    if reply.stop_reason == "tool_use":
        result = run(reply.tool_use)
        msgs.append(result)
        return agent_loop(msgs, tools)

    return reply'''
L = {"model": 1, "append": 2, "test": 4, "run": 5, "result": 6, "again": 7, "return": 9}   # code line of each beat (blank lines skipped)
CALL_LINE = 7   # the line of FRAMEWORK_SRC that runs the agent

HOOKS = [(0, "BeforeInvocation", 0.24), (1, "BeforeModelCall", 0.13), (1, "AfterModelCall", -0.13), (2, "MessageAdded", 0.0),
         (5, "BeforeToolCall", 0.13), (5, "AfterToolCall", -0.13), (6, "MessageAdded", 0.0), (9, "AfterInvocation", -0.24)]   # (line, name, y offset)
CODE_POS = [3.4, 0.35, 0]


class TheCode(TalkSlide):
    def construct(self):
        # --- the last frame of move three, rebuilt: eight messages, three cards, four model calls and two tool calls
        t = title_still(self, *TITLES["loop"])
        st = stage()
        user, app, model, arrows, calls, tools = st["user"], st["app"], st["model"], st["arrows"], st["calls"], st["tools"]
        cards = tool_cards()
        full = put_history(messages(), HIST_LOOP)
        calls.tracker.set_value(4); tools.tracker.set_value(2)
        self.add(user, app, model, arrows, calls, tools, cards, full)
        # --- the first change: the picture shrinks to the left; a new agent, so an empty list; the framework's definition on the right
        mini_model, mini, mini_cards = mini_stage([])
        fw = code(FRAMEWORK_SRC, "python", 18).move_to(CODE_POS)
        fwl = label("a framework: the loop you just watched, behind one call", 14, MUTED).next_to(fw, DOWN, buff=GAP_TIGHT).align_to(fw, LEFT)
        pic_l = label("the same picture, small: model, list, tools", 14, MUTED).next_to(mini_model, UP, buff=GAP_TIGHT).align_to(mini_model, LEFT)
        t = retitle(self, t, *TITLES["code"], extra=[FadeOut(user), FadeOut(app), FadeOut(arrows), FadeOut(calls), FadeOut(tools), FadeOut(full),
                                                     ReplacementTransform(model, mini_model), ReplacementTransform(cards, mini_cards)], run_time=1.2)
        self.add(mini)
        self.play(FadeIn(fw), FadeIn(fwl), FadeIn(pic_l), run_time=0.6)
        self.next_slide("""Everything the application did by hand in move three, a framework does behind one call. The picture stepped aside
        to the left, small: the model, the list, the three tools; a new agent, so the list is empty. On the right, the whole
        agent as Strands writes it: a model, a system prompt, the list of tools, and then a question. There is no loop in
        this code. The loop is inside the Agent, and this move is about what is inside.""")

        # --- the call runs once at speed: nothing to read, the dance happens inside
        def into_model(rt):
            ghost = mini.copy().set_opacity(0.5)
            self.play(ghost.animate.scale(0.2).move_to(mini_model[0].get_center()), run_time=rt * 2)
            self.play(FadeOut(ghost), mini_model[0].animate.set_fill(MODEL, 0.35), run_time=rt)
            self.play(mini_model[0].animate.set_fill(MODEL, 0.10), run_time=rt)

        bar = highlight_line(fw, CALL_LINE)
        self.add(bar)
        self.play(FadeIn(bar), run_time=0.3)
        q = block("", USER, w=2.6, h=MINI_H, bare=True)
        mini.append(self, q, run_time=0.3)
        into_model(0.15)
        b = block("", TOOL, w=2.6, h=MINI_H, bare=True)
        mini.append(self, b, frm=mini_model[0], run_time=0.25)
        travel(self, b, mini_cards[1], TOOL, edges=True, run_time=0.25)
        mini.append(self, block("", RESULT, w=2.6, h=MINI_H, bare=True), frm=mini_cards[1], run_time=0.25)
        into_model(0.15)
        mini.append(self, block("", MODEL, w=2.6, h=MINI_H, bare=True), frm=mini_model[0], run_time=0.25)
        self.play(FadeOut(bar), run_time=0.3)
        self.next_slide("""The last line runs. Watch the picture, because there is nothing to read: the question joins the list, the list goes
        to the model, a tool call comes back, the thermometer answers, the result joins the list, the model is called again
        and answers in words. Four messages, two model calls, one tool call, and the application wrote none of it. That is
        what a framework is for. Now open it up.""")

        # --- under the hood: the definition opens into the eight lines the framework runs; the fast call rewinds so it can be walked slowly
        cd = code(SRC, "python", 20).move_to(CODE_POS)
        cl = label("under the hood: the eight lines the framework runs", 14, MUTED).next_to(cd, DOWN, buff=GAP_TIGHT).align_to(cd, LEFT)
        done = mini.blocks[1:]
        self.play(FadeOut(fwl), *[FadeOut(x) for x in done], run_time=0.4)
        for x in done:
            mini.remove(x)
        mini.blocks = mini.blocks[:1]
        self.play(ReplacementTransform(fw, cd), run_time=1.0)
        self.play(FadeIn(cl), run_time=0.4)
        self.next_slide("""Inside the Agent is this: eight lines. The list rewound to the question so we can watch the same call again, slowly.
        Read the code once, top to bottom, before it runs: call the model with the system prompt, the tools and the messages;
        append the reply; if the reply is a tool call, run it, append the result, and call the loop again; otherwise return
        the reply. Every agent framework is this, plus bookkeeping.""")

        # --- it runs against the picture: the first pass one line per click, then a fast pass, then the return
        bar = highlight_line(cd, L["model"])
        self.add(bar)

        def to_line(name, rt=0.3):
            self.play(bar.animate.move_to(highlight_line(cd, L[name])), run_time=rt)

        self.play(FadeIn(bar), run_time=0.3)
        into_model(0.45)
        self.next_slide("""One line per click. Line one: the whole list, with the system prompt and the tool definitions, goes into the
        model, and the model works. Everything the model will ever know about this conversation is what went in here.""")
        to_line("append")
        b = block("", TOOL, w=2.6, h=MINI_H, bare=True)
        mini.append(self, b, frm=mini_model[0], run_time=0.7)
        self.next_slide("""Line two: the reply comes out and is appended to the list, whatever it is. This time it is a tool call, yellow, so
        the list is one message longer before anything has been decided.""")
        to_line("test", 0.4)
        to_line("run", 0.4)
        travel(self, b, mini_cards[1], TOOL, edges=True, run_time=0.7)
        self.next_slide("""Line three is the test: did the model stop because it wants a tool? It did. Line four: the framework looks up the
        function behind the card and runs it against the real device. This is the only line where anything happens in the
        world, and it is your function that runs.""")
        to_line("result")
        mini.append(self, block("", RESULT, w=2.6, h=MINI_H, bare=True), frm=mini_cards[1], run_time=0.7)
        self.next_slide("""Line five: the result comes back from the tool and is appended, as a message in the user's role, teal. The model
        has not seen it yet; it is just in the list.""")
        to_line("again")
        to_line("model", 0.5)
        self.next_slide("""Line six: the loop calls itself with the longer list, and the bar is back at the top. That is the whole loop: nothing
        in it knows about cameras or thermometers; it calls, appends, runs, appends, and calls again.""")

        def pass_(rt):
            into_model(rt)
            to_line("append", rt)
            b = block("", TOOL, w=2.6, h=MINI_H, bare=True)
            mini.append(self, b, frm=mini_model[0], run_time=rt * 1.5)
            to_line("test", rt)
            to_line("run", rt)
            travel(self, b, mini_cards[1], TOOL, edges=True, run_time=rt * 1.5)
            to_line("result", rt)
            mini.append(self, block("", RESULT, w=2.6, h=MINI_H, bare=True), frm=mini_cards[1], run_time=rt * 1.5)
            to_line("again", rt)
            to_line("model", rt)

        pass_(0.15)
        into_model(0.15)
        to_line("append", 0.15)
        mini.append(self, block("", MODEL, w=2.6, h=MINI_H, bare=True), frm=mini_model[0], run_time=0.25)
        to_line("test", 0.15)
        to_line("return", 0.3)
        self.next_slide("""A second pass at speed, one more tool call than the fast run needed, to show the loop does not care how many. On
        the third call the reply is words, violet, the test is false, and line eight returns it. Six messages from eight
        lines; the model made every decision, the code made none.""")

        # --- the hooks: this SDK's events at the places the loop has
        dots, names = VGroup(), VGroup()
        for i, name, dy in HOOKS:
            y = cd.lines[i].get_center()[1] + dy
            d = Dot(color=TEAL, radius=0.06).move_to([cd.panel.get_left()[0] - 0.2, y, 0])
            n = label(name, 13, TEAL).next_to(d, LEFT, buff=0.1)
            dots.add(d); names.add(n)
        hl = label("Strands hooks: an event at each place the loop has", 14, TEAL).move_to(cl, aligned_edge=LEFT)
        self.play(FadeOut(bar), FadeOut(pic_l), FadeOut(cl), FadeIn(hl), LaggedStart(*[FadeIn(VGroup(d, n)) for d, n in zip(dots, names)], lag_ratio=0.15), run_time=1.2)
        self.next_slide("""Because the framework owns the loop, it can let you in at every place the loop has. Strands calls these hooks, and
        names an event for each: before and after the whole invocation, before and after each model call, before and after
        each tool call, and whenever a message is added. A hook can inspect, change or cancel. The names and the event set
        are this SDK's; other frameworks expose some of the same places under other names, because the loop has no other
        places. Guardrails, logging, cost limits, approval steps and tracing are all hooks at one of these dots.""")

        # --- one hook refuses a call
        self.play(dots[4].animate.set_color(PROBLEM), names[4].animate.set_color(PROBLEM), run_time=0.4)
        bar2 = highlight_line(cd, L["run"], PROBLEM)
        self.add(bar2)
        req = block("", TOOL, w=2.6, h=MINI_H, bare=True)
        mini.append(self, req, frm=mini_model[0], run_time=0.4)
        cross = label("delete_recording(...): refused by policy", 14, PROBLEM).move_to([-6.3, -2.45, 0], aligned_edge=LEFT)
        self.play(FadeIn(bar2), FadeIn(cross), run_time=0.5)
        mini.append(self, block("", PROBLEM, w=2.6, h=MINI_H, bare=True), frm=mini_cards[2], run_time=0.5)
        self.next_slide("""One hook in action. The model asks to delete a recording; a before-tool-call hook checks a policy and cancels the
        call. The tool never runs, and the refusal becomes the tool result, so the model learns it was refused and tells the
        user instead of pretending. This is the shape of every guardrail in an agent: the model asks, your code decides.""")

        # --- the eight lines fold back into the definition, the hook as one more line
        fw2 = code(FRAMEWORK_HOOKS_SRC, "python", 18).move_to(CODE_POS)
        fwl2 = label(FRAMEWORK_LABEL, 14, MUTED).next_to(fw2, DOWN, buff=GAP_TIGHT).align_to(fw2, LEFT)
        self.play(FadeOut(dots), FadeOut(names), FadeOut(bar2), FadeOut(cross), FadeOut(hl), run_time=0.4)
        self.play(ReplacementTransform(cd, fw2), run_time=1.0)
        self.play(FadeIn(fwl2), run_time=0.4)
        self.finish("""And the eight lines fold back into the definition, which has gained one line: the hook, registered on the agent.
        That is the trade a framework offers. You write the tools and the hooks; it runs the loop, keeps the list and raises
        the events. If you understood the loop, you understand what it does for you and what it cannot do: it cannot decide
        what your tools are, and it cannot make the list stop growing. That last one is the next move.""")
