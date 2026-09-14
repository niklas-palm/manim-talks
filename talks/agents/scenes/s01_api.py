"""Move 1: a plain application with one model call. The still picture: a user, an application whose code is three
lines, a model, and the camera API that code calls. A question is answered the way applications did it before agents:
the code fetches the latest frame, sends frame and question to the model, one call, one answer. Then a question the
code cannot serve, because the code decided what to fetch: the wall the next move removes."""
from lib.palette import *
from objects import *


class TheApi(TalkSlide):
    def construct(self):
        t = title(self, *TITLES["api"])   # the deck opens here: no title slide, the speaker introduces the talk over this picture
        st = stage()
        user, app, model, arrows, calls, tools = st["user"], st["app"], st["model"], st["arrows"], st["calls"], st["tools"]
        camera = device_box("camera API", CARD_YS[0])
        link = device_link(camera)
        src = app_code()
        srcl = label("the whole application: three lines", 14, MUTED).next_to(src, UP, buff=GAP_TIGHT).align_to(src, LEFT)
        msgs = messages()
        self.play(FadeIn(user), FadeIn(app), FadeIn(model), FadeIn(arrows), FadeIn(calls), FadeIn(tools), FadeIn(camera), FadeIn(link), FadeIn(src), FadeIn(srcl), run_time=0.8)
        self.next_slide("""This talk is for engineers who have used a chat assistant and want to see what an agent actually is. One
        sentence carries it: a model is called in a loop over a growing list of messages; it may answer with a request to run a
        tool instead of an answer; the application runs the tool, appends the result, and calls the model again. Everything on
        screen for the next fifteen minutes is one picture of that sentence, growing. But we start before agents, with a plain
        application. A user on the left. In the middle an application: a box that will hold a list of messages, and at the
        bottom its entire code, three lines: take a question, fetch the latest frame from camera two, send frame and question
        to the model, return the answer. A model top right. A camera API on the right, which that code calls. Two counters:
        model calls, and tool calls, which stay at zero for a while. Nothing here is an agent.""")
        # --- one question, answered the pre-agent way: fetch, then one model call
        bar = highlight_line(src, 1)
        msgs.append(self, message("user", "user · anyone in the backyard?"), frm=user, run_time=0.8)
        self.add(bar); self.play(FadeIn(bar), run_time=0.2)
        travel(self, src, camera, MUTED, text="frame(2)", edges=True, run_time=0.7)          # the request goes from the code to the API
        msgs.append(self, message("user", "user · [frame from camera 2] + the question"), frm=camera, run_time=0.9)   # the frame comes back into the list
        self.play(bar.animate.move_to(highlight_line(src, 2)), run_time=0.3)
        call_model(self, msgs, model, run_time=1.0)
        reply(self, msgs, model, "assistant", "assistant · yes, one person by the shed", run_time=0.7)
        one = label("one model call per question", 14, MODEL).next_to(app[0], DOWN, buff=GAP_TIGHT).align_to(app[0], LEFT)
        self.play(calls.to(1), FadeOut(bar), FadeIn(one), run_time=0.4)
        self.next_slide("""The user asks whether anyone is in the backyard. Follow the code. Line two runs: the application calls the camera
        API and gets the latest frame. The frame and the question become the list. Line three: one model call, the whole list
        goes in, and one reply comes back in words: yes, one person by the shed. One model call per question. This is a
        perfectly good application, and it is how most teams first used a model: the code decides what to fetch, fetches it,
        and asks the model to read it.""")
        # --- a question the code cannot serve
        msgs.append(self, message("user", "user · warm enough to open the door?"), frm=user, run_time=0.5)
        travel(self, src, camera, MUTED, text="frame(2)", edges=True, run_time=0.35)
        msgs.append(self, message("user", "user · [frame from camera 2] + the question"), frm=camera, run_time=0.5)
        call_model(self, msgs, model, run_time=0.6)
        reply(self, msgs, model, "assistant", "assistant · I cannot read a temperature from a frame", run_time=0.5)
        thermo = device_box("thermometer", CARD_YS[1])
        wall = label("no code path reaches it", 14, PROBLEM).next_to(thermo, DOWN, buff=GAP_TIGHT).align_to(thermo, LEFT)
        why = label("the code decided what to fetch, not the model", 14, PROBLEM).move_to(one, aligned_edge=LEFT)
        self.play(calls.to(2), FadeIn(thermo), FadeIn(wall), FadeOut(one), FadeIn(why), run_time=0.6)
        self.finish("""A second question: is it warm enough to open the door? The code does the only thing it knows, fetches a camera
        frame, and the model answers honestly that a frame has no temperature in it. A thermometer exists, right there, but no
        code path reaches it, because line two decided what to fetch before the model ever saw the question. Notice also what
        every call carried: the whole list, again; the model keeps nothing between calls. That is the wall an agent removes:
        the decision of what to look at has to move from the code to the model. The next move is about how, and it starts
        with a change of vocabulary.""")
