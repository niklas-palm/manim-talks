"""Move 5: the list is the only state. The list from move three, framed as the context window; every call sends all
of it; one long tool result overflows the window and the call is refused; then the two remedies, a sliding window and
summarisation."""
from lib.palette import *
from objects import *

WINDOW = 8   # messages the drawn window holds; a real window is counted in tokens (the note says so)


class TheState(TalkSlide):
    def construct(self):
        # --- the last frame of move four, rebuilt: the small picture with sixteen messages, the code, the hooks, the refusal
        from s04_code import SRC, HOOKS
        t = title_still(self, *TITLES["code"])
        kinds = [k for k, _ in HIST_LOOP] + ["tool_use", "tool_result", "tool_use", "tool_result", "assistant", "tool_use", "tool_result"]
        mini_model, mini, mini_cards = mini_stage(kinds)
        mini.blocks[-1].set_fill(PROBLEM, 0.16).set_stroke(PROBLEM); mini.blocks[-1][1].set_fill(PROBLEM, 0.95)
        cd = code(SRC, "python", 20).move_to([3.4, 0.35, 0])
        cl = label("the loop, eight lines: every agent framework is this plus bookkeeping", 14, MUTED).next_to(cd, DOWN, buff=GAP_TIGHT).align_to(cd, LEFT)
        hooks = VGroup()
        for i, name, dy in HOOKS:
            y = cd.lines[i].get_center()[1] + dy
            col = PROBLEM if name == "BeforeToolCall" else TEAL
            d = Dot(color=col, radius=0.06).move_to([cd.panel.get_left()[0] - 0.2, y, 0])
            hooks.add(d, label(name, 13, col).next_to(d, LEFT, buff=0.1))
        bar2 = highlight_line(cd, 4, PROBLEM)
        cross = label("delete_recording(...): refused by policy", 14, PROBLEM).move_to([-6.3, -2.45, 0], aligned_edge=LEFT)
        self.add(mini_model, mini, mini_cards, cd, bar2, cl, hooks, cross)
        # --- the first change: the code has done its job; the picture grows back to full size with the nine messages of move three
        st = stage()
        user, app, model, arrows, calls, tools = st["user"], st["app"], st["model"], st["arrows"], st["calls"], st["tools"]
        cards = tool_cards()
        msgs = put_history(messages(), HIST_LOOP)
        calls.tracker.set_value(4); tools.tracker.set_value(2)
        t = retitle(self, t, *TITLES["state"], extra=[FadeOut(cd), FadeOut(bar2), FadeOut(cl), FadeOut(hooks), FadeOut(cross),
                                                      ReplacementTransform(mini_model, model), ReplacementTransform(mini, msgs), ReplacementTransform(mini_cards, cards),
                                                      FadeIn(user), FadeIn(app), FadeIn(arrows), FadeIn(calls), FadeIn(tools)], run_time=1.2)
        window = DashedVMobject(RoundedRectangle(corner_radius=0.08, width=BW + 0.3, height=WINDOW * (BH + BGAP) + 0.1, stroke_color=PROBLEM, stroke_width=1.6, fill_opacity=0), num_dashes=60)
        window.move_to([LIST_X, LIST_TOP - (WINDOW * (BH + BGAP)) / 2 + BGAP / 2, 0])
        wl = label("context window", 14, PROBLEM).next_to(window, UP, buff=GAP_TIGHT).align_to(window, RIGHT)   # drawn as 8 messages, counted in tokens: the note says so
        self.play(FadeIn(window), FadeIn(wl), run_time=0.6)
        self.next_slide("""The list as move three left it, eight messages, and around it a dashed frame: the context window, the most the
        model can take in one call. Drawn here as eight messages; a real window is counted in tokens, a few hundred thousand
        for current models, and a long tool result or a large document eats it fast. The list is the only state the loop
        has, and this is its limit.""")
        # --- every call sends the whole list; one long result overflows it
        call_model(self, msgs, model, extra=cards, run_time=0.6)
        self.play(calls.to(5), run_time=0.2)
        big = message("tool_result", "user · tool_result: camera_history, 40,000 tokens of detections")   # the same shape as every message; its size is in its words, its problem is where it lands
        msgs.append(self, big, frm=cards[2], run_time=0.7)
        refused = stop_label("context window exceeded: the call is refused", model, PROBLEM)
        self.play(big[0].animate.set_stroke(PROBLEM, 2.0), big[1].animate.set_fill(PROBLEM, 0.95), FadeIn(refused), run_time=0.6)
        self.play(tools.to(3), run_time=0.2)
        self.next_slide("""Every call sends the whole list, so the list is also what every call costs. Then one tool result arrives that is
        far larger than the others: the camera archive returns forty thousand tokens of detections. It does not fit under
        the window, and the next call is refused; the model never sees it. Nothing in the loop protects against this,
        because the loop only appends. Something has to shorten the list, and there are two honest ways.""")
        # --- sliding window: the oldest exchange leaves, as a unit
        gone = msgs.blocks[0:4]                      # the first exchange: question, tool call, result, answer
        keep = msgs.blocks[4:]
        self.play(*[b.animate.set_opacity(0.25) for b in gone], run_time=0.4)
        self.play(*[FadeOut(b, shift=LEFT * 0.4) for b in gone], run_time=0.5)
        for b in gone:
            msgs.remove(b)
        msgs.blocks = keep
        self.play(big[0].animate.set_stroke(RESULT, 1.4), big[1].animate.set_fill(RESULT, 0.95), FadeOut(refused), run_time=0.3)   # members first, the group move after: never both in one play
        self.play(*[b.animate.move_to(msgs.slot(i)) for i, b in enumerate(keep)], run_time=0.8)
        sw = label("sliding window: the oldest exchange leaves, a tool call and its result together", 14, MUTED).next_to(app[0], DOWN, buff=GAP_TIGHT).align_to(app[0], LEFT)
        self.play(FadeIn(sw), run_time=0.4)
        self.next_slide("""The first remedy: a sliding window. The oldest messages leave, and they leave in pairs: a tool call and its result
        go together, because a result without its call, or a call without its result, is a malformed conversation that
        the model will reject. Now the big result fits. The price is that the model has forgotten the door was opened.""")
        # --- summarisation: the oldest become one message
        old = msgs.blocks[0:3]                       # the second question, its tool call and its result
        summary = message("summary", "summary · door opened at 19 °C; one person by the shed").move_to(msgs.slot(0))
        self.play(ReplacementTransform(VGroup(*old), summary), run_time=0.9)
        for b in old:
            if b in msgs.submobjects:
                msgs.remove(b)
        msgs.blocks = [summary] + msgs.blocks[3:]
        msgs.add(summary)
        self.play(*[b.animate.move_to(msgs.slot(i)) for i, b in enumerate(msgs.blocks)], run_time=0.7)
        sm = label("summarisation: the oldest messages become one; the most recent stay verbatim", 14, MUTED).move_to(sw, aligned_edge=LEFT)
        self.play(FadeOut(sw), FadeIn(sm), run_time=0.4)
        self.finish("""The second remedy: summarisation. The oldest messages are replaced by one message that says what happened in
        them, written by a model call of its own, and the most recent messages stay word for word because that is where
        the model needs detail. The list is shorter and the door is still remembered, at the cost of a call and of whatever
        the summary left out. Everything beyond this point, sessions, memory stores, retrieval, is a way of deciding what
        goes into this list. That is the next talk. This one ends where it started: a model, a list of messages, and a
        loop.""")
