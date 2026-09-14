"""Move 4: the same loop as code, and where to intercept it. The code fills the right half; a small reminder picture on
the left does each step as the highlight bar walks the lines. Then the hook points, then one hook refusing a call."""
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

HOOKS = [(0, "BeforeInvocation", 0.24), (1, "BeforeModelCall", 0.13), (1, "AfterModelCall", -0.13), (2, "MessageAdded", 0.0),
         (4, "BeforeToolCall", 0.13), (4, "AfterToolCall", -0.13), (5, "MessageAdded", 0.0), (7, "AfterInvocation", -0.24)]   # (line, name, y offset)


class TheCode(TalkSlide):
    def construct(self):
        # --- the last frame of move three, rebuilt: nine messages, three cards, four model calls and two tool calls
        t = title_still(self, *TITLES["loop"])
        st = stage()
        user, app, model, arrows, calls, tools = st["user"], st["app"], st["model"], st["arrows"], st["calls"], st["tools"]
        cards = tool_cards()
        full = put_history(messages(), HIST_LOOP)
        calls.tracker.set_value(4); tools.tracker.set_value(2)
        self.add(user, app, model, arrows, calls, tools, cards, full)
        # --- the first change: the picture shrinks to the left to make room for its own code
        mini_model, mini, mini_cards = mini_stage([k for k, _ in HIST_LOOP])
        cd = code(SRC, "python", 20).move_to([3.4, 0.35, 0])
        cl = label("the loop, eight lines: every agent framework is this plus bookkeeping", 14, MUTED).next_to(cd, DOWN, buff=GAP_TIGHT).align_to(cd, LEFT)
        pic_l = label("the picture from move three", 14, MUTED).next_to(mini_model, UP, buff=GAP_TIGHT).align_to(mini_model, LEFT)
        t = retitle(self, t, *TITLES["code"], extra=[FadeOut(user), FadeOut(app), FadeOut(arrows), FadeOut(calls), FadeOut(tools),
                                                     ReplacementTransform(model, mini_model), ReplacementTransform(full, mini), ReplacementTransform(cards, mini_cards)], run_time=1.2)
        self.play(FadeIn(cd), FadeIn(cl), FadeIn(pic_l), run_time=0.6)
        self.next_slide("""The loop from move three written down: eight lines. The picture stepped aside to the left, small: the model,
        the eight messages, the three tools. Read the code once, top to bottom, before it runs: call the model
        with the system prompt, the tools and the messages; append the reply; if the reply is a tool call, run it, append
        the result, and call the loop again; otherwise return the reply. Every agent framework is this, plus bookkeeping.""")
        # --- it runs against the picture, two passes: slow, then fast
        bar = highlight_line(cd, 1)
        self.add(bar)
        self.play(FadeIn(bar), run_time=0.3)

        def pass_(rt):
            ghost = mini.copy().set_opacity(0.5)
            self.play(ghost.animate.scale(0.2).move_to(mini_model[0].get_center()), run_time=rt * 2)
            self.play(FadeOut(ghost), mini_model[0].animate.set_fill(MODEL, 0.35), run_time=rt)
            self.play(mini_model[0].animate.set_fill(MODEL, 0.10), bar.animate.move_to(highlight_line(cd, 2)), run_time=rt)
            b = block("", TOOL, w=2.6, h=MINI_H, bare=True)
            mini.append(self, b, frm=mini_model[0], run_time=rt * 1.5)
            self.play(bar.animate.move_to(highlight_line(cd, 3)), run_time=rt)
            self.play(bar.animate.move_to(highlight_line(cd, 4)), run_time=rt)
            travel(self, b, mini_cards[1], TOOL, edges=True, run_time=rt * 1.5)
            travel(self, mini_cards[1], b, RESULT, edges=True, run_time=rt * 1.5)
            self.play(bar.animate.move_to(highlight_line(cd, 5)), run_time=rt)
            mini.append(self, block("", RESULT, w=2.6, h=MINI_H, bare=True), frm=mini_cards[1], run_time=rt * 1.5)
            self.play(bar.animate.move_to(highlight_line(cd, 6)), run_time=rt)
            self.play(bar.animate.move_to(highlight_line(cd, 1)), run_time=rt)

        pass_(0.45)
        pass_(0.15)
        ghost = mini.copy().set_opacity(0.5)
        self.play(ghost.animate.scale(0.2).move_to(mini_model[0].get_center()), run_time=0.3)
        self.play(FadeOut(ghost), bar.animate.move_to(highlight_line(cd, 2)), run_time=0.15)
        mini.append(self, block("", MODEL, w=2.6, h=MINI_H, bare=True), frm=mini_model[0], run_time=0.25)
        self.play(bar.animate.move_to(highlight_line(cd, 3)), run_time=0.15)
        self.play(bar.animate.move_to(highlight_line(cd, 7)), run_time=0.3)
        self.next_slide("""Now it runs against the picture, slowly the first time. Line one: the list goes into the model. Line two: the reply
        joins the list, a tool call. Line three, the test, is true. Line four: the tool runs against its device. Line five:
        the result joins the list. Line six: the loop calls itself, and the bar is back at the top. The second pass at
        speed, and on the third the reply is words, the test is false, and line eight returns. Ten messages produced by
        eight lines; the model made every decision, the code made none.""")
        # --- the hook points
        dots, names = VGroup(), VGroup()
        for i, name, dy in HOOKS:
            y = cd.lines[i].get_center()[1] + dy
            d = Dot(color=TEAL, radius=0.06).move_to([cd.panel.get_left()[0] - 0.2, y, 0])
            n = label(name, 13, TEAL).next_to(d, LEFT, buff=0.1)
            dots.add(d); names.add(n)
        self.play(FadeOut(bar), FadeOut(pic_l), LaggedStart(*[FadeIn(VGroup(d, n)) for d, n in zip(dots, names)], lag_ratio=0.15), run_time=1.2)
        self.next_slide("""Where can you intercept this loop? Every framework offers the same eight points, because the loop only has eight
        places: before and after the whole invocation, before and after each model call, before and after each tool call,
        and whenever a message is added. A hook there can inspect, change or cancel. Guardrails, logging, cost limits,
        approval steps and tracing are all hooks at one of these dots; nothing else is needed.""")
        # --- one hook refuses a call
        self.play(dots[4].animate.set_color(PROBLEM), names[4].animate.set_color(PROBLEM), run_time=0.4)
        bar2 = highlight_line(cd, 4, PROBLEM)
        self.add(bar2)
        req = block("", TOOL, w=2.6, h=MINI_H, bare=True)
        mini.append(self, req, frm=mini_model[0], run_time=0.4)
        cross = label("delete_recording(...): refused by policy", 14, PROBLEM).move_to([-6.3, -2.45, 0], aligned_edge=LEFT)
        self.play(FadeIn(bar2), FadeIn(cross), run_time=0.5)
        mini.append(self, block("", PROBLEM, w=2.6, h=MINI_H, bare=True), frm=mini_cards[2], run_time=0.5)
        self.finish("""One hook in action. The model asks to delete a recording; a before-tool-call hook checks a policy and refuses.
        The tool never runs, and the refusal becomes the tool result, so the model learns it was refused and tells the user
        instead of pretending. This is the shape of every guardrail in an agent: the model asks, the application decides.""")
