"""Move 2: from an API to a tool. The function the application already has, as code, inside the application; then a
decorator and a docstring, and the tool definition fills in from the code while a highlight walks it: name from the
function name, description from the docstring, input schema from the signature. Then three functions, three cards,
each still facing its device; what crosses to the model, and what stays."""
from lib.palette import *
from objects import *

SRC1 = '''def query_camera(camera: int, question: str):
    frame = camera_api.frame(camera)
    return vision.ask(frame, question)'''

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
        # --- the last frame of move one, rebuilt: six messages, the camera API and the thermometer, the memory label
        t = title_still(self, *TITLES["api"])
        st = stage()
        user, app, model, arrows, calls, tools = st["user"], st["app"], st["model"], st["arrows"], st["calls"], st["tools"]
        camera = device_box("camera API", CARD_YS[0])
        thermo = device_box("thermometer", CARD_YS[1])
        link = device_link(camera)
        old = put_history(messages(), HIST_API)
        mem = label("the list is the only memory: every call sends all of it", 14, MUTED).next_to(app[0], DOWN, buff=GAP_TIGHT).align_to(app[0], LEFT)
        calls.tracker.set_value(3)
        self.add(user, app, model, arrows, calls, tools, camera, thermo, link, old, mem)
        # --- the first change: a new move, the conversation clears, the function that fetched the frame appears
        code1 = code(SRC1, "python", 15).move_to([LIST_X, 1.2, 0])
        cl = label("the application's own function, as it is", 14, MUTED).next_to(code1, DOWN, buff=GAP_TIGHT).align_to(code1, LEFT)
        link2 = device_link(camera, "the function calls it")
        t = retitle(self, t, *TITLES["tool"], extra=[FadeOut(old), FadeOut(mem), FadeOut(thermo), FadeOut(link), calls.to(0)])
        self.play(FadeIn(code1), FadeIn(cl), FadeIn(link2), run_time=0.6)
        self.next_slide("""Same picture, and inside the application the function that fetched the frame in move one, exactly as it is: three
        lines, a name, two typed arguments, a call to the camera API, a call to a vision model on the frame. Nothing about
        it is agent-specific. This is the code most teams already have.""")
        # --- decorator and docstring; the card fills in from the code
        code2 = code(SRC2, "python", 15).move_to([LIST_X, -0.05, 0])
        self.play(FadeOut(code1), FadeOut(cl), FadeOut(link2), run_time=0.3)
        self.play(FadeIn(code2), run_time=0.5)
        bar = highlight_line(code2, 0)
        self.add(bar)
        card = tool_card(*TOOLS[0])
        tag_target = card[4]
        self.play(FadeIn(bar), run_time=0.3)
        self.play(FadeIn(card[0]), Transform(camera, tag_target), run_time=0.8)      # the API box becomes the tag on the card
        self.play(bar.animate.move_to(highlight_line(code2, 1)), run_time=0.5)
        self.play(FadeIn(card[1]), run_time=0.5)
        self.play(bar.animate.move_to(highlight_line(code2, 2)), run_time=0.5)
        self.play(FadeIn(card[2]), run_time=0.5)
        self.play(bar.animate.move_to(highlight_line(code2, 5)), run_time=0.5)
        self.play(bar.animate.stretch_to_fit_height(highlight_line(code2, 5).height * 2.1).move_to(VGroup(code2.lines[5], code2.lines[6])), run_time=0.3)
        self.play(FadeIn(card[3]), run_time=0.5)
        self.play(FadeOut(bar), run_time=0.3)
        self.remove(camera); self.add(tag_target)
        self.next_slide("""Two additions and nothing else: a decorator, and a docstring. Watch the tool definition fill in on the right as
        the highlight walks the code. The decorator says: offer this function to the model. The function's name becomes
        the tool's name. The first line of the docstring becomes the description, and that description is what the model
        reads when it decides whether this tool answers the question; write it as you would for a junior colleague. The
        type hints and the argument list become the input schema, a JSON schema the model must fill in. The camera API is
        still there, as the thing the function reaches; it did not change at all.""")
        # --- three tools; what crosses, what stays
        others = VGroup(tool_card(*TOOLS[1]), tool_card(*TOOLS[2]))
        self.play(LaggedStart(*[FadeIn(c, shift=UP * 0.1) for c in others], lag_ratio=0.3), run_time=0.8)
        to_model = label("to the model: name, description, input schema", 14, TOOL).move_to([MODEL_C[0] - CARD_W / 2, 0.9, 0], aligned_edge=LEFT)
        stays = label("stays here: the code, the API, the credentials", 14, MUTED).next_to(code2, DOWN, buff=GAP_TIGHT).align_to(code2, LEFT)
        self.play(FadeIn(to_model), FadeIn(stays), run_time=0.5)
        self.finish("""Two more functions get the same treatment: one reads the thermometer, one searches the camera archive. Three
        cards, each still tied to the device it reaches. Now the line that matters for security and for architecture: what
        crosses to the model is the cards, name, description and schema, text. What stays in the application is the code,
        the API endpoints and the credentials. The model never executes anything; it can only ask. In the next move it
        does.""")
