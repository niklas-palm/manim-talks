"""Move 3: the loop. The still picture with three tool cards and an empty list. The question that failed in move one:
the model now answers with a tool call, the application runs it, appends the result, calls again, and the model
answers in words. Then the backyard question runs through the same loop at speed."""
from lib.palette import *
from objects import *
from s02_tool import SRC2


class TheLoop(TalkSlide):
    def construct(self):
        # --- the last frame of move two, rebuilt: the decorated function, the three cards, the two labels
        t = title_still(self, *TITLES["tool"])
        st = stage()
        user, app, model, arrows, calls, tools = st["user"], st["app"], st["model"], st["arrows"], st["calls"], st["tools"]
        cards = tool_cards()
        code2 = code(SRC2, "python", 15).move_to([LIST_X, -0.05, 0])
        stays = label("stays here: the code, the API, the credentials", 14, MUTED).next_to(code2, DOWN, buff=GAP_TIGHT).align_to(code2, LEFT)
        to_model = label("to the model: name, description, input schema", 14, TOOL).move_to([MODEL_C[0] - CARD_W / 2, 0.9, 0], aligned_edge=LEFT)
        self.add(user, app, model, arrows, calls, tools, cards, code2, stays, to_model)
        msgs = messages()
        # --- the first change: the code steps aside; the cards stay; the list is empty and ready
        t = retitle(self, t, *TITLES["loop"], extra=[FadeOut(code2), FadeOut(stays), FadeOut(to_model)])
        self.add(msgs)
        self.next_slide("""The same picture with the three tool cards in place and an empty list. Read the arrow into the model once more:
        the system prompt, the tools, and the messages. From here on every call carries the cards too, so the model knows
        what it can ask for.""")
        # --- the question that failed, slowly
        msgs.append(self, message("user", "user · warm enough to open the door?"), frm=user, run_time=0.8)
        call_model(self, msgs, model, extra=cards, run_time=1.0)
        tu = reply(self, msgs, model, "tool_use", "assistant · tool_use: query_temperature()", run_time=0.7)
        stop = stop_label('stop_reason: "tool_use"', model, TOOL)
        self.play(calls.to(1), FadeIn(stop), run_time=0.4)
        self.next_slide("""The question that failed in move one. It joins the list, the list and the cards go to the model, and the reply is
        not words. It is a tool call: a structured message naming query_temperature, with the arguments the schema asked
        for, none here, and a stop reason that says tool_use. The model chose that tool from the descriptions; nobody wrote
        a rule. It cannot run it; it can only ask.""")
        # --- the application runs it
        travel(self, tu, cards[1], TOOL, text="run", edges=True, run_time=0.7)          # the call goes to the tool that answers it
        msgs.append(self, message("tool_result", "user · tool_result: 19 °C"), frm=cards[1], run_time=0.8)   # the result comes back from that tool into its slot
        ran = label("the application ran it; the model never does", 14, MUTED).next_to(app[0], DOWN, buff=GAP_TIGHT).align_to(app[0], LEFT)
        self.play(tools.to(1), FadeIn(ran), run_time=0.4)
        self.next_slide("""The application sees the tool call, finds the function behind the card, runs it against the real thermometer, and
        appends the result to the list as a message in the user's role, tagged with the call it answers. Tool calls: one.
        Nothing has been decided about the door yet; the model has not seen the number.""")
        # --- call again; the answer in words
        call_model(self, msgs, model, extra=cards, run_time=0.8)
        reply(self, msgs, model, "assistant", "assistant · 19 °C: yes, open it", run_time=0.6)
        stop2 = stop_label('stop_reason: "end_turn"', model, MODEL)
        self.play(calls.to(2), FadeOut(stop), FadeIn(stop2), run_time=0.4)
        self.next_slide("""Called again with the longer list, the model has the number and answers in words, and the stop reason says
        end_turn. That is the whole loop: call, if the reply is a tool call then run it and append the result and call
        again, otherwise the turn is over. Two model calls, one tool call, one question the code alone could not answer.""")
        # --- the same loop at speed, for the first question
        self.play(FadeOut(ran), FadeOut(stop2), run_time=0.3)
        msgs.append(self, message("user", "user · anyone in the backyard?"), frm=user, run_time=0.35)
        call_model(self, msgs, model, extra=cards, run_time=0.4)
        tu2 = reply(self, msgs, model, "tool_use", 'assistant · tool_use: query_camera(2, "anyone there?")', run_time=0.3)
        self.play(calls.to(3), run_time=0.15)
        travel(self, tu2, cards[0], TOOL, edges=True, run_time=0.3)
        msgs.append(self, message("tool_result", "user · tool_result: a person by the shed"), frm=cards[0], run_time=0.4)
        self.play(tools.to(2), run_time=0.15)
        call_model(self, msgs, model, extra=cards, run_time=0.4)
        reply(self, msgs, model, "assistant", "assistant · yes, one person by the shed", run_time=0.3)
        self.play(calls.to(4), run_time=0.2)
        self.finish("""Now the first question again, at speed, through the same loop: the model asks for camera two with a question of
        its own choosing, the application fetches, the result joins the list, the model answers. Compare with move one: the
        code no longer decides what to look at; it only executes what the model asks for and keeps the list. That shift is
        the whole definition of an agent. Four model calls and two tool calls for two questions, and the list has grown to
        eight messages; keep an eye on that.""")
