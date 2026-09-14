"""Move 3: the same loop as code, and where to intercept it. The picture from move 2, drawn small on the left; the loop
as eight lines on the right. The code runs: each line lights as the picture does its step. Then the hooks: the seven
places an application can look, change or stop, marked on the lines; and one of them in action, refusing a tool call.

  Clicks: 1 the code appears  2 it runs, line by line, against the picture  3 the hook points  4 a hook refuses a call.
"""
from lib.palette import *
from objects import *

S = 0.85                                   # the reminder picture at this scale, on the left; its blocks are colour only
LINES = ["def loop(msgs, tools):",
         "    reply = model(system, tools, msgs)",
         "    msgs.append(reply)",
         '    if reply.stop_reason == "tool_use":',
         "        results = run(reply.tool_uses)",
         "        msgs.append(results)",
         "        return loop(msgs, tools)",
         "    return reply"]
HOOKS = [(0, "BeforeInvocation", -1), (1, "BeforeModelCall", -1), (1, "AfterModelCall", 1), (2, "MessageAdded", 0), (4, "BeforeToolCall", -1),
         (4, "AfterToolCall", 1), (5, "MessageAdded", 0), (7, "AfterInvocation", 1)]


class TheCode(TalkSlide):
    def construct(self):
        t = title(self, "The same loop as code, and where to intercept it", "3  the loop as code")
        # --- the picture, on the left half: a reminder of the last two moves, blocks as colours only
        user = node("user", USER, w=1.0, h=0.45, size=15).move_to([-6.3, 2.3, 0])
        app = box(4.0, 4.6, "application", MUTED, size=16, fill=0.04).move_to([-4.9, -0.45, 0])
        model = box(1.9, 1.3, "model", MODEL, size=18, fill=0.10).move_to([-1.7, 0.6, 0])
        card = node("query_camera", TOOL, w=1.9, h=0.45, size=14).move_to([-1.7, -0.55, 0])
        dev = node("camera", MUTED, w=1.9, h=0.45, size=14).move_to([-1.7, -1.55, 0])
        msgs = Stack(-4.9, 1.2, h=BH * S, gap=GAP * S)
        sysb = block("", KIND["system"], bare=True).scale(S).move_to([-4.9, 1.45, 0])
        self.play(FadeIn(user), FadeIn(app), FadeIn(model), FadeIn(card), FadeIn(dev), FadeIn(sysb), run_time=0.6)
        # --- 1 the code
        code = code_lines(LINES, size=18).move_to([-0.3, 2.0, 0], aligned_edge=UL)
        cl = label("the loop, eight lines; every agent framework is this plus bookkeeping", 14, MUTED).next_to(code, DOWN, buff=0.18).align_to(code, LEFT)
        self.play(LaggedStart(*[FadeIn(l, shift=RIGHT * 0.1) for l in code], lag_ratio=0.12), run_time=1.2)
        self.play(FadeIn(cl), run_time=0.3)
        self.next_slide("""Here is the loop from the last move written down, and it is eight lines. Send the system prompt, the tools and the
        messages to the model; append what comes back; if the reply asked for tools, run them, append the results and go
        round again; otherwise return the reply. Every agent framework you will meet is this function plus bookkeeping:
        streaming, retries, budgets, logging. The shape never changes, and once you can see it, you can read any of them.""")
        # --- 2 run it against the picture
        hl = Rectangle(width=code.width + 0.3, height=0.4, fill_color=HI, fill_opacity=0.12, stroke_width=0)

        def at(i):
            return hl.animate.move_to([code.get_left()[0] + code.width / 2, code[i].get_y(), 0])
        hl.move_to([code.get_left()[0] + code.width / 2, code[0].get_y(), 0])
        self.play(FadeIn(hl), run_time=0.2)
        q = block("", KIND["user"], bare=True).scale(S)
        msgs.append(self, q, frm=user, run_time=0.35)
        self.play(at(1), run_time=0.25); call_model(self, msgs, model, run_time=0.45, extra=[sysb, card])
        self.play(at(2), run_time=0.25); msgs.append(self, block("", KIND["tool_use"], bare=True).scale(S), frm=model[0], run_time=0.35)
        self.play(at(3), run_time=0.3)
        self.play(at(4), run_time=0.25); travel(self, card, dev, TOOL, run_time=0.3, flash=RESULT)
        self.play(at(5), run_time=0.25); msgs.append(self, block("", KIND["tool_result"], bare=True).scale(S), frm=card, run_time=0.35)
        self.play(at(6), run_time=0.3); self.play(at(0), run_time=0.3)
        self.play(at(1), run_time=0.25); call_model(self, msgs, model, run_time=0.45, extra=[sysb, card])
        self.play(at(2), run_time=0.25); a = msgs.append(self, block("", KIND["assistant"], bare=True).scale(S), frm=model[0], run_time=0.35)
        self.play(at(3), run_time=0.3); self.play(at(7), run_time=0.3)
        out = a.copy()
        self.play(out.animate.scale(0.5).move_to(user.get_center()).set_opacity(0), run_time=0.4)
        self.remove(out)
        self.next_slide("""Run it against the picture. The highlight is the line executing; the picture does what the line says. The
        question joins the list; invoke sends the list to the model; the reply is a tool request and is appended; the stop
        reason says tool_use, so the tools run, the camera answers, the result is appended, and the function calls itself
        with the longer list. Second time round the reply is words, the stop reason is end_turn, the function returns and the
        user gets the answer. Two passes through eight lines.""")
        # --- 3 the hook points
        self.play(FadeOut(hl), run_time=0.2)
        marks = VGroup()
        for i, name, side in HOOKS:
            y = code[i].get_y() + (0.14 if side < 0 else -0.14 if side > 0 else 0)
            dot = Dot(radius=0.06, color=RESULT).move_to([code.get_left()[0] - 0.28, y, 0])
            lab = label(name, 14, RESULT).move_to([code.get_left()[0] + code.width + 0.3, y, 0], aligned_edge=LEFT)
            marks.add(VGroup(dot, lab))
        hk = label("hooks: eight places to look, change or refuse", 14, RESULT).move_to(cl)
        self.play(FadeOut(cl), FadeIn(hk), LaggedStart(*[FadeIn(m) for m in marks], lag_ratio=0.1), run_time=1.0)
        self.next_slide("""Because the loop is this small, everything an application wants to do to an agent is a hook at one of these
        points: before and after the whole invocation, before and after each model call, before and after each tool call,
        and whenever a message is added. A hook can inspect the event, for logging and tracing; it can modify it, rewriting
        a tool's arguments or a result; and at some points it can cancel. Names differ between frameworks; the points do not,
        because they are the joints of the loop itself.""")
        # --- 4 a hook refuses a call
        q2 = block("", KIND["user"], bare=True).scale(S)
        msgs.append(self, q2, frm=user, run_time=0.35)
        call_model(self, msgs, model, run_time=0.45, extra=[sysb, card])
        msgs.append(self, block("", KIND["tool_use"], bare=True).scale(S), frm=model[0], run_time=0.35)
        gate = marks[4]
        self.play(gate[0].animate.set_color(PROBLEM).scale(1.8), gate[1].animate.set_color(PROBLEM), run_time=0.4)
        denied = block("", KIND["tool_result"], bare=True).scale(S)
        denied[0].set_stroke(PROBLEM); denied[1].set_fill(PROBLEM)
        msgs.append(self, denied, frm=gate[0], run_time=0.5)
        call_model(self, msgs, model, run_time=0.45, extra=[sysb, card])
        a2 = msgs.append(self, block("", KIND["assistant"], bare=True).scale(S), frm=model[0], run_time=0.35)
        out = a2.copy()
        self.play(out.animate.scale(0.5).move_to(user.get_center()).set_opacity(0), run_time=0.4)
        self.remove(out)
        self.finish("""One hook in action. The user asks for last night's recordings to be deleted, and the model, doing its job, asks
        for a tool that would. The before-tool-call hook is where the application's policy lives: it cancels the call, the
        camera is never touched, and what goes into the list instead is a result saying so. The model is called again, reads
        the refusal, and tells the user. The model was never in charge of the deletion; the loop was, and the loop is code
        you own. That is the design principle behind every guardrail and every approval prompt you have seen an agent show.""")
