"""Move 2: from an API to a tool. The application's own function, as code, on the right half; on the left, the tool
definition the model will receive, filled in field by field from the function: the name from its name, the description
from its docstring, the input schema from its type hints. Then three such cards, and the line that matters: the model
receives the definitions, never the code.

  Final frame: the tool code on the right (a highlighted block); three tool cards in a column on the left with their
  three devices beside them; a label saying what crosses to the model and what stays.
  Clicks: 1 the function the application already has  2 a decorator and a docstring make it a tool; the card fills in
  from the code  3 three tools: the definitions go to the model, the code stays in the application.
"""
from lib.palette import *
from objects import *

CODE_X = 0.4     # the code block's left edge; the picture uses x -6.4 .. -0.2
V1 = ['def query_camera(camera: int, question: str):',
      '    frame = camera_api.frame(camera)',
      '    return vision.ask(frame, question)']
V2 = ['@tool',
      'def query_camera(camera: int, question: str):',
      '    """What a camera sees right now.',
      '',
      '    Args:',
      '        camera: the camera number, 1 to 4',
      '        question: what to look for in the frame',
      '    """',
      '    frame = camera_api.frame(camera)',
      '    return vision.ask(frame, question)']
BIG_W, BIG_H = 5.6, 2.3


def big_card(x: float, y: float) -> VGroup:
    """The tool definition at reading size: three field names down the left, values filled in later.
    card.fields = {"name": (header, value_anchor_x, y)}"""
    r = RoundedRectangle(corner_radius=0.1, width=BIG_W, height=BIG_H, fill_color=TOOL, fill_opacity=0.08, stroke_color=TOOL, stroke_width=1.6).move_to([x, y, 0])
    g = VGroup(r)
    g.rows = {}
    for k, name in enumerate(("name", "description", "input schema")):
        yy = y + BIG_H / 2 - 0.45 - k * 0.7
        h = label(name, 14, MUTED).move_to([x - BIG_W / 2 + GAP, yy, 0], aligned_edge=LEFT)
        g.add(h)
        g.rows[name] = yy
    g.value_x = x - BIG_W / 2 + 1.9
    return g


