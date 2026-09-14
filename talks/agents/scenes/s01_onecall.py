"""Move 1: one model call can only talk.

  Final frame: the user (left); the application box holding a system prompt block and the list of messages; the model
  box (right) with the request arrow above and the reply arrow below; a camera far right that nothing reaches; a
  counter of model calls.
  Clicks: 1 the user's question becomes the first message, the list goes into the model, an answer comes back in words
  2 the camera exists and the model has no path to it  3 what a call actually carries: a system prompt plus every message.
"""
from lib.palette import *
from objects import *

# the fixed furniture, shared by the scenes that draw this picture at full size
USER_AT, APP_AT, MODEL_AT = [-6.55, 1.3, 0], [-2.75, -0.35, 0], [3.05, 0.9, 0]
LIST_X, LIST_TOP, SYS_Y = -4.1, 1.25, 1.65
CARD_X, CARD_YS = -0.85, (1.2, 0.35, -0.5)
DEV_X, DEV_YS = 5.9, (1.7, 0.95, 0.2)
ARROW_Y_REQ, ARROW_Y_REP = 1.4, 0.45
APP_R, MODEL_L = 0.45, 1.85            # the application's right edge and the model's left edge: the arrows run between them


def furniture():
    """Everything a full-size scene starts from: user, application, model, the two arrows, the counters."""
    user = node("user", USER, w=1.0, h=0.5, size=15).move_to(USER_AT)
    app = app_box(6.4, 5.4).move_to(APP_AT)
    model = model_box().move_to(MODEL_AT)
    req = Arrow([APP_R, ARROW_Y_REQ, 0], [MODEL_L, ARROW_Y_REQ, 0], buff=0, color=MUTED, stroke_width=2.2, tip_length=0.18)
    rep = Arrow([MODEL_L, ARROW_Y_REP, 0], [APP_R, ARROW_Y_REP, 0], buff=0, color=MUTED, stroke_width=2.2, tip_length=0.18)
    req_l = label("all messages", 13, MUTED).move_to([1.15, 1.9, 0])
    rep_l = label("one reply", 13, MUTED).move_to([1.15, 0.2, 0])
    calls = Counter("model calls", 0, "", MODEL, size=22).move_to([2.0, -1.8, 0], aligned_edge=LEFT)
    tcalls = Counter("tool calls", 0, "", TOOL, size=22).move_to([4.6, -1.8, 0], aligned_edge=LEFT)
    return user, app, model, req, rep, req_l, rep_l, calls, tcalls


class OneCall(TalkSlide):
    def construct(self):
        t = title(self, "One model call can only talk", "1  one model call can only talk")
        user, app, model, req, rep, req_l, rep_l, calls, tcalls = furniture()
        msgs = Stack(LIST_X, LIST_TOP, gap=GAP)
        self.play(FadeIn(user), FadeIn(app), FadeIn(model), run_time=0.6)
        self.play(Create(req), Create(rep), FadeIn(req_l), FadeIn(rep_l), FadeIn(calls), run_time=0.6)
        # the question becomes the first message; the list goes into the model; words come back
        q = block("user · anyone in the backyard?", KIND["user"])
        msgs.append(self, q, frm=user, run_time=0.6)
        call_model(self, msgs, model, run_time=0.8)
        a = reply(self, msgs, model, "assistant", "assistant · I cannot see the backyard")
        out = a.copy()
        self.play(out.animate.scale(0.5).move_to(user.get_center()).set_opacity(0), calls.to(1), run_time=0.6)
        self.remove(out)
        self.next_slide("""Start with the simplest thing that can be called an assistant. A user types a question. The application puts it
        into a list of messages, the blue block, and sends the whole list to the model. The model reads it and produces one
        reply, in words, the violet block, which is appended to the same list and shown to the user. One call, one answer. It
        is also the end of the story: the model has read a sentence and written a sentence. It cannot look at anything.""")
        # the world exists; the model has no path to it
        cam = device("camera").move_to([DEV_X, DEV_YS[0], 0])
        gap = DashedLine(model[0].get_right() + RIGHT * 0.1, cam.get_left() + LEFT * 0.1, color=DIM, stroke_width=2)
        cross = VGroup(Line(UP * 0.14 + LEFT * 0.14, DOWN * 0.14 + RIGHT * 0.14), Line(UP * 0.14 + RIGHT * 0.14, DOWN * 0.14 + LEFT * 0.14)).set_stroke(PROBLEM, 3).move_to(gap.get_center())
        gl = label("the model produces text;\nit cannot call anything", 13, PROBLEM).next_to(cam, DOWN, buff=0.1)
        self.play(FadeIn(cam), Create(gap), run_time=0.5)
        self.play(FadeIn(cross), FadeIn(gl), run_time=0.4)
        self.next_slide("""There is a camera on the house. The model knows nothing about it and, more to the point, could not use it if it
        did: a language model takes text in and puts text out. Whatever the answer requires from the world, the world is on
        the other side of a wall the model cannot cross. Every agent framework exists to get across that wall, and the way
        across is not to make the model do more; it is to change what goes into the call.""")
        # what a call carries
        sysb = block("system · home surveillance assistant …", KIND["system"]).move_to([LIST_X, SYS_Y, 0])
        req_l2 = label("system prompt + all messages", 13, MUTED).move_to(req_l)
        self.play(FadeIn(sysb, shift=DOWN * 0.1), FadeOut(req_l), FadeIn(req_l2), run_time=0.5)
        call_model(self, msgs, model, run_time=0.7, extra=[sysb])
        self.play(calls.to(2), run_time=0.3)
        self.finish("""Look at what one call actually carries, because the whole trick lives there. Not just the user's question: the
        application also sends a system prompt, the grey block, the standing instructions for this assistant, and it sends
        every message so far, every time. The model has no memory between calls; the list is the memory, and it is resent in
        full. So if we want the model to reach the camera, the only place to say so is inside this call. That is the next
        move.""")
