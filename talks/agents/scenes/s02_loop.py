"""Move 2: tools, and the loop. The picture from move 1 grows: tool definitions appear inside the application, the model
answers with a tool call instead of words, the application runs the tool and appends the result, the model is called
again, and the loop closes when it answers in words.

  Clicks: 1 tool definitions join the call  2 where a definition comes from  3 the reply is a tool call  4 the application
  runs it and appends the result  5 called again with the longer list, the answer in words ends the turn  6 the loop
  drawn, then a second question runs through it at speed.
"""
from lib.palette import *
from objects import *
from s01_onecall import furniture, LIST_X, LIST_TOP, SYS_Y, CARD_X, CARD_YS, DEV_X, DEV_YS, MODEL_L, APP_R, MODEL_AT

TOOLS = [("query_camera", "what a camera sees right now", "camera: int, question: str"),
         ("query_temperature", "outdoor temperature in °C", "no arguments"),
         ("camera_history", "recordings from a camera since a time", "camera: int, since: str")]
DEVICES = ["camera", "thermometer", "camera archive"]


class TheLoop(TalkSlide):
    def construct(self):
        t = title(self, "Tools, and the loop", "2  tools, and the loop")
        user, app, model, req, rep, req_l, rep_l, calls, tcalls = furniture()
        req_l = label("system prompt + all messages", 13, MUTED).move_to(req_l)
        msgs = Stack(LIST_X, LIST_TOP, gap=GAP)
        sysb = block("system · home surveillance assistant …", KIND["system"]).move_to([LIST_X, SYS_Y, 0])
        for kind, text in (("user", "user · anyone in the backyard?"), ("assistant", "assistant · I cannot see the backyard")):
            b = block(text, KIND[kind]).move_to(msgs.slot(len(msgs.blocks))); msgs.blocks.append(b); msgs.add(b)
        calls.tracker.set_value(2)
        cam = device(DEVICES[0]).move_to([DEV_X, DEV_YS[0], 0])
        gap = DashedLine(model[0].get_right() + RIGHT * 0.1, cam.get_left() + LEFT * 0.1, color=DIM, stroke_width=2)
        cross = VGroup(Line(UP * 0.14 + LEFT * 0.14, DOWN * 0.14 + RIGHT * 0.14), Line(UP * 0.14 + RIGHT * 0.14, DOWN * 0.14 + LEFT * 0.14)).set_stroke(PROBLEM, 3).move_to(gap.get_center())
        self.add(user, app, model, req, rep, req_l, rep_l, calls, msgs, sysb, cam, gap, cross)
        # --- 1 tool definitions join the call
        cards = VGroup(*[tool_card(*spec).move_to([CARD_X, y, 0]) for spec, y in zip(TOOLS, CARD_YS)])
        devs = VGroup(cam, *[device(n).move_to([DEV_X, y, 0]) for n, y in zip(DEVICES[1:], DEV_YS[1:])])
        tl = label("tools: name, description,\ninput schema", 13, TOOL).next_to(cards, DOWN, buff=0.12)
        req_l2 = label("system prompt + tools + all messages", 13, MUTED).move_to(req_l)
        self.play(FadeOut(gap), FadeOut(cross), FadeIn(cards, lag_ratio=0.2), FadeIn(tl), FadeIn(devs[1:]), FadeOut(req_l), FadeIn(req_l2), FadeIn(tcalls), run_time=0.9)
        self.next_slide("""The application declares tools. A tool definition is three things and nothing more: a name, a description in
        plain words, and the schema of its arguments. The yellow cards are the definitions of three functions the application
        can run: ask a camera what it sees, read the outdoor temperature, fetch recordings. They go into the call next to the
        system prompt and the messages. The model still cannot call anything; it has only been told what the application
        could call on its behalf. The devices on the right are still out of the model's reach, and stay so.""")
        # --- 2 where a definition comes from: the function itself
        code = code_lines(["@tool", "def query_camera(camera: int, question: str):", '    """What a camera sees right now."""'], size=14)
        code[1].set_color_by_t2c({"query_camera": TOOL, "camera: int, question: str": MUTED})
        code[2].set_color(TEXT)
        code.move_to([MODEL_L, -0.5, 0], aligned_edge=LEFT)
        cl = label("name from the function, description from the docstring,\nschema from the type hints", 13, MUTED).next_to(code, DOWN, buff=0.1).align_to(code, LEFT)
        self.play(FadeIn(code), FadeIn(cl), cards[0][0].animate.set_fill(TOOL, 0.3), run_time=0.6)
        self.play(cards[0][0].animate.set_fill(TOOL, 0.10), run_time=0.3)
        self.next_slide("""Where does a definition come from? From the function, usually by a decorator: the function's name becomes the
        tool's name, the first paragraph of its docstring becomes the description, and the type hints become the input
        schema. The colours on the code are the colours on the card. This is worth a pause, because the description is the
        only thing the model has to decide with. A vague docstring is a vague tool. The best advice in the field is to write
        it as you would for a new colleague: what it does, when to use it, what the arguments mean.""")
        self.play(FadeOut(code), FadeOut(cl), run_time=0.4)
        # --- 3 the reply is a tool call
        q = block("user · anyone in the backyard?", KIND["user"])
        msgs.append(self, q, frm=user, run_time=0.5)
        call_model(self, msgs, model, run_time=0.8, extra=[sysb, cards])
        self.play(cards[0][2].animate.set_color(TOOL), run_time=0.3)     # the description is what the model matched
        tu = reply(self, msgs, model, "tool_use", 'assistant · tool_use query_camera(2, …)')
        stop = label('stop_reason: "tool_use"', 14, TOOL).move_to([MODEL_AT[0], -0.2, 0])
        self.play(FadeIn(stop), calls.to(3), cards[0][2].animate.set_color(TEXT), run_time=0.4)
        self.next_slide("""The user asks again. The same list goes in, now with the tool definitions, and the model's reply is different in
        kind: not words, a structured request, the yellow block. It names a tool and fills in the arguments: camera two, the
        question. The reply carries a stop reason that says so, tool_use rather than end_turn. The model chose that tool by
        matching the question against the descriptions; the description that matched lit up for a moment. Note what the model
        did not do: it did not call anything. It asked.""")
        # --- 4 the application runs it
        travel(self, cards[0], devs[0], TOOL, run_time=0.45, flash=RESULT)
        travel(self, devs[0], cards[0], RESULT, run_time=0.45)
        tr = msgs.append(self, block("user · tool_result: a person by the shed", KIND["tool_result"]), frm=cards[0], run_time=0.5)
        rl = label("the application ran it;\nthe model never does", 13, RESULT).move_to(tl)
        self.play(tcalls.to(1), FadeOut(tl), FadeIn(rl), run_time=0.4)
        self.next_slide("""The application reads the request, runs the real function against the real camera, and gets an answer back: a
        person by the shed. That answer becomes a message too, the teal block, a tool result tagged with the id of the request
        it answers, and it is appended to the list in the user's role, because from the model's point of view it is the world
        speaking. Nothing here needed the model; this step is ordinary code. It is also the step where every safety decision
        lives: the application can refuse, log, or ask a human before it runs anything.""")
        # --- 5 called again, the longer list; the answer in words ends the turn
        call_model(self, msgs, model, run_time=0.8, extra=[sysb, cards])
        a = reply(self, msgs, model, "assistant", "assistant · yes, one person by the shed")
        stop2 = label('stop_reason: "end_turn"', 14, MODEL).move_to(stop)
        out = a.copy()
        self.play(FadeOut(stop), FadeIn(stop2), out.animate.scale(0.5).move_to(user.get_center()).set_opacity(0), calls.to(4), FadeOut(rl), run_time=0.6)
        self.remove(out)
        self.next_slide("""Then the model is called again, with everything: the question, its own tool request, the result. Now it can
        answer in words, and it does: yes, one person by the shed. The stop reason is end_turn, and that is what ends the
        loop. The user sees only the last block; the whole exchange in between, the request and the result, happened inside
        the application and stays in the list. Two model calls, one tool call, one answer.""")
        # --- 6 the loop, drawn; then a second question at speed
        loop = CurvedArrow([MODEL_L, 0.05, 0], [APP_R, 1.05, 0], angle=-TAU / 3, color=TOOL, stroke_width=2.5, tip_length=0.18)
        ll = label("tool_use: run it, append the result, call again", 13, TOOL).move_to([MODEL_L, -0.9, 0], aligned_edge=LEFT)
        ll2 = label("end_turn: stop", 13, MODEL).next_to(ll, DOWN, buff=0.06).align_to(ll, LEFT)
        self.play(Create(loop), FadeIn(ll), FadeIn(ll2), run_time=0.6)
        q2 = block("user · warm enough to open the door?", KIND["user"])
        msgs.append(self, q2, frm=user, run_time=0.3)
        call_model(self, msgs, model, run_time=0.4, extra=[sysb, cards])
        reply(self, msgs, model, "tool_use", "assistant · tool_use query_temperature()", run_time=0.3)
        self.play(calls.to(5), FadeOut(stop2), FadeIn(stop), run_time=0.2)
        travel(self, cards[1], devs[1], TOOL, run_time=0.3, flash=RESULT)
        msgs.append(self, block("user · tool_result: 19 °C", KIND["tool_result"]), frm=cards[1], run_time=0.3)
        self.play(tcalls.to(2), run_time=0.2)
        call_model(self, msgs, model, run_time=0.4, extra=[sysb, cards])
        a2 = reply(self, msgs, model, "assistant", "assistant · 19 °C: yes, open it", run_time=0.3)
        out = a2.copy()
        self.play(FadeOut(stop), FadeIn(stop2), out.animate.scale(0.5).move_to(user.get_center()).set_opacity(0), calls.to(6), run_time=0.4)
        self.remove(out)
        self.finish("""That is the whole agent, and here it is drawn as the loop it is: call the model; if the reply is a tool request,
        run it, append the result, call again; if the reply is words, stop. Watch a second question go round at speed: warm
        enough to leave the door open? The model asks for the temperature, the application reads the thermometer, 19 degrees
        goes into the list, the model answers. The loop runs as many times as the model asks; a real one also stops on a
        turn or token budget, so a confused model cannot run forever. Everything an agent framework adds sits on this loop.
        Next, the loop as code, because it is shorter than you think.""")
