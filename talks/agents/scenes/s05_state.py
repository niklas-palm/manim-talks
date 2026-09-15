"""Move 5: the list is the only state. The list from move three, framed as the context window; every call sends all
of it; one long tool result overflows the window and the call is refused; then the two remedies, a sliding window and
summarisation."""
from lib.palette import *
from objects import *

class TheState(TalkSlide):
    def construct(self):
        # --- the last frame of move four, rebuilt: the stage, the compact agent inside the application with the eight rows of
        # move three's two questions, four model calls and two tool calls
        t = title_still(self, *TITLES["code"])
        st = stage()
        user, app, model, arrows, calls, tools = st["user"], st["app"], st["model"], st["arrows"], st["calls"], st["tools"]
        agent_c, lst_c, cards_c = agent_in_app(HIST_KINDS)
        calls.tracker.set_value(4); tools.tracker.set_value(2)
        self.add(user, app, model, arrows, calls, tools, agent_c, lst_c, cards_c)
        # --- the first change: the agent opens up, its rows become the messages they are, the cards take their place by the model
        agent = agent_frame()
        cards = tool_cards()
        msgs = put_history(messages(AGENT_LIST_TOP), HIST_LOOP)
        t = retitle(self, t, *TITLES["state"], extra=[ReplacementTransform(agent_c, agent), ReplacementTransform(lst_c, msgs), ReplacementTransform(cards_c, cards)], run_time=1.2)
        window = context_window(AGENT_LIST_TOP)
        self.play(FadeIn(window), run_time=0.6)
        self.next_slide("""The agent opens up so its list can be read: the same eight messages the two questions produced, inside the agent,
        inside the application; the tool cards take their place by the model, which is where their descriptions go on every
        call. Around the list a dashed frame: the context window, the most the
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
        sw = under_app("sliding window: the oldest exchange leaves, a tool call and its result together", app=app)
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
        sm = label(SUMMARY_LABEL, 14, MUTED).move_to(sw, aligned_edge=LEFT)
        self.play(FadeOut(sw), FadeIn(sm), run_time=0.4)
        self.finish("""The second remedy: summarisation. The oldest messages are replaced by one message that says what happened in
        them, written by a model call of its own, and the most recent messages stay word for word because that is where
        the model needs detail. The list is shorter and the door is still remembered, at the cost of a call and of whatever
        the summary left out. Everything beyond this point, sessions, memory stores, retrieval, is a way of deciding what
        goes into this list. That is the next talk. This one ends where it started: a model, a list of messages, and a
        loop.""")
