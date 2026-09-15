"""Move 2: the whole process becomes a tool. Change of vocabulary: fetch a frame and ask about it is one capability,
so name it as one: a function with a decorator and a docstring, and the tool card fills in from the code. Then more
tools, one per device. Then the new problem: someone has to choose which tool a question needs, at every step. The
model can, if it is told what the tools are; and then the application has to call it again after running one."""
from lib.palette import *
from objects import *

SRC2 = '''@tool
def query_camera(camera: int, question: str):
    """What a camera sees right now.

    Args:
        camera: camera number, 1 to 4
        question: what to look for
    """
    frame = camera_api.frame(camera)
    return vision.ask(frame, question)'''


class ToolFromApi(TalkSlide):
    def construct(self):
        # --- the last frame of move one, rebuilt: six messages, the code, the camera API and the thermometer, the wall
        t = title_still(self, *TITLES["api"])
        st = stage()
        user, app, model, arrows, calls, tools = st["user"], st["app"], st["model"], st["arrows"], st["calls"], st["tools"]
        camera = device_box("camera API", CARD_YS[0])
        thermo = device_box("thermometer", CARD_YS[1])
        link = device_link(camera)
        src = app_code()
        srcl = label("the whole application: three lines", 14, MUTED).next_to(src, UP, buff=GAP_TIGHT).align_to(src, LEFT)
        old = put_history(messages(), HIST_API)
        wall = label("no code path reaches it", 14, PROBLEM).next_to(thermo, DOWN, buff=GAP_TIGHT).align_to(thermo, LEFT)
        why = under_app("the code decided what to fetch, not the model", 14, PROBLEM, app=app)
        calls.tracker.set_value(2)
        self.add(user, app, model, arrows, calls, tools, camera, thermo, link, src, srcl, old, wall, why)
        # --- the first change: the conversation clears and the three lines move up to be looked at as one process
        code2 = code(SRC2, "python", 15).move_to([LIST_X, -0.05, 0])
        proc = label("fetch a frame, ask about it: one process", 14, MUTED).move_to([APP_X0 + 0.3, 1.85, 0], aligned_edge=LEFT)
        src_up = app_code().move_to([LIST_X, 0.9, 0])
        t = retitle(self, t, *TITLES["tool"], extra=[FadeOut(old), FadeOut(why), FadeOut(wall), FadeOut(thermo), FadeOut(srcl), calls.to(0), Transform(src, src_up), FadeIn(proc)])
        self.next_slide("""The same application, its conversation cleared, and the three lines moved up where we can look at them. Read them
        as one thing: fetch a frame from a camera, ask a vision model about it. That is a capability. The change of
        vocabulary that makes an agent possible is to name that capability as one unit, a tool, so that it can be one of
        several, and so that something other than the code can decide when to use it.""")
        # --- the process becomes a tool: decorator and docstring; the card fills in from the code
        self.play(FadeOut(src), FadeOut(proc), run_time=0.3)
        self.play(FadeIn(code2), run_time=0.5)
        bar = highlight_line(code2, 0)
        self.add(bar)
        card = tool_card(*TOOLS[0])
        tag_target = card[4]
        self.play(FadeIn(bar), run_time=0.3)
        self.play(FadeIn(card[0]), Transform(camera, tag_target), FadeOut(link), run_time=0.8)      # the API box becomes the tag on the card
        self.play(bar.animate.move_to(highlight_line(code2, 1)), run_time=0.5)
        self.play(FadeIn(card[1]), run_time=0.5)
        self.play(bar.animate.move_to(highlight_line(code2, 2)), run_time=0.5)
        self.play(FadeIn(card[2]), run_time=0.5)
        self.play(bar.animate.move_to(highlight_line(code2, 5)), run_time=0.5)
        self.play(bar.animate.stretch_to_fit_height(highlight_line(code2, 5).height * 2.1).move_to(VGroup(code2.lines[5], code2.lines[6])), run_time=0.3)
        self.play(FadeIn(card[3]), run_time=0.5)
        self.play(FadeOut(bar), run_time=0.3)
        self.remove(camera); self.add(tag_target)
        self.next_slide("""The process becomes a function with a name and typed arguments, plus two additions and nothing else: a decorator,
        and a docstring. Watch the tool definition fill in on the right as the highlight walks the code. The decorator says:
        offer this to the model. The function's name is the tool's name. The first line of the docstring is the description,
        and that description is what the model will read when it decides whether this tool answers a question; write it as
        you would for a junior colleague. The type hints and the argument list become the input schema. The camera API is
        still there, as the thing the function reaches. Nothing about the process changed; it has a name now.""")
        # --- more tools, one per device
        others = VGroup(tool_card(*TOOLS[1]), tool_card(*TOOLS[2]))
        self.play(LaggedStart(*[FadeIn(c, shift=UP * 0.1) for c in others], lag_ratio=0.3), run_time=0.8)
        to_model = label(TO_MODEL_LABEL, 14, TOOL).move_to([MODEL_C[0] - CARD_W / 2, 0.9, 0], aligned_edge=LEFT)
        stays = label(STAYS_LABEL, 14, MUTED).next_to(code2, DOWN, buff=GAP_TIGHT).align_to(code2, LEFT)
        self.play(FadeIn(to_model), FadeIn(stays), run_time=0.5)
        self.next_slide("""Once the process has a name, the thermometer and the camera archive get the same treatment: two more functions,
        two more cards, each tied to the device it reaches. The line that matters for security and for architecture: what
        crosses to the model is the cards, name, description and schema, text. What stays in the application is the code, the
        API endpoints and the credentials. The model never executes anything; it can only ask.""")
        # --- the new problem: which tool? Named here; the next move shows the answer, the cards going in with the list
        q = under_app(WHICH_LABEL, 15, PROBLEM, app=app)
        self.play(FadeIn(q), run_time=0.4)
        self.finish("""And now the new problem, the one the old code never had: with three tools, which one does a question need? Not
        the code; the code deciding was the wall. The model can choose, if it is told what the tools are: read the arrow into
        the model once more, the cards go into every call beside the system prompt and the messages, and the model can
        answer with the name of a tool and the arguments it wants. But a choice is not an answer. The application has to run
        the chosen tool, put the result into the list, and ask the model again, until the model answers in words. That is the
        loop, and in the next move the application runs it.""")
