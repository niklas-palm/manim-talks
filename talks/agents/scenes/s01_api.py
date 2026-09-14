"""Move 1: an application, an API, and one model call. Before any agent exists, the application already answers the
question: its own function calls the camera API, the frame goes into the prompt, the model answers from what it was
given. Then the wall: a different question, and the code fetches the wrong thing, because the code decided.

  Final frame: user (left column); the application box with the system block and the list of messages, and in its
  second column the application's own function; the model top right; the camera API and a thermometer at the right
  margin, on the rows of the functions that reach them; a wall between the function column and the thermometer.
  Clicks: 1 the question arrives, the function calls the camera API, frame and question go to the model, words come
  back  2 a different question: the same code fetches the same frame, the model cannot answer, the thermometer is out of
  reach  3 what a call carries: system prompt and every message, resent in full; the only place to change the answer
  is inside the call.
"""
from lib.palette import *
from objects import *


class TheApi(TalkSlide):
    def construct(self):
        t = title(self, "An application, an API, and one model call", "1  an application, an API, and one model call")
        user, app, model, req, rep, rep_l = furniture()
        req_l = req_label("system prompt\n+ messages")
        calls, tcalls = counters()
        msgs = Stack(LIST_X, LIST_TOP, h=BH, gap=BGAP)
        sysb = msg("system", "system · home surveillance assistant …").move_to([LIST_X, SYS_Y, 0])
        fn = function_node("query_camera", 0)
        api = device(DEVICES[0], 0)
        fl = label("the application's own function", 14, MUTED).next_to(fn, DOWN, buff=GAP_TIGHT).align_to(fn, LEFT)
        self.play(FadeIn(user), FadeIn(app), FadeIn(sysb), FadeIn(fn), FadeIn(fl), FadeIn(api), FadeIn(model), run_time=0.6)
        self.play(Create(req), Create(rep), FadeIn(req_l), FadeIn(rep_l), FadeIn(calls), run_time=0.5)
        # --- 1 the question; the function calls the API; frame and question go to the model; words come back
        q = msg("user", "user · anyone in the backyard?")
        msgs.append(self, q, frm=user, run_time=0.6)
        self.play(fn[0].animate.set_fill(MUTED, 0.35), run_time=0.2)
        travel(self, fn, api, TOOL, text="GET /cameras/2/frame", edges=True, run_time=0.6, flash=RESULT)
        travel(self, api, fn, RESULT, edges=True, run_time=0.5)
        frame = msgs.append(self, msg("tool_result", "user · [frame from camera 2] + the question"), frm=fn, run_time=0.5)
        self.play(fn[0].animate.set_fill(MUTED, 0.12), run_time=0.2)
        call_model(self, msgs, model, run_time=0.8, extra=[sysb])
        a = reply(self, msgs, model, "assistant", "assistant · yes, one person by the shed")
        to_user(self, a, user, calls.to(1))
        self.next_slide("""Start where every team starts, with an application that already works. A user asks whether anyone is in the
        backyard. The application has a function for that: query_camera calls the camera API, gets a frame back, and puts the
        frame and the question into a prompt, after a system prompt that says what this assistant is. The whole list goes to
        the model, and the model answers in words: yes, one person by the shed. Notice who did what. The application decided
        to call the camera, before it knew the question. The model only read what it was given and answered. It is a good
        application. It is not an agent.""")
        # --- 2 a different question; the code fetches the same thing; the model cannot answer
        thermo = device(DEVICES[1], 1)
        q2 = msg("user", "user · warm enough to open the door?")
        msgs.append(self, q2, frm=user, run_time=0.5)
        self.play(FadeIn(thermo), run_time=0.3)
        self.play(fn[0].animate.set_fill(MUTED, 0.35), run_time=0.2)
        travel(self, fn, api, TOOL, text="GET /cameras/2/frame", edges=True, run_time=0.5, flash=RESULT)
        travel(self, api, fn, RESULT, edges=True, run_time=0.4)
        msgs.append(self, msg("tool_result", "user · [frame from camera 2] + the question"), frm=fn, run_time=0.4)
        self.play(fn[0].animate.set_fill(MUTED, 0.12), run_time=0.2)
        call_model(self, msgs, model, run_time=0.6, extra=[sysb])
        a2 = reply(self, msgs, model, "assistant", "assistant · I cannot read a temperature from a frame")
        a2[0].set_stroke(PROBLEM)
        w = wall(fn, thermo)
        wl = label("the code decides what to fetch,\nnot the model", 14, PROBLEM).next_to(thermo, DOWN, buff=GAP_TIGHT).align_to(thermo, RIGHT)
        self.play(FadeIn(w), FadeIn(wl), calls.to(2), run_time=0.5)
        self.next_slide("""Now a different question: is it warm enough to open the door? The application runs the only code it has. It
        fetches a camera frame again, because that is what the code does for every question, and sends it with the question.
        The model, honestly, cannot read a temperature from a photograph. There is a thermometer on the house, but no code path
        reaches it, and the model could not ask for one if it wanted to: it produces text. This is the wall. The decision of
        what to fetch was made by a programmer before the question existed, and every new kind of question means new
        application code. The way over the wall is not a smarter model; it is to move that decision into the call.""")
        # --- 3 what a call carries
        req_l2 = req_label("system prompt +\nevery message")
        self.play(FadeOut(req_l), FadeIn(req_l2), run_time=0.3)
        call_model(self, msgs, model, run_time=0.9, extra=[sysb])
        self.play(calls.to(3), run_time=0.3)
        ml = label("no memory between calls: the list is the memory", 14, MUTED).next_to(app[0], DOWN, buff=GAP_TIGHT).align_to(app[0], LEFT)
        self.play(FadeIn(ml), run_time=0.3)
        self.finish("""Look at what one call carries, because the whole trick lives there. Not just the newest question: the
        application sends the system prompt, the grey block, and every message so far, every time, in full. The model keeps
        nothing between calls; the list is the memory, and the application owns it. So there is exactly one place where the
        model could be given the choice of what to fetch, and it is inside this call. The next move takes the function we
        already have and puts a description of it into the call. That is all a tool is.""")