class ToolFromApi(TalkSlide):
    def construct(self):
        t = title(self, "From an API to a tool", "2  from an API to a tool")
        # --- 1 the function the application already has
        c1 = code(V1, "python", 15).move_to([CODE_X, 1.9, 0], aligned_edge=UL)
        cl = label("the application's own function, as it is", 14, MUTED).next_to(c1, DOWN, buff=GAP).align_to(c1, LEFT)
        fn = node("query_camera", MUTED, w=4.2, h=0.8, size=20, sub="camera, question").move_to([-3.3, 1.2, 0])
        api = node(DEVICES[0], MUTED, w=3.0, h=0.7, size=18).move_to([-3.3, -1.2, 0])
        fl = label("in the application", 14, MUTED).next_to(fn, UP, buff=GAP_TIGHT).align_to(fn, LEFT)
        self.play(FadeIn(fn), FadeIn(fl), FadeIn(api), run_time=0.5)
        self.play(FadeIn(c1), FadeIn(cl), run_time=0.6)
        bar = highlight_line(c1, 1)
        self.add(bar)
        travel(self, fn, api, TOOL, text="GET /cameras/2/frame", edges=True, run_time=0.6, flash=RESULT)
        self.play(bar.animate.move_to(highlight_line(c1, 2)), run_time=0.3)
        travel(self, api, fn, RESULT, text="frame", edges=True, run_time=0.5)
        self.play(FadeOut(bar), run_time=0.2)
        self.next_slide("""Here is that function, three lines. Given a camera number and a question, it fetches the current frame from the
        camera API and asks a vision model the question about the frame. Nothing about it is agentic; it is the code the
        application already had. Keep it exactly as it is. What changes is not the function but what the model is told about
        it.""")
        # --- 2 a decorator and a docstring make it a tool; the card fills in from the code
        c2 = code(V2, "python", 15).move_to([CODE_X, 2.4, 0], aligned_edge=UL)
        inserted = [highlight_line(c2, i, TOOL) for i in (0, 2, 3, 4, 5, 6, 7)]
        for b in inserted:
            b.set_fill(TOOL, 0.10)
        cl2 = label("the same function: a decorator and a docstring added", 14, MUTED).next_to(c2, DOWN, buff=GAP).align_to(c2, LEFT)
        self.play(FadeOut(c1), FadeOut(cl), FadeOut(fn), FadeOut(fl), FadeOut(api), run_time=0.35)
        self.play(FadeIn(c2), FadeIn(cl2), run_time=0.5)
        self.play(LaggedStart(*[FadeIn(b) for b in inserted], lag_ratio=0.1), run_time=0.6)
        card = big_card(-3.3, 0.9)
        ct = label("the tool definition, as the model receives it", 14, TOOL).next_to(card[0], UP, buff=GAP_TIGHT).align_to(card[0], LEFT)
        self.play(FadeIn(card), FadeIn(ct), run_time=0.5)
        fills = [(1, "name", "query_camera", TOOL), (2, "description", "What a camera sees right now.", TEXT),
                 (5, "input schema", "camera: integer, question: string", MUTED)]
        pointer = highlight_line(c2, 1)
        self.add(pointer)
        vals = []
        for line, field, value, colour in fills:
            v = label(value, 16, colour).move_to([card.value_x, card.rows[field], 0], aligned_edge=LEFT)
            src = c2.lines[line].copy()
            self.play(pointer.animate.move_to(highlight_line(c2, line)), run_time=0.3)
            self.play(ReplacementTransform(src, v), run_time=0.6)
            vals.append(v)
        self.play(FadeOut(pointer), run_time=0.2)
        self.next_slide("""Two additions and nothing else. A decorator marks the function as a tool, and a docstring says in plain words what
        it does and what its arguments mean. From those the framework derives the tool definition, the card on the left, and
        the card has exactly three fields. The name is the function's name. The description is the first paragraph of the
        docstring. The input schema comes from the type hints and the argument descriptions: camera is an integer, question a
        string. This is worth a pause: the description is the only thing the model will have to decide with. A vague docstring
        is a vague tool. Write it as you would for a new colleague.""")
        # --- 3 three tools; the definitions cross, the code stays
        small_cards = VGroup(*[tool_card(*spec, row=k).move_to([-4.6, 1.3 - 0.9 * k, 0]) for k, spec in enumerate(TOOLS)])
        devs = VGroup(*[device(n, k).move_to([-1.7, 1.3 - 0.9 * k, 0]) for k, n in enumerate(DEVICES)])
        self.play(ReplacementTransform(VGroup(card, *vals), small_cards[0]), FadeOut(ct), run_time=0.7)
        self.play(FadeIn(small_cards[1:], lag_ratio=0.2), FadeIn(devs), run_time=0.6)
        for k in range(3):
            self.play(Create(DashedLine(small_cards[k].get_right() + RIGHT * 0.1, devs[k].get_left() + LEFT * 0.1, color=DIM, stroke_width=1.5)), run_time=0.15)
        goes = label("to the model: name, description, input schema", 15, TOOL).move_to([-6.4, -1.75, 0], aligned_edge=LEFT)
        stays = label("stays in the application: the code, the API, the credentials", 15, MUTED).next_to(goes, DOWN, buff=GAP_TIGHT).align_to(goes, LEFT)
        self.play(FadeIn(goes), FadeIn(stays), run_time=0.4)
        self.finish("""Do the same for two more functions and the application has three tools: ask a camera what it sees, read the
        outdoor temperature, fetch recordings since a time. Each card faces a device on the right, because each is a door to
        one part of the world. Now the line that matters. What crosses to the model is the three cards: names, descriptions,
        schemas. What stays in the application is everything else: the code, the API endpoints, the credentials. The model
        will be able to ask for a door to be opened; it will never hold the key. The next move puts the cards into the
        call and watches what the model does with them.""")
