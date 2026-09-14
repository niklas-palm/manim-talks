"""Move 3: the loop. The full picture from move 1, now with the three tool cards in the functions column and their
devices at the right margin. The cards join the call; the model answers with a tool call instead of words; the
application runs it and appends the result; the model is called again and answers in words; the loop is drawn and a
second question runs through it at speed.

  Clicks: 1 the tool definitions join the call  2 the reply is a tool call  3 the application runs it and appends the
  result  4 called again with the longer list, the answer in words ends the turn  5 the loop drawn, then a second
  question at speed.
"""
from lib.palette import *
from objects import *


class TheLoop(TalkSlide):
    def construct(self):
        t = title(self, "The loop", "3  the loop")
        user, app, model, req, rep, rep_l = furniture()
        req_l = req_label("system prompt\n+ messages")
        calls, tcalls = counters()
        calls.tracker.set_value(3)
        msgs = Stack(LIST_X, LIST_TOP, h=BH, gap=BGAP)
        sysb = msg("system", "system · home surveillance assistant …").move_to([LIST_X, SYS_Y, 0])
        preload(msgs, [("user", "user · warm enough to open the door?"), ("assistant", "assistant · I cannot read a temperature from a frame")])
        msgs.blocks[1][0].set_stroke(PROBLEM)
        fn = function_node("query_camera", 0)
        devs = VGroup(*[device(n, k) for k, n in enumerate(DEVICES)])
        w = wall(fn, devs[1])
        self.add(user, app, model, req, rep, req_l, rep_l, calls, msgs, sysb, fn, devs[0], devs[1], w)
        # --- 1 the tool definitions join the call
        cards = VGroup(*[tool_card(*spec, row=k) for k, spec in enumerate(TOOLS)])
        req_l2 = req_label("system prompt + tools\n+ messages")
        self.play(FadeOut(w), ReplacementTransform(fn, cards[0]), run_time=0.5)
        self.play(FadeIn(cards[1:], lag_ratio=0.2), FadeIn(devs[2]), FadeOut(req_l), FadeIn(req_l2), FadeIn(tcalls), run_time=0.6)
        call_model(self, msgs, model, run_time=0.8, extra=[sysb, cards])
        self.play(calls.to(4), run_time=0.3)
        self.next_slide("""The three cards take the place of the plain function, each on the row of the device it reaches, and they go into
        the call next to the system prompt and the messages. Watch the whole bundle shrink into the model: system prompt,
        three definitions, every message. The model still cannot call anything; it has been told what the application could
        call on its behalf. The devices stay where they were, out of the model's reach, and they will stay there.""")
        # --- 2 the reply is a tool call
        self.play(cards[1][2].animate.set_color(TOOL), run_time=0.3)      # the description the model matched
        tu = reply(self, msgs, model, "tool_use", "assistant · tool_use query_temperature()")
        stop = label('stop_reason: "tool_use"', 14, TOOL).move_to(STOP_AT)
        self.play(FadeIn(stop), cards[1][2].animate.set_color(TEXT), run_time=0.4)
        self.next_slide("""And the reply is different in kind. Not words: a structured request, the yellow block. It names a tool,
        query_temperature, and fills in its arguments, none in this case. The reply carries a stop reason that says so:
        tool_use rather than end_turn. The model chose that tool by matching the question against the three descriptions; the
        one that matched lit up for a moment. Note what the model did not do. It did not read the thermometer. It asked.""")
        # --- 3 the application runs it and appends the result
        travel(self, cards[1], devs[1], TOOL, edges=True, run_time=0.45, flash=RESULT)
        travel(self, devs[1], cards[1], RESULT, edges=True, run_time=0.45)
        tr = msgs.append(self, msg("tool_result", "user · tool_result: 19 °C"), frm=cards[1], run_time=0.5)
        rl = label("the application ran it;\nthe model never does", 13, RESULT).next_to(cards[2], DOWN, buff=GAP).align_to(cards[2], LEFT)
        self.play(tcalls.to(1), FadeIn(rl), run_time=0.4)
        self.next_slide("""The application reads the request, runs the real function against the real thermometer, and gets 19 degrees.
        That answer becomes a message too, the teal block, a tool result tagged with the id of the request it answers, appended
        in the user's role, because from the model's point of view it is the world speaking. Nothing here needed the model;
        this step is ordinary code. It is also the step where every safety decision lives: the application can refuse, log,
        or ask a human before it runs anything.""")
        # --- 4 called again; the answer in words ends the turn
        call_model(self, msgs, model, run_time=0.8, extra=[sysb, cards])
        a = reply(self, msgs, model, "assistant", "assistant · 19 °C: yes, open it")
        stop2 = label('stop_reason: "end_turn"', 14, MODEL).move_to(STOP_AT)
        to_user(self, a, user, FadeOut(stop), FadeIn(stop2), calls.to(5), FadeOut(rl))
        self.next_slide("""Then the model is called again, with everything: the question, its own request, the result. Now it can answer in
        words, and it does: 19 degrees, yes, open it. The stop reason is end_turn, and that is what ends the loop. The user
        sees only the last block; the request and the result stayed inside the application, in the list. Compare with move
        one: the same question, the same thermometer, but this time the model decided to read it. Two model calls, one tool
        call, one answer.""")
        # --- 5 the loop, drawn; then a second question at speed
        loop = CurvedArrow([MODEL_L, REP_Y - 0.25, 0], [APP_R, REQ_Y - 0.15, 0], angle=-TAU / 3, color=TOOL, stroke_width=2.5, tip_length=0.18)
        ll = label("tool_use: run it, append\nthe result, call again", 13, TOOL).move_to([MODEL_L, 0.5, 0], aligned_edge=LEFT)
        ll2 = label("end_turn: stop", 13, MODEL).next_to(ll, DOWN, buff=0.06).align_to(ll, LEFT)
        self.play(Create(loop), FadeIn(ll), FadeIn(ll2), run_time=0.6)
        q2 = msg("user", "user · anyone in the backyard?")
        msgs.append(self, q2, frm=user, run_time=0.3)
        call_model(self, msgs, model, run_time=0.4, extra=[sysb, cards])
        reply(self, msgs, model, "tool_use", "assistant · tool_use query_camera(2, …)", run_time=0.3)
        self.play(calls.to(6), FadeOut(stop2), FadeIn(stop), run_time=0.2)
        travel(self, cards[0], devs[0], TOOL, edges=True, run_time=0.3, flash=RESULT)
        msgs.append(self, msg("tool_result", "user · tool_result: a person by the shed"), frm=cards[0], run_time=0.3)
        self.play(tcalls.to(2), run_time=0.2)
        call_model(self, msgs, model, run_time=0.4, extra=[sysb, cards])
        a2 = reply(self, msgs, model, "assistant", "assistant · yes, one person by the shed", run_time=0.3)
        to_user(self, a2, user, FadeOut(stop), FadeIn(stop2), calls.to(7), run_time=0.4)
        self.wait(0.3)
        self.finish("""That is the whole agent, and here it is drawn as the loop it is: call the model; if the reply is a tool request,
        run it, append the result, call again; if the reply is words, stop. Watch the first question from move one go round at
        speed: anyone in the backyard? This time the model asks for the camera, the application runs the same function it
        always had, the frame's answer goes into the list, the model answers. The loop runs as many times as the model asks;
        a real one also stops on a turn or token budget, so a confused model cannot run forever. Everything an agent framework
        adds sits on this loop. Next, the loop as code, because it is shorter than you think.""")
