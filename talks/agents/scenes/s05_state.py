"""Move 5: the list is the only state. The full picture again; the list column is framed as the context window, and the
list grows turn by turn until it no longer fits. Two remedies, drawn on the list itself.

  Clicks: 1 every call sends the whole list; one more turn and the window is nearly full  2 a long result overflows it,
  the call is refused  3 sliding window: the oldest messages go, a call and its result together  4 summarisation: the
  oldest messages become one block.
"""
from lib.palette import *
from objects import *

CAP = 8   # the window drawn as room for this many messages


class TheState(TalkSlide):
    def construct(self):
        t = title(self, "The list is the only state", "5  the list is the only state")
        user, app, model, req, rep, rep_l = furniture()
        req_l = req_label("system prompt + tools\n+ messages")
        calls, tcalls, sent = counters(with_sent=True)
        msgs = Stack(LIST_X, LIST_TOP, h=BH, gap=BGAP)
        sysb = msg("system", "system · home surveillance assistant …").move_to([LIST_X, SYS_Y, 0])
        preload(msgs, [("user", "user · anyone in the backyard?"), ("tool_use", "assistant · tool_use query_camera(2, …)"),
                       ("tool_result", "user · tool_result: a person by the shed"), ("assistant", "assistant · yes, one person by the shed")])
        cards = VGroup(*[tool_card(*spec, row=k) for k, spec in enumerate(TOOLS)])
        devs = VGroup(*[device(n, k) for k, n in enumerate(DEVICES)])
        calls.tracker.set_value(2); tcalls.tracker.set_value(1); sent.tracker.set_value(5)
        self.add(user, app, model, req, rep, req_l, rep_l, calls, tcalls, sent, msgs, sysb, cards, devs)
        # --- 1 the window, and one more turn
        top = SYS_Y + BH / 2 + 0.06
        bottom = msgs.slot(CAP - 1)[1] - BH / 2 - 0.06
        win = DashedVMobject(RoundedRectangle(corner_radius=0.08, width=BW + 0.3, height=top - bottom, stroke_color=RESULT, stroke_width=1.6, fill_opacity=0)
                             .move_to([LIST_X, (top + bottom) / 2, 0]), num_dashes=60)
        wl = label("context window:\ndrawn as room for 8 messages", 13, RESULT).move_to([CARD_X - CARD_W / 2, -2.0, 0], aligned_edge=LEFT)
        self.play(Create(win), FadeIn(wl), run_time=0.7)
        call_model(self, msgs, model, run_time=0.7, extra=[sysb, cards])
        self.play(calls.to(3), run_time=0.2)
        msgs.append(self, msg("user", "user · warm enough to open the door?"), frm=user, run_time=0.3)
        call_model(self, msgs, model, run_time=0.35, extra=[sysb, cards]); self.play(calls.to(4), sent.to(len(msgs.blocks) + 1), run_time=0.2)
        reply(self, msgs, model, "tool_use", "assistant · tool_use query_temperature()", run_time=0.3)
        travel(self, cards[1], devs[1], TOOL, edges=True, run_time=0.3, flash=RESULT)
        msgs.append(self, msg("tool_result", "user · tool_result: 19 °C"), frm=cards[1], run_time=0.3); self.play(tcalls.to(2), run_time=0.15)
        call_model(self, msgs, model, run_time=0.35, extra=[sysb, cards]); self.play(calls.to(5), sent.to(len(msgs.blocks) + 1), run_time=0.2)
        reply(self, msgs, model, "assistant", "assistant · 19 °C: yes, open it", run_time=0.3)
        self.wait(0.3)
        self.next_slide("""One thing carries over from call to call, and it is the list. The model keeps nothing; every call sends the system
        prompt, the tools and every message so far, and the third counter says how many. That list has to fit the model's
        context window, drawn here as room for eight messages; a real window is 200,000 tokens on Claude Haiku 4.5 and a
        million on Claude Opus 5, but a tool result can be a whole document and an agent can run for hundreds of turns, so the window fills faster than it sounds.
        Watch one more question go round: four more messages, and the window is full.""")
        # --- 2 overflow
        over = []
        msgs.append(self, msg("user", "user · who was here yesterday afternoon?"), frm=user, run_time=0.3)
        call_model(self, msgs, model, run_time=0.35, extra=[sysb, cards]); self.play(calls.to(6), sent.to(len(msgs.blocks) + 1), run_time=0.2)
        over.append(reply(self, msgs, model, "tool_use", "assistant · tool_use camera_history(1, …)", run_time=0.3))
        travel(self, cards[2], devs[2], TOOL, edges=True, run_time=0.3, flash=RESULT)
        over.append(msgs.append(self, msg("tool_result", "user · tool_result: 3 recordings, 14 min …"), frm=cards[2], run_time=0.3))
        self.play(tcalls.to(3), run_time=0.15)
        ghost = VGroup(msgs.copy(), sysb.copy(), cards.copy()).set_opacity(0.55)
        self.play(ghost.animate.scale(0.22).move_to(model[0].get_center()), run_time=0.6)
        ol = label("more than the window holds: the call is refused", 14, PROBLEM).move_to(STOP_AT)
        self.play(FadeOut(ghost), win.animate.set_stroke(PROBLEM), *[b[0].animate.set_stroke(PROBLEM) for b in over], FadeIn(ol), calls.to(7), sent.to(len(msgs.blocks) + 1), run_time=0.6)
        self.next_slide("""A question about yesterday brings in the archive, and the archive's answer is long. The list now has more than
        the window holds, and the next call is refused: the model cannot be sent more than it can read. This is the wall every
        long-running agent hits, and it is not the model's problem to solve, because the model never saw the list grow. The
        application owns the list, so the application has to make it shorter, and there are two honest ways.""")
        # --- 3 sliding window: the oldest messages go, a tool call and its result together
        drop = msgs.blocks[:4]
        keep = msgs.blocks[4:]
        self.play(*[FadeOut(b, shift=LEFT * 0.4) for b in drop], run_time=0.5)
        msgs.blocks = keep
        msgs.remove(*drop)
        self.play(win.animate.set_stroke(RESULT), *[b[0].animate.set_stroke(KIND[k]) for b, k in zip(over, ("tool_use", "tool_result"))], FadeOut(ol), run_time=0.3)   # members first, on their own
        self.play(*[b.animate.move_to(msgs.slot(i)) for i, b in enumerate(keep)], sent.to(len(keep) + 1), run_time=0.7)
        sl = label("sliding window: the oldest messages leave;\na tool call and its result leave together", 13, RESULT).move_to(STOP_AT).align_to(model[0], LEFT)
        self.play(FadeIn(sl), run_time=0.3)
        self.next_slide("""The first way is a sliding window: keep the last so many messages and let the oldest fall off, the system prompt
        excepted. One rule makes it safe: a tool request and its result are one unit, because a result whose request is gone,
        or a request whose result is gone, is a malformed conversation and the model will refuse it; so the window drops them
        together. The list fits again. The price is memory: the first question and its answer are gone, and the model will
        not know they happened.""")
        # --- 4 summarisation: the oldest become one block
        old = msgs.blocks[:3]
        rest = msgs.blocks[3:]
        summ = msg("summary", "assistant · summary of the door question").move_to(msgs.slot(0))
        summ[0].set_stroke(MODEL).set_fill(MODEL, 0.28)
        self.play(ReplacementTransform(VGroup(*old), summ), run_time=0.7)
        msgs.blocks = [summ, *rest]
        msgs.remove(*old); msgs.add(summ)
        self.play(*[b.animate.move_to(msgs.slot(i + 1)) for i, b in enumerate(rest)], sent.to(len(msgs.blocks) + 1), run_time=0.6)
        sl2 = label("summarisation: the oldest messages become one;\nthe most recent stay as they were", 13, MODEL).move_to(sl, aligned_edge=LEFT)
        self.play(FadeOut(sl), FadeIn(sl2), run_time=0.3)
        self.finish("""The second way keeps the memory and pays in precision: ask the model, in a separate call, to summarise the oldest
        part of the list into one message, and put that in their place; the most recent messages stay as they were. One
        framework's defaults are a good picture of the trade: summarise the oldest thirty percent, always keep the ten most
        recent. So the list is the agent's whole state, it is resent on every call, and managing its length is the
        application's job, not the model's. Save the list per user and you have a session; put facts somewhere the loop can
        fetch them with a tool and you have memory. Both are the next talk. This one ends where it began: an application, an
        API that became a tool, a model, a list of messages, and a loop.""")
