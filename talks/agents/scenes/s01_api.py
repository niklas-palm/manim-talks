"""Move 1: an application, an API, and one model call. The still picture first: a user, an application holding an empty
list of messages, a model, and a camera API the application's own code calls. Then a question is answered the way
applications did it before agents: the code fetches a frame, the model describes it. Then a question the code cannot
serve, because the code, not the model, decided what to fetch. Then what every call carries."""
from lib.palette import *
from objects import *


class TheApi(TalkSlide):
    def construct(self):
        t = title(self, "An application, an API, and one model call", "1  an application, an API, one model call")
        st = stage()
        user, app, model, arrows, calls, tools = st["user"], st["app"], st["model"], st["arrows"], st["calls"], st["tools"]
        camera = device_box("camera API", CARD_YS[0])
        link = device_link(camera)
        msgs = messages()
        self.play(FadeIn(user), FadeIn(app), FadeIn(model), FadeIn(arrows), FadeIn(calls), FadeIn(tools), FadeIn(camera), FadeIn(link), run_time=0.8)
        self.next_slide("""The picture for the whole talk, still. A user on the left. An application in the middle: a box that will hold a
        list of messages. A model top right: every call sends it the system prompt and every message, and one reply comes
        back. On the right, a camera API, which the application's own code knows how to call. Two counters at the bottom:
        model calls, and tool calls, which stay at zero for a while. Nothing here is an agent yet.""")
        # --- one question, answered the pre-agent way
        msgs.append(self, message("user", "user · anyone in the backyard?"), frm=user, run_time=0.8)
        travel(self, app[0], camera, MUTED, text="frame(2)", edges=True, run_time=0.7)
        travel(self, camera, app[0], RESULT, text="image", edges=True, run_time=0.7)
        msgs.append(self, message("user", "user · [frame from camera 2] + the question"), frm=camera, run_time=0.7)
        call_model(self, msgs, model, run_time=1.0)
        reply(self, msgs, model, "assistant", "assistant · yes, one person by the shed", run_time=0.7)
        self.play(calls.to(1), run_time=0.4)
        self.next_slide("""The user asks whether anyone is in the backyard. Watch the order. The question becomes the first message. The
        application's code calls the camera API, gets a frame, and puts the frame and the question into the list as a
        second message. Then the whole list goes into the model, and one reply comes back in words: yes, one person by the
        shed. One model call. This is how most applications used models before agents: the code decided what to fetch,
        fetched it, and asked the model to read it.""")
        # --- a question the code cannot serve
        msgs.append(self, message("user", "user · warm enough to open the door?"), frm=user, run_time=0.5)
        travel(self, app[0], camera, MUTED, text="frame(2)", edges=True, run_time=0.35)
        travel(self, camera, app[0], RESULT, text="image", edges=True, run_time=0.35)
        msgs.append(self, message("user", "user · [frame from camera 2] + the question"), frm=camera, run_time=0.4)
        call_model(self, msgs, model, run_time=0.6)
        reply(self, msgs, model, "assistant", "assistant · I cannot read a temperature from a frame", run_time=0.5)
        thermo = device_box("thermometer", CARD_YS[1])
        wall = label("no code path reaches it", 14, PROBLEM).next_to(thermo, DOWN, buff=GAP_TIGHT).align_to(thermo, LEFT)
        why = label("the code decided what to fetch, not the model", 14, PROBLEM).next_to(app[0], DOWN, buff=GAP_TIGHT).align_to(app[0], LEFT)
        self.play(calls.to(2), FadeIn(thermo), FadeIn(wall), FadeIn(why), run_time=0.6)
        self.next_slide("""A second question: is it warm enough to open the door? The code does what it always does, fetches a camera frame,
        and the model answers honestly that a frame has no temperature in it. A thermometer exists, right there, but no
        code path reaches it, because the code decided what to fetch before the model ever saw the question. That is the
        wall an agent removes: the decision of what to look at has to move from the code to the model. Everything in the
        next move is about how.""")
        # --- what every call carries
        mem = label("the list is the only memory: every call sends all of it", 14, MUTED).move_to(why, aligned_edge=LEFT)
        self.play(FadeOut(why), FadeOut(wall), FadeIn(mem), run_time=0.4)
        call_model(self, msgs, model, run_time=0.9)
        self.play(calls.to(3), run_time=0.3)
        self.finish("""One more thing to see before the wall comes down, because the rest depends on it. The model keeps nothing between
        calls. Each call sends the system prompt and every message so far, the whole list, and the reply is computed from
        that and nothing else. So the list is the only memory the application has, and the only place a conversation
        exists. Hold on to that: it is what the loop will grow, and it is what runs out at the end of the talk.""")
