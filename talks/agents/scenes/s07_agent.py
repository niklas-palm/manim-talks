"""Move 7: the agent, as one thing. Every part has now been seen at full size: the list, the tools, the loop, the
framework, the list's limit, generic tools. The list and the cards fold into one compact entity inside the application, a
frame named agent holding the rows and the cards, and a task runs through it at speed. This is the picture the talk
leaves behind, and the one every later talk on agents can start from.

  Final frame: the stage; inside the application, top left, the entity with the rows of one task and three named cards;
  the model top right; counters 8 and 6.
  Clicks: 1 the list and the cards fold into the entity  2 a task through it at speed.
"""
from lib.palette import *
from objects import *


class TheAgent(TalkSlide):
    def construct(self):
        # --- the last frame of move six, rebuilt: the coding task's eight messages, the generic cards, the closing label
        t = title_still(self, *TITLES["every"])
        st = stage()
        user, app, model, arrows, calls, tools = st["user"], st["app"], st["model"], st["arrows"], st["calls"], st["tools"]
        generic = VGroup(*[tool_card(*g) for g in GENERIC_TOOLS])
        msgs = put_history(messages(), HIST_CODE)
        calls.tracker.set_value(4); tools.tracker.set_value(3)
        own = under_app("generic tools: the agent makes the tool it needs, on demand", 15, TOOL, app=app)
        self.add(user, app, model, arrows, calls, tools, generic, msgs, own)
        # --- the first change: the list and the cards fold into one thing
        frame, lst, cards = agent_entity(HIST_CODE_KINDS)
        one = under_app("one thing: the list, the tools, the loop", 15, TEXT, app=app)
        t = retitle(self, t, *TITLES["agent"], extra=[FadeOut(own), ReplacementTransform(msgs, lst), ReplacementTransform(generic, cards)], run_time=1.0)
        self.play(FadeIn(frame), FadeIn(one), run_time=0.5)
        self.next_slide("""Everything this talk built, folded into one thing. The list of messages and the three tools shrink into a frame
        inside the application, and the frame has a name: the agent. The rows are the same messages, coloured by who wrote
        them; the cards are the same tools, named. The loop is the frame itself: it is what calls the model with the list,
        runs the card the model asks for, appends what came back, and calls again. The model stays where it always was,
        outside. From here on, when anyone says agent, this is the picture.""")
        # --- a task through it at speed
        run = Run(self, lst, cards, model, calls, tools, 4, 3)
        run.clear(0.3)
        run.ask(user, 0.3)
        run.think(0.25)
        run.use(1, rt=0.2)           # read_file
        run.result(cards[1], 0.2)
        run.think(0.2)
        run.use(2, rt=0.2)           # write_file
        run.result(cards[2], 0.2)
        run.think(0.2)
        run.use(0, rt=0.2)           # bash
        run.result(cards[0], 0.2)
        run.think(0.2)
        run.answer(0.25)
        self.finish("""One more task, at speed, to show the thing working as a whole: a question comes in, the list goes to the model,
        the model asks for a file, then writes one, then runs the tests, each answer joining the list, and finally it answers
        in words. Four model calls, three tool calls, and no line in the application knew what the task was. So the whole
        talk is one picture. A plain application with one model call, whose code decided what to fetch. The same process
        named as a tool, then several, and the model choosing. The application running the loop; a framework hiding it; the
        list as the only state, with its window. Generic tools, and the agent making its own. And every agent you will use or
        build this year is this entity, inside some application, calling some model. What has to be built around it so that it can run on its own, a place to act, a way to be woken, a record of what it did, attaches to this picture without changing it.""")
