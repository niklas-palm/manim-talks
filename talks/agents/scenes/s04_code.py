"""Move 4: the same loop as code, and where to intercept it. The picture from move 3, drawn at reminder size on the
left half; the loop as eight highlighted lines on the right. The code runs: a bar walks the lines while the picture
does each step. Then the hooks, marked on the lines; and one of them refusing a tool call.

  Clicks: 1 the code appears  2 it runs, line by line, against the picture  3 the hook points  4 a hook refuses a call.
"""
from lib.palette import *
from objects import *

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
# the reminder picture, left half: the same objects, three quarters size, blocks as colour only
PX_USER, PX_APP, PX_MODEL, PX_CARD, PX_DEV = [-5.95, 1.3, 0], [-3.75, -0.15, 0], [-1.3, 1.6, 0], [-1.3, 0.2, 0], [-1.3, -1.1, 0]
LX, LTOP, S = -3.75, 1.5, 0.75


class TheCode(TalkSlide):
    def construct(self):
        t = title(self, "The same loop as code, and where to intercept it", "4  the loop as code")
        user = node("user", USER, w=0.9, h=0.45, size=15).move_to(PX_USER)
        app = box(2.9, 4.5, "application", MUTED, size=16, fill=0.04, name_align="left").move_to(PX_APP)
        model = box(1.6, 1.1, "model", MODEL, size=18, fill=0.10).move_to(PX_MODEL)
        card = node("query_camera", TOOL, w=1.6, h=0.45, size=13).move_to(PX_CARD)
        dev = node("camera API", MUTED, w=1.6, h=0.45, size=13).move_to(PX_DEV)
        msgs = Stack(LX, LTOP, h=BH * S, gap=BGAP)
        sysb = block("", KIND["system"], w=BW * S, h=BH * S, bare=True).move_to([LX, 1.72, 0])
        self.play(FadeIn(user), FadeIn(app), FadeIn(model), FadeIn(card), FadeIn(dev), FadeIn(sysb), run_time=0.6)
        # --- 1 the code
        c = code(LINES, "python", 15)
        for k, ln in enumerate(c.lines):          # open the line pitch so two hook labels fit beside one line
            ln.shift(DOWN * 0.13 * k)
        c.panel.stretch_to_fit_height(c.lines.height + 0.7).move_to(c.lines.get_center())
        c.move_to([0.2, 2.35, 0], aligned_edge=UL)
        cl = label("the loop, eight lines; every framework is this plus bookkeeping", 14, MUTED).next_to(c, DOWN, buff=GAP).align_to(c, LEFT)
        self.play(FadeIn(c), run_time=0.8)
        self.play(FadeIn(cl), run_time=0.3)
        self.next_slide("""Here is the loop from the last move written down, and it is eight lines. Send the system prompt, the tools and the
        messages to the model; append what comes back; if the reply asked for tools, run them, append the results and go
        round again; otherwise return the reply. Every agent framework you will meet is this function plus bookkeeping:
        streaming, retries, budgets, logging. The shape never changes, and once you can see it, you can read any of them.""")
        # --- 2 run it against the picture
        bar = highlight_line(c, 0)
        self.play(FadeIn(bar), run_time=0.2)
        small_block = lambda kind: block("", KIND[kind], w=BW * S, h=BH * S, bare=True)

        def at(i, rt=0.25):
            self.play(bar.animate.move_to(highlight_line(c, i)), run_time=rt)
        msgs.append(self, small_block("user"), frm=user, run_time=0.35)
        at(1); call_model(self, msgs, model, run_time=0.45, extra=[sysb, card])
        at(2); msgs.append(self, small_block("tool_use"), frm=model[0], run_time=0.35)
        at(3, 0.3)
        at(4); travel(self, card, dev, TOOL, run_time=0.3, flash=RESULT)
        at(5); msgs.append(self, small_block("tool_result"), frm=card, run_time=0.35)
        at(6, 0.3); at(0, 0.3)
        at(1); call_model(self, msgs, model, run_time=0.45, extra=[sysb, card])
        at(2); a = msgs.append(self, small_block("assistant"), frm=model[0], run_time=0.35)
        at(3, 0.3); at(7, 0.3)
        to_user(self, a, user, run_time=0.4)
        self.next_slide("""Run it against the picture. The bar is the line executing; the picture does what the line says. The question
        joins the list; the call sends the list to the model; the reply is a tool request and is appended; the stop reason
        says tool_use, so the tool runs, the camera answers, the result is appended, and the function calls itself with the
        longer list. Second time round the reply is words, the stop reason is end_turn, the function returns and the user
        gets the answer. Two passes through eight lines.""")
        # --- 3 the hook points
        self.play(FadeOut(bar), run_time=0.2)
        marks = VGroup()
        right = c.panel.get_right()[0] + GAP
        for i, name, side in HOOKS:
            y = c.lines[i].get_y() + (0.16 if side < 0 else -0.16 if side > 0 else 0)
            dot = Dot(radius=0.055, color=RESULT).move_to([c.panel.get_left()[0] - GAP_TIGHT, y, 0])
            lab = label(name, 12, RESULT).move_to([right, y, 0], aligned_edge=LEFT)
            marks.add(VGroup(dot, lab))
        hk = label("hooks: eight places to look, change or refuse", 14, RESULT).move_to(cl, aligned_edge=LEFT)
        self.play(FadeOut(cl), FadeIn(hk), LaggedStart(*[FadeIn(m) for m in marks], lag_ratio=0.1), run_time=1.0)
        self.next_slide("""Because the loop is this small, everything an application wants to do to an agent is a hook at one of these
        points: before and after the whole invocation, before and after each model call, before and after each tool call,
        and whenever a message is added. A hook can inspect the event, for logging and tracing; it can modify it, rewriting
        a tool's arguments or a result; and at some points it can cancel. Names differ between frameworks; the points do not,
        because they are the joints of the loop itself.""")
        # --- 4 a hook refuses a call
        msgs.append(self, small_block("user"), frm=user, run_time=0.35)
        call_model(self, msgs, model, run_time=0.45, extra=[sysb, card])
        msgs.append(self, small_block("tool_use"), frm=model[0], run_time=0.35)
        gate = marks[4]
        self.play(gate[0].animate.set_color(PROBLEM).scale(1.8), gate[1].animate.set_color(PROBLEM), run_time=0.4)
        denied = small_block("tool_result")
        denied[0].set_stroke(PROBLEM); denied[1].set_fill(PROBLEM)
        msgs.append(self, denied, frm=gate[0], run_time=0.5)
        call_model(self, msgs, model, run_time=0.45, extra=[sysb, card])
        a2 = msgs.append(self, small_block("assistant"), frm=model[0], run_time=0.35)
        to_user(self, a2, user, run_time=0.4)
        self.wait(0.2)
        self.finish("""One hook in action. The user asks for last night's recordings to be deleted, and the model, doing its job, asks
        for a tool that would. The before-tool-call hook is where the application's policy lives: it cancels the call, the
        archive is never touched, and what goes into the list instead is a result saying so. The model is called again, reads
        the refusal, and tells the user. The model was never in charge of the deletion; the loop was, and the loop is code
        you own. That is the design principle behind every guardrail and every approval prompt you have seen an agent show.""")
