
# ============================================================================ #
#  THE REFERENCE LOOK — 22 Sept 2026
#
#  Appended to a composed PYQ scene by tools/make_ref_scene.py. It follows the
#  user's reference reel (memory: reference-look-sept19):
#    * captions ALWAYS on, one line at the very top, key words gold;
#    * one presenter size (the compositor), so every graphic lives in the band
#      STAGE_TOP..STAGE_BOT above his head;
#    * tables with a numbered middle column, every row drawn empty from the
#      start and filled as it is spoken, the row being spoken outlined in gold,
#      and a small gold section tag naming that row's topic;
#    * diagram labels as pills (the one being named white, the rest dark);
#    * fact pills, a pale statement card, and a gold "नोट्स बटन पर आंसर" pill.
#
#  Ion charges are typeset in MathTex (no vendored face has "⁺"), arrows are
#  drawn as shapes (none has "→"), and Devanagari goes through Noto Sans
#  Devanagari, the one face here that keeps a reph clear of an i-matra.
# ============================================================================ #
import re as _re_ref

LOOK = "reference"
CAPTION_SIZE, CAPTION_W, CAPTION_TOP = 36, 0.92, 0.030
STAGE_TOP, STAGE_BOT, STAGE_W = 0.092, 0.600, 0.92
CELL_TOP, CELL_FLOOR = 0.092, 0.600
CAPTION_GAP = 0.34

R_FONT = "Noto Sans Devanagari"
R_GOLD, R_GREEN, R_TEAL = "#F6BE45", "#72E0A8", "#5CCBEA"
R_GRID, R_BODY, R_DIM = "#4A6CA3", "#EAF0FA", "#8FA3C4"
R_PILL = "#0C1D3E"
R_CARD, R_CARD_EDGE, R_CARD_INK, R_CARD_RULE = "#EEF3FB", "#E3A33A", "#13284A", "#3F7BD6"
R_TONE = {"gold": R_GOLD, "green": R_GREEN, "teal": R_TEAL, "white": INK}

# SPACING, in pixels of a 1080-wide frame. One set of numbers for every block,
# so a table, a list and a card all breathe the same: the user asked for the
# gaps between a table, the text inside it and the text around it to be even.
# Raised once after review (23 Sept): a row's text sat tight against its rule.
# These are the gap between a table and the text INSIDE it, so they move
# together — widening the inset without the row height only moves the crowding
# from the sides to the top and bottom.
PAD_X = 34          # left/right inset of text inside a cell
ROW_PAD = 58        # space above+below a row's text
ROW_MIN = 108       # a row is never shorter than this
HEAD_H = 78         # the header row
NUM_W = 64          # the numbered middle column
TAG_GAP = 18        # tag pill to the top of its table
LINE_GAP = 0.32     # between wrapped lines, as a share of the type size
PILL_GAP = 16       # between stacked pills
BLOCK_GAP = 30      # between a block and whatever hangs under it
# The statement card's own insets. Bigger than a table cell's, because a card is
# a single block of prose and needs a visible margin all round rather than a
# grid's tight cells.
CARD_PAD_X = 52     # left/right inset of anything inside the card
CARD_PAD_Y = 44     # above the title and below the last line
CARD_GAP = 26       # title -> rule -> body
CARD_RULE_W = 0.62  # the rule, as a share of the card's width — never the lot

# An ion is an element symbol followed by a charge: Mn2+, Fe2+, Cl-.
_ION = _re_ref.compile(
    r"(?<![A-Za-z])(Mn|Fe|Cu|Zn|Cr|Co|Ni|Ti|Sc|Mg|Ca|Na|Al|Cl|Ag|Pb|Hg)(\d?)([+\-])(?![\w])")


def _u(px):
    """Pixels of a 1080-wide frame -> scene units."""
    return px * config.frame_width / 1080.0


def r_rich(s, size=30, color=R_BODY, weight="BOLD", t2c=None):
    """Text in the house face with any ion typeset in MathTex, level with it.

    A `$...$` span is set as maths too. The Devanagari faces carry no Greek and
    no sub/superscripts, so a unit symbol written into the Hindi string — ओम
    मीटर Ω·m — comes out as a tofu box. The symbol has to travel through LaTeX
    and sit BESIDE the Hindi rather than inside it, which is the same rule the
    repo already follows for E°सेल. Keep the span free of spaces: r_wrap splits
    on whitespace, so `$\Omega\,m$` survives word-wrapping and `$\Omega m$`
    does not.
    """
    pieces = _re_ref.split(r"(\$[^$]+\$)", s)
    if len(pieces) > 1:
        g = VGroup()
        for piece in pieces:
            if not piece.strip():
                continue
            if piece.startswith("$") and piece.endswith("$"):
                # 1.35, not 1.12. LaTeX sets its glyphs smaller than the
                # Devanagari face at the same nominal size, so a symbol matched
                # by the NUMBER read as a footnote beside the word it belongs
                # to. Matched by eye against the Hindi instead.
                g.add(Tex(r"\textsf{\textbf{$%s$}}" % piece[1:-1],
                          color=color, font_size=size * 1.35))
            else:
                g.add(r_rich(piece.strip(), size, color, weight, t2c))
        # A WORD'S BREADTH, not a hairline. At 0.26 the unit was jammed against
        # the last matra and read as part of the word.
        g.arrange(RIGHT, buff=_u(size * 0.5))
        return g
    parts, pos = [], 0
    for m in _ION.finditer(s):
        if m.start() > pos:
            parts.append(("t", s[pos:m.start()]))
        parts.append(("m", m.group(1), (m.group(2) or "") + m.group(3)))
        pos = m.end()
    if pos < len(s):
        parts.append(("t", s[pos:]))
    if not any(p[0] == "m" for p in parts):
        return Text(s, font=R_FONT, font_size=size, color=color, weight=weight,
                    t2c=t2c or {})
    g = VGroup()
    for p in parts:
        if p[0] == "t":
            if p[1].strip():
                g.add(Text(p[1].strip(), font=R_FONT, font_size=size, color=color,
                           weight=weight, t2c=t2c or {}))
        else:
            # SANS BOLD, to sit with the Devanagari face: the default maths
            # face is a serif and read as a different font mid-caption.
            g.add(Tex(r"\textsf{\textbf{%s}}$^{\textsf{\textbf{%s}}}$" % (p[1], p[2]),
                      color=color, font_size=size * 1.12))
    g.arrange(RIGHT, buff=_u(size * 0.26))
    return g


def r_wrap(s, width, size=26, color=R_BODY, weight="BOLD", align=None):
    """Wrap words to `width` (scene units); returns a VGroup of centred lines."""
    # A UNIT SYMBOL NEVER STARTS A LINE. "ओम मीटर $(\Omega\cdot m)$" is one
    # idea — the unit and the word that names it — and letting the wrapper break
    # between them put (Ω·m) alone on a second row, reading as a separate entry
    # rather than as the unit of the thing above it. Glued to the preceding
    # word, the line overruns and is scaled to fit instead, which keeps them
    # side by side.
    # A CELL CARRYING A UNIT SYMBOL IS NOT WRAPPED AT ALL. Gluing the symbol to
    # the word before it only moved the break one word earlier — "ओम / मीटर
    # (Ω·m)" — because the cell is too narrow for the whole phrase at full size.
    # The phrase is one idea and belongs on one line, so it is set as one line
    # and the scale-to-fit at the end of this function shrinks it into the cell.
    if "$" in s:
        g = VGroup(r_rich(s, size, color, weight))
        if g.width > width:
            g.scale(width / g.width)
        return g
    words, lines, cur = s.split(), [], []
    for w in words:
        trial = " ".join(cur + [w])
        if cur and r_rich(trial, size, color, weight).width > width:
            lines.append(" ".join(cur))
            cur = [w]
        else:
            cur.append(w)
    if cur:
        lines.append(" ".join(cur))
    g = VGroup(*[r_rich(l, size, color, weight) for l in lines])
    g.arrange(DOWN, buff=_u(size * LINE_GAP), aligned_edge=align if align is not None else ORIGIN)
    if g.width > width:
        g.scale(width / g.width)
    return g


def r_pill(text, tone="white", active=False, size=24, pad=(20, 11)):
    """A label pill: white-filled when it is the one being named, else dark."""
    t = r_rich(text, size, R_CARD_INK if active else INK)
    box = RoundedRectangle(width=t.width + _u(pad[0] * 2), height=t.height + _u(pad[1] * 2),
                           corner_radius=_u(12))
    if active:
        box.set_fill(INK, 1).set_stroke(INK, 2)
    else:
        box.set_fill(R_PILL, 0.95).set_stroke(R_TONE.get(tone, INK), 2.2)
    t.move_to(box)
    g = VGroup(box, t)
    g.pill_box, g.pill_text = box, t
    return g


def r_fact(lead, text, tone="gold", size=24):
    """A fact pill: dark fill, border in the tone, the lead word in that tone."""
    col = R_TONE.get(tone, R_GOLD)
    a = r_rich(lead, size, col)
    b = r_rich(text, size, INK)
    row = VGroup(a, b).arrange(RIGHT, buff=_u(10))
    box = RoundedRectangle(width=row.width + _u(40), height=row.height + _u(22),
                           corner_radius=_u(10))
    box.set_fill(R_PILL, 0.95).set_stroke(col, 2.4)
    row.move_to(box)
    return VGroup(box, row)


def _stage_bottom(self):
    """The lowest VISIBLE point of what is on the stage.

    Measured over the parts, not the groups: a VGroup's own fill opacity is 0,
    so filtering groups by it found nothing, and a "keep" pill fell back to a
    default position — straight across generation II of the pedigree."""
    ys = []
    for m in self.stage_mobs:
        if not isinstance(m, Mobject):
            continue
        for sm in m.get_family():
            if not sm.has_points():
                continue
            fo = getattr(sm, "get_fill_opacity", lambda: 1.0)()
            so = getattr(sm, "get_stroke_opacity", lambda: 0.0)()
            if fo > 0.05 or so > 0.05:
                ys.append(sm.get_bottom()[1])
    return min(ys) if ys else None


def _ref_caption(self, text, size=CAPTION_SIZE):
    limit = config.frame_width * CAPTION_W
    hl = self._hl(text)
    g = r_rich(text, size, INK, t2c=hl)
    if g.width > limit:
        if g.width * 0.80 <= limit:
            g.scale(limit / g.width)
        else:
            words = text.split()
            best, bk = None, 1
            for k in range(1, len(words)):
                a, b = " ".join(words[:k]), " ".join(words[k:])
                d = abs(len(a) - len(b))
                if best is None or d < best:
                    best, bk = d, k
            g = VGroup(r_rich(" ".join(words[:bk]), size, INK, t2c=self._hl(" ".join(words[:bk]))),
                       r_rich(" ".join(words[bk:]), size, INK, t2c=self._hl(" ".join(words[bk:]))))
            g.arrange(DOWN, buff=_u(10))
            if g.width > limit:
                g.scale(limit / g.width)
    g.move_to(norm_point(0.5, CAPTION_TOP))
    g.shift(DOWN * g.height / 2)
    return g


def _lg(g):
    """Mark every part of one figure as ONE diagram for the layout audit.

    The audit compares top-level mobjects, and animating a part of a group lifts
    that part to the top level — so a nucleus and its own "+26", or a pull arrow
    and the cloud it crosses, were reported as 100% overlaps. Parts sharing a
    `_layout_group` are one diagram; text-on-text is still checked across all."""
    key = getattr(g, "_ref_key", None) or id(g)
    g._ref_key = key
    for m in g.get_family():
        m._layout_group = key
    return g


def _later(self, at, fn):
    self._pending_calls = getattr(self, "_pending_calls", []) + [(int(at), fn)]


# ---------------------------------------------------------------- tables ---- #
def beat_rtable(self, spec):
    """The reference table. Every row is drawn EMPTY from the start, numbered in
    the middle column, and filled as the narration reaches it; the row being
    spoken is outlined in gold and the section tag names its topic."""
    heads = spec["heads"]
    rows = spec["rows"]
    n = max(int(spec.get("n", len(rows))), len(rows))
    W = config.frame_width * 0.92
    wn = _u(NUM_W)
    wc = (W - wn) / 2
    size = spec.get("size", 30)
    # cells first, so the row height fits the tallest cell
    cells = []
    for r in rows:
        lt = r_wrap(r.get("l", ""), wc - _u(PAD_X * 2), size) if r.get("l") else VGroup()
        rt = r_wrap(r.get("r", ""), wc - _u(PAD_X * 2), size) if r.get("r") else VGroup()
        cells.append((lt, rt))
    body_h = max([max(a.height, b.height) for a, b in cells] + [_u(40)])
    rh = max(body_h + _u(ROW_PAD), _u(ROW_MIN))
    hh = _u(HEAD_H)
    H = hh + rh * n
    x0, y0 = -W / 2, H / 2                           # local frame: top-left
    g = VGroup()
    grid = VGroup()
    frame = Rectangle(width=W, height=H).set_stroke(R_GRID, 2).set_fill(opacity=0)
    grid.add(frame)
    for xx in (x0 + wc, x0 + wc + wn):
        grid.add(Line([xx, y0, 0], [xx, y0 - H, 0]).set_stroke(R_GRID, 2))
    for k in range(n + 1):
        yy = y0 - hh - rh * k
        if k < n:
            grid.add(Line([x0, yy, 0], [x0 + W, yy, 0]).set_stroke(R_GRID, 1.6 if k else 2.4))
    hl = r_rich(heads[0], 38, R_GOLD).move_to([x0 + wc / 2, y0 - hh / 2, 0])
    hr = r_rich(heads[1], 38, R_GREEN).move_to([x0 + wc + wn + wc / 2, y0 - hh / 2, 0])
    for hdr in (hl, hr):
        if hdr.width > wc - _u(PAD_X * 2):
            hdr.scale((wc - _u(PAD_X * 2)) / hdr.width)
    nums = VGroup(*[Text(str(k + 1), font=R_FONT, font_size=26, color=R_DIM, weight="BOLD")
                    .move_to([x0 + wc + wn / 2, y0 - hh - rh * k - rh / 2, 0]) for k in range(n)])
    g.add(grid, hl, hr, nums)
    fills = []
    for k, (lt, rt) in enumerate(cells):
        cy = y0 - hh - rh * k - rh / 2
        lt.move_to([x0 + wc / 2, cy, 0])
        rt.move_to([x0 + wc + wn + wc / 2, cy, 0])
        g.add(lt, rt)
        fills.append((lt, rt))
    # the tag above the table's top-left corner
    tag = self._rtag(f"1 · {rows[0].get('tag', '')}" if rows and rows[0].get("tag") else "")
    tag.next_to(frame, UP, buff=_u(TAG_GAP)).align_to(frame, LEFT)
    g.add(tag)
    g.rt_tag = tag
    self.place(g, y=spec.get("y", 0.42), grow=False)
    # measured AFTER placement: place() may have shrunk the table to the band
    sc = frame.width / W
    row_h = rh * sc
    outline = RoundedRectangle(width=frame.width + _u(8), height=row_h - _u(6),
                               corner_radius=_u(6))
    outline.set_stroke(R_GOLD, 3.2, opacity=0).set_fill(R_GOLD, 0)
    g.add(outline)
    filled = set(spec.get("filled", []))

    def row_center(k):
        return np.array([frame.get_center()[0], nums[k].get_center()[1], 0])

    for k, (lt, rt) in enumerate(fills):
        side_at = rows[k].get("at")
        shown = rows[k].get("show", "")          # "l" / "r": that side already filled
        if k in filled or (side_at is None and not shown):
            if k not in filled:
                lt.set_opacity(0); rt.set_opacity(0)
            continue
        lt.set_opacity(1 if "l" in shown else 0)
        rt.set_opacity(1 if "r" in shown else 0)
        if side_at is None:
            continue
        ats = side_at if isinstance(side_at, list) else [side_at, side_at]
        for side, a in zip((lt, rt), ats):
            if a is None:
                continue

            def go(k=k, side=side):
                anims = []
                if outline.get_stroke_opacity() < 0.5:
                    outline.move_to(row_center(k))
                    anims.append(outline.animate.set_stroke(opacity=1).set_fill(opacity=0.07))
                elif abs(outline.get_center()[1] - row_center(k)[1]) > 1e-3:
                    anims.append(outline.animate.move_to(row_center(k)))
                t = rows[k].get("tag")
                if t:
                    new = self._rtag(f"{k + 1} · {t}").move_to(g.rt_tag, aligned_edge=LEFT)
                    anims.append(Transform(g.rt_tag, new))
                anims.append(side.animate.set_opacity(1))
                self.cue("click", gain=0.5)
                self.play(*anims, run_time=0.45)
            self._later(a, go)
    # a table shown again later with rows already filled starts with the
    # outline on the last filled row, the way the reference returns to it
    if filled and spec.get("outline_last", True):
        k = max(filled)
        outline.move_to(row_center(k)).set_stroke(opacity=1).set_fill(opacity=0.07)
        t = rows[k].get("tag") if k < len(rows) else None
        if t:
            new = self._rtag(f"{k + 1} · {t}").move_to(g.rt_tag, aligned_edge=LEFT)
            g.rt_tag.become(new)
    return _lg(g)


def _rtag(self, text):
    if not text:
        return VGroup()
    t = Text(text, font=R_FONT, font_size=23, color=R_GOLD, weight="BOLD")
    box = RoundedRectangle(width=t.width + _u(20), height=t.height + _u(12),
                           corner_radius=_u(6)).set_stroke(R_GOLD, 1.8).set_fill(R_PILL, 0.9)
    t.move_to(box)
    return VGroup(box, t)


def beat_rlist(self, spec):
    """A numbered list in the table's language: every row visible from the
    start with its number, text filling in as spoken, current row outlined."""
    rows = spec["rows"]
    n = max(int(spec.get("n", len(rows))), len(rows))
    W = config.frame_width * 0.92
    size = spec.get("size", 25)
    # the width left once the disc, its inset and the far-side inset are taken
    texts = [r_wrap(r["text"], W - _u(74 + PAD_X * 2), size, align=LEFT) for r in rows]
    rh = max([t.height for t in texts] + [_u(40)]) + _u(ROW_PAD)
    title = r_rich(spec.get("title", ""), 30, R_GOLD) if spec.get("title") else VGroup()
    g = VGroup()
    frame = RoundedRectangle(width=W, height=rh * n, corner_radius=_u(10)).set_stroke(R_GRID, 2)
    g.add(frame)
    top = frame.get_top()[1]
    left = frame.get_left()[0]
    nums, bodies = VGroup(), []
    for k in range(n):
        cy = top - rh * k - rh / 2
        if k:
            g.add(Line([left, top - rh * k, 0], [left + W, top - rh * k, 0]).set_stroke(R_GRID, 1.5))
        disc = Circle(radius=_u(22)).set_stroke(R_GOLD, 2.2).set_fill(R_PILL, 1)
        num = Text(str(k + 1), font=R_FONT, font_size=22, color=R_GOLD, weight="BOLD").move_to(disc)
        nm = VGroup(disc, num).move_to([left + _u(52), cy, 0])
        nums.add(nm)
        if k < len(texts):
            t = texts[k]
            # the disc ends at left+74 (centre 52, radius 22); PAD_X past it, so
            # the gap from the number to the text is the same inset a table cell
            # gets from its rule
            t.move_to([left + _u(74 + PAD_X) + t.width / 2, cy, 0])
            g.add(t)
            bodies.append(t)
    g.add(nums)
    if len(title):
        title.next_to(frame, UP, buff=_u(TAG_GAP + 6))
        if title.width > W:
            title.scale(W / title.width)
        g.add(title)
    self.place(g, y=spec.get("y", 0.25), grow=False)
    outline = RoundedRectangle(width=frame.width + _u(6), height=frame.height / n - _u(6),
                               corner_radius=_u(8))
    outline.set_stroke(R_GOLD, 3.2, opacity=0).set_fill(R_GOLD, 0)
    g.add(outline)
    filled = set(spec.get("filled", []))
    # A REVISION PASS walks the gold outline down a list that is already full:
    # "पहली है…, दूसरी है…" with every row on screen. focus_at is [[row, line], …].
    for row, at in spec.get("focus_at", []) or []:
        def focus(row=row):
            c = np.array([frame.get_center()[0], nums[row].get_center()[1], 0])
            if outline.get_stroke_opacity() < 0.5:
                outline.move_to(c)
                self.play(outline.animate.set_stroke(opacity=1).set_fill(opacity=0.07), run_time=0.3)
            else:
                self.cue("click", gain=0.5)
                self.play(outline.animate.move_to(c), run_time=0.35)
        self._later(at, focus)
    for k, t in enumerate(bodies):
        if k in filled:
            continue
        a = rows[k].get("at")
        if a is None:
            # NO REVEAL TIME MEANS THERE IS NOTHING TO WAIT FOR, so the row
            # stays on screen. Hiding it first and then finding no `at` left it
            # invisible for the REST OF THE VIDEO: che-c4-sa-01's second effect
            # was an empty gold-outlined box from t=45 to the end, with
            # focus_at pointing straight at it. A row is hidden only when there
            # is a moment coming to fill it in — which is also what this beat's
            # docstring has always claimed it does.
            continue
        t.set_opacity(0)

        def go(k=k, t=t):
            c = np.array([frame.get_center()[0], nums[k].get_center()[1], 0])
            anims = [t.animate.set_opacity(1)]
            if outline.get_stroke_opacity() < 0.5:
                outline.move_to(c)
                anims.append(outline.animate.set_stroke(opacity=1).set_fill(opacity=0.07))
            else:
                anims.append(outline.animate.move_to(c))
            self.cue("click", gain=0.5)
            self.play(*anims, run_time=0.45)
        self._later(a, go)
    return _lg(g)


# ------------------------------------------------------------- cards/pills -- #
def beat_statement(self, spec):
    """The pale statement card: dark title, a blue rule under it, lines that
    arrive as they are said, THE CARD GROWING DOWN TO MEET THEM.

    A TABLE RESERVES ITS EMPTY ROWS; A CARD MUST NOT. The numbered table draws
    every row from the start on purpose — the empty rows are the map of what is
    coming, and the student can see there are four. A statement card has no
    such map: a definition's third line reserved for it is just a slab of blank
    white, and on the genetic-code part that slab was two thirds of the card
    for thirty-five seconds. So the lines are laid out in their FINAL positions
    (nothing ever moves under the reader) and the box is drawn only as far down
    as the last line that has actually arrived."""
    W = config.frame_width * spec.get("w", 0.88)
    # EVERYTHING INSIDE THE CARD IS HELD TO THE CARD. The box is built at a
    # FIXED width W, and nothing used to hold the title or the rule to it:
    # "लैन्थेनॉइड संकुचन (Lanthanoid Contraction)" ran wider than the card and
    # spilled out past both edges onto the plate, and the rule — sized from that
    # title at 1.25x — leaked further still. Only the body lines were ever
    # wrapped, so it took the first question with a long title to show it.
    inner_w = W - _u(CARD_PAD_X * 2)
    title = r_rich(spec["title"], 30, R_CARD_INK)
    if title.width > inner_w:
        title.scale(inner_w / title.width)
    rule = Line(LEFT, RIGHT).set_stroke(R_CARD_RULE, 3)
    # The rule is a divider, not an underline: it is a fixed share of the CARD,
    # so it always reads as sitting inside the card whatever the title's length.
    rule.set_width(min(W * CARD_RULE_W, inner_w))
    lines = [r_wrap(l, inner_w, spec.get("size", 26), R_CARD_INK) for l in spec["lines"]]
    body = VGroup(*lines).arrange(DOWN, buff=_u(20))
    inner = VGroup(title, rule, body).arrange(DOWN, buff=_u(CARD_GAP))
    box = RoundedRectangle(width=W, height=inner.height + _u(CARD_PAD_Y * 2),
                           corner_radius=_u(16))
    box.set_fill(R_CARD, 0.97).set_stroke(R_CARD_EDGE, 3.2)
    inner.move_to(box)
    g = VGroup(box, inner)
    # placed at FULL size, so the band decides the scale the finished card gets
    self.place(g, y=spec.get("y", 0.30), grow=False)
    ats = spec.get("reveal_at") or []

    def card_to(k: int) -> RoundedRectangle:
        """The box as it should look with k lines showing; top edge never moves."""
        top = box.get_top()[1]
        bot = (lines[k - 1] if k else rule).get_bottom()[1] - _u(CARD_PAD_Y)
        r = RoundedRectangle(width=box.width, height=max(top - bot, _u(60)),
                             corner_radius=_u(16))
        r.set_fill(R_CARD, 0.97).set_stroke(R_CARD_EDGE, 3.2)
        return r.move_to([box.get_center()[0], (top + bot) / 2, 0])

    shown = 0
    if ats:
        for l in lines[:len(ats)]:
            l.set_opacity(0)
        box.become(card_to(0))
    for k, (l, a) in enumerate(zip(lines, ats)):
        def go(l=l, k=k):
            nonlocal shown
            shown = max(shown, k + 1)
            self.cue("pop", gain=0.5)
            self.play(box.animate.become(card_to(shown)),
                      l.animate.set_opacity(1), run_time=0.40)
        self._later(a, go)
    return _lg(g)


def beat_facts(self, spec):
    """Fact pills. With "keep": true they sit UNDER whatever is on the stage,
    as the reference hangs its ΔG pills under the finished table."""
    pills = VGroup(*[r_fact(it["lead"], it.get("text", ""), it.get("tone", "gold"),
                            spec.get("size", 24)) for it in spec["items"]])
    pills.arrange(DOWN, buff=_u(PILL_GAP))
    W = config.frame_width * 0.94
    if pills.width > W:
        pills.scale(W / pills.width)
    c, w, h = self.stage_box()
    band_bot = c[1] - h / 2
    under = _stage_bottom(self) if spec.get("keep") else None
    if under is not None:
        pills.next_to([0, under, 0], DOWN, buff=_u(BLOCK_GAP))
        over = band_bot - pills.get_bottom()[1]
        if over > 0:
            # lift the whole stage to make room, as far as the caption allows
            lift = over
            for m in self.stage_mobs:
                if isinstance(m, Mobject):
                    m.shift(UP * lift)
            pills.shift(UP * lift)
    else:
        self.place(pills, y=spec.get("y", 0.35), grow=False)
    ats = spec.get("reveal_at") or []
    for p, a in zip(pills, ats):
        p.set_opacity(0)

        def go(p=p):
            self.cue("pop", gain=0.5)
            self.play(p.animate.set_opacity(1), run_time=0.35)
        self._later(a, go)
    return _lg(pills)


def beat_rchain(self, spec):
    """Cause and effect as pills joined by drawn arrows; each quantity carries
    a drawn up or down arrow (no vendored face has one)."""
    items = spec["items"]
    col = {"up": R_GREEN, "down": R_GOLD}
    rows = []
    for text, d in items:
        t = r_rich(text, spec.get("size", 34), INK)
        arr = Arrow(DOWN * 0.30 if d == "up" else UP * 0.30,
                    UP * 0.30 if d == "up" else DOWN * 0.30, buff=0,
                    stroke_width=8, max_tip_length_to_length_ratio=0.45,
                    color=col.get(d, INK))
        row = VGroup(t, arr).arrange(RIGHT, buff=_u(14))
        box = RoundedRectangle(width=row.width + _u(40), height=row.height + _u(22),
                               corner_radius=_u(12)).set_fill(R_PILL, 0.95).set_stroke(col.get(d, INK), 2.4)
        row.move_to(box)
        rows.append(VGroup(box, row))
    g = VGroup()
    links = []
    for k, r in enumerate(rows):
        g.add(r)
    g.arrange(DOWN, buff=_u(64))
    for k in range(len(rows) - 1):
        a = Arrow(rows[k].get_bottom(), rows[k + 1].get_top(), buff=_u(6), stroke_width=6,
                  color=R_DIM, max_tip_length_to_length_ratio=0.35)
        links.append(a)
        g.add(a)
    if spec.get("title"):
        tt = r_rich(spec["title"], 32, R_TEAL)
        tt.next_to(g, UP, buff=_u(18))
        g.add(tt)
    self.place(g, y=spec.get("y", 0.35), grow=False)
    ats = spec.get("reveal_at") or []
    for k, r in enumerate(rows):
        if k >= len(ats):
            break
        r.set_opacity(0)
        if k:
            links[k - 1].set_opacity(0)

        def go(k=k, r=r):
            anims = [r.animate.set_opacity(1)]
            if k:
                anims.insert(0, links[k - 1].animate.set_opacity(1))
            self.cue("pop", gain=0.5)
            self.play(*anims, run_time=0.40)
        self._later(ats[k], go)
    return _lg(g)


def beat_codons(self, spec):
    """The triplets themselves: three bases boxed as one codon, as the narration
    says "screen पर आप A U G, U U U और G G C देख रहे हो". Optionally an arrow
    from one codon to the amino acid it codes for."""
    trips = spec["triplets"]
    size = spec.get("size", 40)
    groups = []
    for t in trips:
        tiles = VGroup()
        for b in t:
            txt = Text(b, font=R_FONT, font_size=size, color=INK, weight="BOLD")
            cell = RoundedRectangle(width=_u(74), height=_u(74), corner_radius=_u(10))
            cell.set_stroke(R_GRID, 2).set_fill(R_PILL, 0.9)
            txt.move_to(cell)
            tiles.add(VGroup(cell, txt))
        tiles.arrange(RIGHT, buff=_u(8))
        box = RoundedRectangle(width=tiles.width + _u(26), height=tiles.height + _u(24),
                               corner_radius=_u(12)).set_stroke(R_GOLD, 3).set_fill(opacity=0)
        tiles.move_to(box)
        groups.append(VGroup(box, tiles))
    row = VGroup(*groups).arrange(RIGHT, buff=_u(40))
    g = VGroup(row)
    title = r_rich(spec.get("title", ""), 30, R_TEAL) if spec.get("title") else VGroup()
    if len(title):
        title.next_to(row, UP, buff=_u(TAG_GAP + 6))
        g.add(title)
    amino = VGroup()
    if spec.get("amino"):
        k = int(spec.get("amino_of", 0))
        arr = Arrow(groups[k].get_bottom(), groups[k].get_bottom() + DOWN * _u(70),
                    buff=_u(6), stroke_width=6, color=R_DIM,
                    max_tip_length_to_length_ratio=0.35)
        pill = r_fact(spec["amino"], "", "green", 26)
        pill.next_to(arr, DOWN, buff=_u(10))
        amino = VGroup(arr, pill)
        g.add(amino)
    self.place(g, y=spec.get("y", 0.34), grow=False)
    ats = spec.get("reveal_at") or []
    for grp in groups:
        grp.set_opacity(0)
    amino.set_opacity(0)
    for k, at in enumerate(ats[:len(groups)]):
        def go(k=k):
            self.cue("pop", gain=0.5)
            self.play(groups[k].animate.set_opacity(1), run_time=0.35)
        self._later(at, go)
    if spec.get("amino_at") is not None:
        def show_amino():
            self.cue("reveal", gain=0.5)
            self.play(amino.animate.set_opacity(1), run_time=0.45)
        self._later(spec["amino_at"], show_amino)
    return _lg(g)


def beat_shrink(self, spec):
    """A row of atoms getting smaller across a series, drawn to scale.

    THE QUESTION IS A MECHANISM WITH A DIRECTION, so it is animated rather than
    listed (memory: animate-mechanisms). Lanthanoid contraction is exactly one
    thing happening: as you walk right along the series the nucleus pulls
    harder and the atom gets smaller. Words can only assert that; a row of
    circles drawn to their real radii SHOWS it, and the student can see the
    change is gradual rather than sudden.

    This is Manim's work, not a generated clip's. There is no footage of an
    atomic radius, and a clip of a laboratory would be decoration with no
    teaching job (memory: screen-carries-only-what-teaches,
    tell-user-when-manim-suffices).

    Each item is {"label", "r"} with `r` the radius in picometres, drawn to
    scale against the largest. The arrow beneath is DRAWN, never a glyph: no
    vendored face has an arrow (CLAUDE.md).

    THE NUMBER IS SHOWN, because the drawing alone cannot be checked. These are
    real radii and the circles are in true proportion to them, but the change
    across the series is only about a sixth — small enough that a student could
    read the row as a decorative gradient rather than as data. Printing the
    value under each atom makes the claim precise, lets the figure be checked
    against a textbook, and gives the student two numbers worth quoting in an
    answer. `subtitle` says WHICH radius is drawn, since "आकार" covers both the
    atom and the ion and they contract by different amounts.
    """
    items = spec["items"]
    big = max(float(i["r"]) for i in items)
    cell = _u(spec.get("cell", 150))
    rmax = cell * 0.44
    groups = []
    for it in items:
        rad = rmax * (float(it["r"]) / big)
        ring = Circle(radius=rad).set_stroke(R_TEAL, 3).set_fill(R_PILL, 0.55)
        core = Dot(radius=_u(7), color=R_GOLD)
        lab = r_rich(it["label"], 26, INK)
        num = r_rich(str(it.get("z", "")), 20, R_DIM) if it.get("z") else VGroup()
        val = r_rich(str(it["r"]), 22, R_TEAL) if spec.get("values", True) else VGroup()
        stack = VGroup(ring, core)
        col = VGroup(stack, lab)
        if len(num):
            col.add(num)
        if len(val):
            col.add(val)
        col.arrange(DOWN, buff=_u(8))
        groups.append(col)
    # EVEN PITCH BY POSITION, NOT BY A SPACER. An invisible rectangle in each
    # column does give the circles an even pitch — until the column is revealed
    # with set_opacity(1), which un-hides the spacer too and draws a white bar
    # under the atoms. Nothing here is hidden that later gets shown, so the
    # columns are simply placed on the pitch.
    n_it = len(groups)
    for k, col in enumerate(groups):
        col.move_to(RIGHT * ((k - (n_it - 1) / 2) * cell))
    # the tallest column sets the row's baseline, so labels line up
    base = min(c.get_bottom()[1] for c in groups)
    for col in groups:
        col.shift(UP * (base - col.get_bottom()[1]))
    row = VGroup(*groups)

    shaft = Line(row.get_left() + LEFT * _u(4), row.get_right() + RIGHT * _u(4))
    shaft.set_stroke(R_GOLD, 5)
    tip = Triangle().set_fill(R_GOLD, 1).set_stroke(width=0)
    tip.set_height(_u(26)).rotate(-PI / 2).move_to(shaft.get_right())
    arrow = VGroup(shaft, tip)
    cap = r_rich(spec.get("arrow", ""), 24, R_GOLD) if spec.get("arrow") else VGroup()
    under = VGroup(arrow)
    if len(cap):
        under.add(cap)
        under.arrange(DOWN, buff=_u(10))
    g = VGroup(row, under).arrange(DOWN, buff=_u(BLOCK_GAP))
    head = VGroup()
    if spec.get("title"):
        head.add(r_rich(spec["title"], 30, R_GOLD))
    if spec.get("subtitle"):
        head.add(r_rich(spec["subtitle"], 22, R_DIM))
    if len(head):
        head.arrange(DOWN, buff=_u(8))
        g = VGroup(head, g).arrange(DOWN, buff=_u(TAG_GAP + 8))
    # GROWN TO THE BAND, like every other block. Left at its authored size the
    # row sat small in a band it could have filled, and a contraction drawn
    # small is a contraction nobody notices.
    self.place(g, y=spec.get("y", 0.34), grow=True, pad_w=spec.get("pad_w", 0.98))

    ats = spec.get("reveal_at") or []
    for grp in groups:
        grp.set_opacity(0)
    under.set_opacity(0)
    for k, at in enumerate(ats[:len(groups)]):
        def go(k=k):
            self.cue("pop", gain=0.5)
            self.play(groups[k].animate.set_opacity(1), run_time=0.30)
        self._later(at, go)
    if spec.get("arrow_at") is not None:
        def show_arrow():
            self.cue("reveal", gain=0.5)
            self.play(under.animate.set_opacity(1), run_time=0.45)
        self._later(spec["arrow_at"], show_arrow)
    return _lg(g)


def beat_pyramid(self, spec):
    """An ecological pyramid: producers at the BOTTOM, narrowing upward.

    THE ANSWER IS THE SHAPE. "यह सदैव सीधा क्यों होता है" cannot be answered by
    a list — the student has to SEE each tier narrower than the one beneath it.

    THE BASE GOES AT THE BOTTOM, which is not what arrange(DOWN) does. Given the
    tiers base-first (the order energy flows and the order the narration walks),
    arrange(DOWN) puts the first one at the TOP and draws the pyramid upside
    down — producers in the sky, top consumer on the ground. It rendered that
    way once and it is the one thing this figure must not get wrong, since the
    question is literally about which way up it stands.

    WIDTH IS A COMPRESSED SCALE, AND THAT IS SAID OUT LOUD. Energy falls by a
    factor of about ten per level, so a strictly proportional drawing makes the
    fourth tier a thousandth of the base — a hairline nobody can see, with an
    unreadable label. Every textbook draws this pyramid schematically for the
    same reason. The widths here are the cube root of the energy, which is
    monotonic (a bigger tier is always more energy) but gentle enough to read as
    a pyramid; the exact ratio is carried by the NUMBER printed beside each
    tier, which is where a student should be reading it from anyway.
    """
    tiers = spec["tiers"]
    top_e = max(float(t["energy"]) for t in tiers)
    # narrower bars when an icon column is asked for, so the row still fits
    icons_on = any(t.get("icon") for t in tiers)
    W = config.frame_width * spec.get("w", 0.46 if icons_on else 0.60)
    # Low enough that the top two tiers still DIFFER. At 0.26 both the third
    # and fourth tier clamped to the floor and came out the same width, which
    # reads as the pyramid stopping its taper one level early — in a figure
    # whose whole point is that every level is narrower than the one below.
    MIN_W = W * 0.16
    th = _u(spec.get("tier", 84))
    rows, labels = [], []
    for t in tiers:
        frac = (float(t["energy"]) / top_e) ** (1.0 / 3.0)
        w = max(MIN_W, W * frac)
        tone = R_TONE.get(t.get("tone", "green"), R_GREEN)
        bar = Rectangle(width=w, height=th)
        bar.set_fill(tone, 0.22).set_stroke(tone, 3)
        # the label goes ON the tier while it fits, and beside it when it does
        # not: shrinking "शीर्ष उपभोक्ता" into the narrowest tier made it
        # unreadable, which is worse than moving it out
        name = r_rich(t["label"], 25, INK)
        outside = name.width > w - _u(24)
        if not outside:
            name.move_to(bar)
        val = r_rich(str(t.get("note", "")), 24, tone) if str(t.get("note", "")) else VGroup()
        # THE EXAMPLE THAT GROUP IS. A tier called "उत्पादक" is an abstraction;
        # a tuft of grass beside it is the thing itself, and the student holds
        # the level by what lives there. Photos were tried first (the house
        # rule) and Commons returned seed-catalogue scans covered in English
        # text, so these are generated — with no lettering of their own, since
        # the tier already carries its label (CLAUDE.md).
        ic = VGroup()
        if t.get("icon"):
            # ROOT is the project directory the composed scene already defines,
            # and it imports pathlib as _Path — plain `Path` is not in scope
            path = _Path(t["icon"])
            if not path.is_absolute():
                path = ROOT / path
            if path.is_file():
                ic = ImageMobject(str(path))
                # FIT THE TIER'S PITCH, not a flat multiple of its height. The
                # tiers sit about one tier-height apart, so an icon scaled to
                # 1.45x that overlapped the ones above and below — four animals
                # in a heap. Fitted to a box instead, so a tall eagle and a wide
                # tiger both land inside their own row whatever their shape.
                box_h = th * float(spec.get("icon_scale", 0.96))
                box_w = th * float(spec.get("icon_w", 1.7))
                k = min(box_h / ic.height, box_w / ic.width)
                ic.scale(k)
        rows.append(VGroup(bar, name) if not outside else VGroup(bar))
        labels.append((name if outside else VGroup(), val, bar, ic))
    # BASE FIRST IN THE DATA, BASE LOWEST ON SCREEN
    stack = VGroup(*rows[::-1]).arrange(DOWN, buff=_u(6))
    extras = VGroup()
    right = VGroup()
    for out_name, val, bar, ic in labels:
        side = VGroup()
        if len(out_name):
            side.add(out_name)
        if len(val):
            side.add(val)
        if len(side):
            side.arrange(RIGHT, buff=_u(14))
            side.next_to(bar, RIGHT, buff=_u(18))
            right.add(side)
            extras.add(side)
    # ICONS IN ONE COLUMN, not beside each bar: the bars are different widths by
    # design, so hanging each icon off its own bar staggers them and the eye
    # reads the stagger as meaning something. A straight column on the left is
    # a key, which is what it is.
    icon_g = Group()
    if icons_on:
        left_x = min(b.get_left()[0] for _, _, b, _ in labels) - _u(28)
        for _, _, bar, ic in labels:
            if isinstance(ic, ImageMobject):
                ic.move_to([left_x - ic.width / 2, bar.get_center()[1], 0])
                icon_g.add(ic)
    g = Group(VGroup(stack, extras), icon_g) if icons_on else VGroup(stack, extras)
    head = VGroup()
    if spec.get("title"):
        head.add(r_rich(spec["title"], 30, R_GOLD))
    if spec.get("subtitle"):
        head.add(r_rich(spec["subtitle"], 22, R_DIM))
    if len(head):
        head.arrange(DOWN, buff=_u(8))
        # Group, not VGroup, once an ImageMobject is in the tree (CLAUDE.md):
        # a VGroup refuses a Group as a submobject and the render dies here
        g = (Group(head, g) if icons_on else VGroup(head, g)).arrange(
            DOWN, buff=_u(TAG_GAP + 8))
    self.place(g, y=spec.get("y", 0.32), grow=True, pad_w=spec.get("pad_w", 0.96))

    ats = spec.get("reveal_at") or []
    parts = []
    for k, (out_name, val, bar, ic) in enumerate(labels):
        # PHOTOS ARE Group, NOT VGroup — an ImageMobject is not a VMobject
        # (CLAUDE.md), so a tier with an icon is grouped the looser way.
        grp = Group(rows[k], out_name, val, ic) if isinstance(ic, ImageMobject) \
            else VGroup(rows[k], out_name, val)
        grp.set_opacity(0)
        parts.append(grp)
    for k, at in enumerate(ats[:len(parts)]):
        def go(k=k):
            self.cue("pop", gain=0.5)
            self.play(parts[k].animate.set_opacity(1), run_time=0.35)
        self._later(at, go)
    return _lg(g)


def beat_notes(self, spec):
    t = Text(spec.get("text", "नोट्स बटन पर आंसर"), font=R_FONT, font_size=30,
             color=R_CARD_INK, weight="BOLD")
    box = RoundedRectangle(width=t.width + _u(48), height=t.height + _u(26),
                           corner_radius=_u(14)).set_fill(R_GOLD, 1).set_stroke(R_GOLD, 2)
    t.move_to(box)
    g = VGroup(box, t)
    self.place(g, y=spec.get("y", 0.45), grow=False)
    return _lg(g)


# --------------------------------------------------------------- mechanisms -- #
def _leader(self, pill, target, side=LEFT):
    start = pill.get_edge_center(-side) if False else pill.get_center()
    ln = Line(pill.get_boundary_point(target - pill.get_center()), target)
    ln.set_stroke(INK, 2.2)
    dot = Dot(target, radius=_u(5), color=INK)
    return VGroup(ln, dot)


def beat_ions(self, spec):
    """Two ions side by side: the nucleus with its charge, the electron cloud
    around it, then the pull (inward arrows, stronger on the right) and the
    right-hand cloud contracting. The mechanism, not a picture of the result."""
    L, R = spec["left"], spec["right"]
    r0 = _u(spec.get("r", 185))
    atoms = []
    for side, a in ((LEFT, L), (RIGHT, R)):
        cloud = VGroup(*[Circle(radius=r0 * f).set_stroke(width=0).set_fill(R_TEAL, 0.10 + 0.05 * i)
                         for i, f in enumerate((1.0, 0.86, 0.72))])
        rng = np.random.default_rng(3 if side is LEFT else 5)
        dots = VGroup()
        for k in range(int(a.get("dots", 18))):
            ang = 2 * PI * k / int(a.get("dots", 18)) + rng.uniform(-0.12, 0.12)
            rr = r0 * rng.uniform(0.62, 0.95)
            dots.add(Dot([rr * np.cos(ang), rr * np.sin(ang), 0], radius=_u(6), color=R_TEAL))
        nuc = Circle(radius=_u(42)).set_fill(R_GOLD, 1).set_stroke(INK, 2)
        q = MathTex(r"+%d" % a["z"], color=R_CARD_INK, font_size=34).move_to(nuc)
        title = r_rich(a["sym"], 34, R_TEAL)
        atom = VGroup(cloud, dots, nuc, q)
        atoms.append((atom, cloud, dots, nuc, title))
    g = VGroup()
    la, ra = atoms[0][0], atoms[1][0]
    VGroup(la, ra).arrange(RIGHT, buff=_u(120))
    for atom, cloud, dots, nuc, title in atoms:
        title.next_to(atom, UP, buff=_u(26))
        g.add(atom, title)
    # labels, as pills, on the LEFT ion only (the right one is the same anatomy)
    p_nuc = r_pill(spec.get("nucleus_label", "नाभिक"), active=True, size=22)
    p_cloud = r_pill(spec.get("cloud_label", "इलेक्ट्रॉन मेघ"), size=22)
    p_nuc.next_to(la, DOWN, buff=_u(40)).shift(LEFT * _u(40))
    p_cloud.next_to(la, DOWN, buff=_u(40)).shift(RIGHT * _u(170))
    g.add(p_nuc, p_cloud)
    self.place(g, y=spec.get("y", 0.38), grow=False)
    lead_n = _leader(self, p_nuc, atoms[0][3].get_bottom())
    lead_c = _leader(self, p_cloud, atoms[0][1][0].point_at_angle(-PI / 3))
    g.add(lead_n, lead_c)
    _lg(g)
    for m in (p_nuc, p_cloud, lead_n, lead_c):
        m.set_opacity(0)

    def label_nuc():
        self.play(p_nuc.animate.set_opacity(1), lead_n.animate.set_opacity(1), run_time=0.35)

    def label_cloud():
        # THE PILL BEING NAMED IS THE WHITE ONE. The reference moves the white
        # fill to whichever part the narration names; the earlier pill goes
        # dark but stays (labels persist once shown).
        self.play(p_cloud.animate.set_opacity(1), lead_c.animate.set_opacity(1),
                  p_nuc.pill_box.animate.set_fill(R_PILL, 0.95).set_stroke(INK, 2.2),
                  p_nuc.pill_text.animate.set_color(INK),
                  p_cloud.pill_box.animate.set_fill(INK, 1).set_stroke(INK, 2),
                  p_cloud.pill_text.animate.set_color(R_CARD_INK), run_time=0.35)

    def pull():
        arrows = VGroup()
        for (atom, cloud, dots, nuc, title), n_ar, w in ((atoms[0], 4, 3), (atoms[1], 6, 5)):
            for k in range(n_ar):
                ang = 2 * PI * k / n_ar + PI / n_ar
                p0 = nuc.get_center() + r0 * 0.98 * np.array([np.cos(ang), np.sin(ang), 0])
                p1 = nuc.get_center() + _u(62) * np.array([np.cos(ang), np.sin(ang), 0])
                arrows.add(Arrow(p0, p1, buff=0, stroke_width=w, color=R_GOLD,
                                 max_tip_length_to_length_ratio=0.25))
        g.add(arrows)
        _lg(g)
        self.stage_mobs.append(arrows)
        self.cue("pop", gain=0.5)
        self.play(LaggedStart(*[GrowArrow(a) for a in arrows], lag_ratio=0.08), run_time=0.9)
        g.pull_arrows = arrows

    def shrink():
        atom, cloud, dots, nuc, title = atoms[1]
        k = spec.get("shrink", 0.80)
        arrows = getattr(g, "pull_arrows", VGroup())
        right = [a for a in arrows if np.linalg.norm(a.get_center() - nuc.get_center()) < r0 * 1.2]
        c0 = nuc.get_center()
        # the parts themselves, never a VGroup made for the occasion: that group
        # would reach the scene untagged and read as a stranger to the audit
        self.play(cloud.animate.scale(k, about_point=c0),
                  dots.animate.scale(k, about_point=c0),
                  *[a.animate.scale(k, about_point=c0) for a in right],
                  run_time=1.2, rate_func=smooth)
        # the two radii, measured from each nucleus, so the comparison is drawn
        rl = Line(atoms[0][3].get_center(), atoms[0][3].get_center() + RIGHT * r0 * 0.98).set_stroke(INK, 3)
        rr = Line(nuc.get_center(), nuc.get_center() + RIGHT * r0 * 0.98 * k).set_stroke(INK, 3)
        tl = r_pill(spec.get("left_r", "बड़ी त्रिज्या"), size=21)
        tr = r_pill(spec.get("right_r", "छोटी त्रिज्या"), active=True, size=21)
        tl.next_to(atoms[0][0], DOWN, buff=_u(26))
        tr.next_to(atom, DOWN, buff=_u(26))
        self.play(FadeOut(p_nuc), FadeOut(p_cloud), FadeOut(lead_n), FadeOut(lead_c), run_time=0.25)
        g.add(rl, rr, tl, tr)
        _lg(g)
        self.stage_mobs.extend([rl, rr, tl, tr])
        self.cue("pop", gain=0.5)
        self.play(Create(rl), Create(rr), FadeIn(tl), FadeIn(tr), run_time=0.6)

    for key, fn in (("nucleus_at", label_nuc), ("cloud_at", label_cloud),
                    ("pull_at", pull), ("shrink_at", shrink)):
        if spec.get(key) is not None:
            self._later(spec[key], fn)
    # electrons drift, so the cloud reads as a cloud and not a drawing of one
    for atom, cloud, dots, nuc, title in atoms:
        dots.add_updater(lambda m, dt, c=nuc: m.rotate(0.18 * dt, about_point=c.get_center()))
    return _lg(g)


def beat_pedigree(self, spec):
    """A three-generation pedigree, drawn a generation at a time: squares are
    males, circles females, filled means the trait is shown."""
    s = _u(46)                              # symbol size

    def male(fill):
        m = Square(side_length=s).set_stroke(INK, 3)
        return m.set_fill(R_GOLD if fill else R_PILL, 1)

    def female(fill):
        m = Circle(radius=s / 2).set_stroke(INK, 3)
        return m.set_fill(R_GOLD if fill else R_PILL, 1)

    gy = [0, -_u(170), -_u(340)]
    # generation I: affected father x mother
    I1, I2 = male(True).move_to([-_u(70), gy[0], 0]), female(False).move_to([_u(70), gy[0], 0])
    mI = Line(I1.get_right(), I2.get_left()).set_stroke(INK, 3)
    dI = Line(mI.get_center(), mI.get_center() + DOWN * _u(70)).set_stroke(INK, 3)
    # generation II: three children, one of them marries
    xs2 = [-_u(260), -_u(60), _u(140)]
    kids2 = [male(True), female(False), male(True)]
    for k, x in zip(kids2, xs2):
        k.move_to([x, gy[1], 0])
    sib2 = Line([xs2[0], gy[1] + _u(55), 0], [xs2[-1], gy[1] + _u(55), 0]).set_stroke(INK, 3)
    drops2 = VGroup(*[Line([x, gy[1] + _u(55), 0], [x, gy[1] + s / 2, 0]).set_stroke(INK, 3) for x in xs2])
    sp2 = female(False).move_to([_u(290), gy[1], 0])
    m2 = Line(kids2[2].get_right(), sp2.get_left()).set_stroke(INK, 3)
    d2 = Line(m2.get_center(), m2.get_center() + DOWN * _u(70)).set_stroke(INK, 3)
    # generation III
    xs3 = [_u(130), _u(300)]
    kids3 = [female(True), male(False)]
    for k, x in zip(kids3, xs3):
        k.move_to([x, gy[2], 0])
    sib3 = Line([xs3[0], gy[2] + _u(55), 0], [xs3[-1], gy[2] + _u(55), 0]).set_stroke(INK, 3)
    drops3 = VGroup(*[Line([x, gy[2] + _u(55), 0], [x, gy[2] + s / 2, 0]).set_stroke(INK, 3) for x in xs3])
    roman = VGroup(*[Text(r, font=R_FONT, font_size=26, color=R_TEAL, weight="BOLD").move_to([-_u(440), y, 0])
                     for r, y in zip(("I", "II", "III"), gy)])
    gen1 = VGroup(I1, I2, mI, roman[0])
    gen2 = VGroup(dI, sib2, drops2, *kids2, sp2, m2, roman[1])
    gen3 = VGroup(d2, sib3, drops3, *kids3, roman[2])
    legend = VGroup(
        VGroup(male(False).scale(0.6), Text("पुरुष", font=R_FONT, font_size=22, color=INK, weight="BOLD")).arrange(RIGHT, buff=_u(10)),
        VGroup(female(False).scale(0.6), Text("स्त्री", font=R_FONT, font_size=22, color=INK, weight="BOLD")).arrange(RIGHT, buff=_u(10)),
        VGroup(male(True).scale(0.6), Text("लक्षण वाले", font=R_FONT, font_size=22, color=R_GOLD, weight="BOLD")).arrange(RIGHT, buff=_u(10)),
    ).arrange(RIGHT, buff=_u(36))
    chart = VGroup(gen1, gen2, gen3)
    legend.next_to(chart, DOWN, buff=_u(40))
    title = r_rich(spec.get("title", "वंशावली (Pedigree)"), 30, R_TEAL)
    title.next_to(chart, UP, buff=_u(30))
    g = VGroup(title, chart, legend)
    self.place(g, y=spec.get("y", 0.30), grow=False)
    ats = spec.get("gen_at", [])
    for part in (gen2, gen3, legend):
        part.set_opacity(0)
    parts = [gen2, gen3, legend]
    for part, a in zip(parts, ats[1:] + [spec.get("legend_at")]):
        if a is None:
            continue

        def go(part=part):
            self.cue("write", gain=0.5)
            self.play(part.animate.set_opacity(1), run_time=0.6)
        self._later(a, go)
    # the trait being followed: ring every filled symbol in turn
    if spec.get("trace_at") is not None:
        def trace():
            hits = [I1, kids2[0], kids2[2], kids3[0]]
            rings = VGroup(*[Circle(radius=s * 0.85).move_to(h).set_stroke(R_GOLD, 3) for h in hits])
            g.add(rings)
            _lg(g)
            self.stage_mobs.append(rings)
            self.play(LaggedStart(*[Create(r) for r in rings], lag_ratio=0.25), run_time=1.2)
        self._later(spec["trace_at"], trace)
    return _lg(g)


def beat_loop(self, spec):
    """A feedback cycle: pills round a ring joined by curved arrows, arriving as
    they are named, then a light running the loop faster each lap.

    STROKE ONLY. Revealing an arc with set_opacity turns its FILL on too, and
    each arrow filled in as a solid white crescent across the middle of the
    screen. Arcs are hidden and shown by their stroke; their tips by their fill.
    """
    nodes = spec["nodes"]
    n = len(nodes)
    R = _u(300)
    angs = [PI / 2 - 2 * PI * k / n for k in range(n)]      # clockwise from the top
    pills = [r_pill(t, tone="gold", size=22) for t in nodes]
    for p, ang in zip(pills, angs):
        if p.width > _u(430):
            p.scale(_u(430) / p.width)
        p.move_to([R * np.cos(ang) * 1.15, R * np.sin(ang) * 0.92, 0])
    arrows = VGroup()
    for k in range(n):
        a, b = pills[k], pills[(k + 1) % n]
        start = a.get_boundary_point(normalize(b.get_center() - a.get_center()))
        end = b.get_boundary_point(normalize(a.get_center() - b.get_center()))
        arr = CurvedArrow(start, end, angle=-0.55, color=R_DIM,
                          tip_length=_u(26), stroke_width=5)
        arr.set_fill(opacity=0)
        arrows.add(arr)
    g = VGroup(arrows, *pills)
    note = r_fact(spec.get("centre", ""), "", "gold", 22) if spec.get("centre") else VGroup()
    if len(note):
        note.next_to(g, DOWN, buff=_u(26))
        g.add(note)
    self.place(g, y=spec.get("y", 0.34), grow=False)

    def hide(m):
        m.set_stroke(opacity=0)
        for t in m.get_tips():
            t.set_opacity(0)

    def show(m):
        m.set_stroke(opacity=1)
        for t in m.get_tips():
            t.set_opacity(1)

    for p in pills:
        p.set_opacity(0)
    for arr in arrows:
        hide(arr)
    note.set_opacity(0)
    ats = spec.get("reveal_at", [])
    for k, at in enumerate(ats):
        def go(k=k):
            self.cue("pop", gain=0.5)
            self.play(pills[k].animate.set_opacity(1), run_time=0.35)
            if k:                       # the arrow that led here
                prev = arrows[k - 1]
                self.play(prev.animate.set_stroke(opacity=1),
                          *[t.animate.set_opacity(1) for t in prev.get_tips()],
                          run_time=0.25)
            if k == n - 1:              # and the one that closes the loop
                last = arrows[n - 1]
                self.play(last.animate.set_stroke(opacity=1),
                          *[t.animate.set_opacity(1) for t in last.get_tips()],
                          run_time=0.25)
        self._later(at, go)
    if spec.get("spin_at") is not None:
        def spin():
            dot = Dot(radius=_u(11), color=R_GOLD)
            dot._layout_group = getattr(g, "_ref_key", id(g))
            self.add(dot)
            self.stage_mobs.append(dot)
            if len(note):
                self.play(note.animate.set_opacity(1), run_time=0.3)
            for rt in (1.5, 1.0, 0.7):
                for arr in arrows:
                    self.play(MoveAlongPath(dot, arr), run_time=rt / n, rate_func=linear)
            self.remove(dot)
        self._later(spec["spin_at"], spin)
    return _lg(g)



def beat_complex(self, spec):
    """A coordination entity: the central metal, and its ligands counted onto it.

    THE COUNT IS THE ANSWER, so it is DRAWN. "उप-सहसंयोजन संख्या" is the number
    of ligands bonded straight to the central metal, which is a discrete
    quantity that is the whole mark — exactly what docs/routing-veo-and-svg.md
    refuses to hand to a generator. Here the ligands arrive one at a time and a
    tally counts up with them, so the six is arrived at on screen rather than
    asserted; a student who loses the thread can recount it from the picture.

    GEOMETRY IS THE TEXTBOOK'S, not a ring. Six ligands go to the vertices of an
    octahedron drawn in the plane — four square, one up, one down — because that
    is the shape beside this definition in the book, and two go opposite each
    other because dicyanidoargentate is linear. Drawing six evenly round a
    circle would be tidier and would teach the wrong shape.

    SCRIPT SPLIT, as everywhere: the metal and the ligand are formulae and go
    through MathTex; every Hindi word goes through Text. Devanagari is never
    glued inside a symbol (CLAUDE.md).
    """
    metal = spec["metal"]                       # e.g. "Co^{3+}"
    lig = spec["ligand"]                        # e.g. "NH_3"
    n = int(spec["n"])
    geom = spec.get("geometry", "octahedral")
    # THE SPREAD IS BOUNDED BY THE BAND, not by taste. Content lives between the
    # caption strip (ends at 0.26 of frame height) and the presenter (starts at
    # 0.50) — about 460px. An octahedron of radius R is 2R + one ligand tall, so
    # R past ~185 pushes the top ligand into the caption, which is exactly what
    # happened at 268. Bigger is bought in the BOXES and the type instead.
    R = _u(spec.get("r", 182))

    # where each ligand sits, in drawing order
    # EVENLY ROUND THE CENTRE, and the reason is the band, not the chemistry.
    # The first cut placed six at octahedral positions — four square, one up,
    # one down — because that is the shape beside this definition in the book.
    # It does not fit: the band between caption and presenter is ~460px, so the
    # radius has to come down to ~180, and at that radius the axial box lands on
    # top of the two diagonal ones. Evenly spaced, adjacent ligands are 2R·sin30
    # apart and clear each other. This is a schematic of HOW MANY are bonded,
    # which is what the question asks; it does not claim a bond geometry.
    if geom == "linear" or n == 2:
        angles = [PI, 0]
    else:
        angles = [PI / 2 - 2 * PI * k / n for k in range(n)]

    # CENTRE THE SYMBOL, NOT THE SYMBOL-PLUS-CHARGE. move_to() centres a
    # mobject's bounding box, and a superscript hangs up and to the right — so
    # centring "Co^{3+}" as one object pushes the "Co" down and left and it sits
    # visibly off in its disc. The base and the charge are therefore separate:
    # the base goes dead centre, the charge rides on its shoulder.
    # ONE MathTex, ALIGNED ON THE BASE, IN A DISC SIZED TO HOLD IT. Centring
    # "Co^{3+}" as a whole puts the symbol down-left of the middle, because the
    # superscript drags the bounding box. Splitting it into two mobjects fixed
    # that but pushed a two-character charge outside the disc — "Co³⁺" rendered
    # as "Co³" with the plus over the rim. So the charge stays part of the same
    # MathTex (it is one formula), the group is shifted until the BASE sits dead
    # centre, and the circle is grown to whatever that costs.
    base, charge = (metal.split("^", 1) + [""])[:2]
    parts = [base] + ([f"^{{{charge.strip('{}')}}}"] if charge else [])
    core_tx = MathTex(*parts, color=R_CARD_INK, font_size=spec.get("sym_size", 44))
    need = max(core_tx.width, core_tx.height) * 0.60 + _u(14)
    core = Circle(radius=max(_u(spec.get("core_r", 66)), need))
    core.set_fill(R_GOLD, 1).set_stroke(INK, 2.5)
    core_tx.shift(core.get_center() - core_tx[0].get_center())
    centre = VGroup(core, core_tx)

    bonds, ligs = VGroup(), VGroup()
    for a in angles:
        d = np.array([np.cos(a), np.sin(a), 0.0])
        box = VGroup(
            RoundedRectangle(corner_radius=_u(12),
                             width=_u(spec.get("lig_w", 146)),
                             height=_u(spec.get("lig_h", 74)))
            .set_fill(R_CARD, 1).set_stroke(R_TEAL, 2.8),
        )
        lt = MathTex(lig, color=R_CARD_INK, font_size=spec.get("lig_size", 38))
        lt.move_to(box[0])
        box.add(lt)
        box.move_to(core.get_center() + d * R)
        bonds.add(Line(core.get_center() + d * core.radius,
                       box.get_center() - d * _u(72)).set_stroke(INK, 3.8))
        ligs.add(box)

    tally = r_pill(spec.get("tally", "सीधे जुड़े लिगैण्ड") + " : 0", size=24)
    g = VGroup(bonds, centre, ligs, tally)
    tally.next_to(VGroup(bonds, centre, ligs), DOWN, buff=_u(46))
    self.place(g, y=spec.get("y", 0.40), grow=False)
    _lg(g)
    for m in list(bonds) + list(ligs):
        m.set_opacity(0)
    tally.set_opacity(0)

    def show(i):
        def run():
            if i == 0:
                self.play(tally.animate.set_opacity(1), run_time=0.2)
            new = r_pill(f"{spec.get('tally', 'सीधे जुड़े लिगैण्ड')} : {i + 1}",
                         active=True, size=24).move_to(tally)
            self.cue("pop", gain=-2.0)
            self.play(bonds[i].animate.set_opacity(1),
                      ligs[i].animate.set_opacity(1),
                      Transform(tally, new), run_time=0.34)
        return run

    at = spec.get("reveal_at") or []
    for i in range(n):
        if i < len(at):
            self._later(at[i], show(i))

    def answer():
        # the count, restated as the thing that earns the mark
        txt = r_rich(spec.get("answer", "उप-सहसंयोजन संख्या"), 34, R_GOLD)
        num = MathTex(r"=\;%d" % n, color=R_GOLD, font_size=46)
        row = VGroup(txt, num).arrange(RIGHT, buff=_u(16))
        row.next_to(tally, DOWN, buff=_u(34))
        g.add(row)
        _lg(g)
        self.stage_mobs.append(row)
        self.cue("reveal", gain=-3.0)
        self.play(FadeIn(row, shift=UP * _u(12)), run_time=0.5)

    if spec.get("answer_at") is not None:
        self._later(spec["answer_at"], answer)
    return _lg(g)

def beat_config(self, spec):
    """Element cards showing electronic configuration, side by side.

    WHY THIS EXISTS. CHE-C4-SA-01's second effect — "Zr और Hf के गुणों में काफी
    समानता" — was one pill of text for forty-five seconds, and the pill asserts
    the similarity without ever showing WHY. The reason is a configuration: Hf
    sits a whole period below Zr and should be much larger, but fourteen 4f
    electrons are filled in between, and the contraction they cause cancels the
    increase. That is a fact about where electrons go, so a card of
    configurations shows it and a sentence cannot.

    NO RADII ARE PRINTED HERE, on purpose. The obvious version of this card puts
    Zr 145 pm beside Hf 144 pm, and those numbers are not in this repo and not on
    the answer sheet — only in a textbook nobody has scanned for this chapter. A
    number on screen is a claim a student will copy into an exam, so this draws
    the part that IS certain and leaves the measurement out. `r` may be supplied
    per item later, and `values` then prints it, the way beat_shrink does.

    CONFIGURATIONS GO THROUGH MathTex, never Text. The house face has no
    superscripts at all (CLAUDE.md), so "4f^{14}" set in Poppins is three tofu
    boxes. The symbol and the Devanagari note stay in Text; the two are never
    glued into one string.
    """
    items = spec["items"]
    title = r_rich(spec.get("title", ""), 30, R_GOLD) if spec.get("title") else VGroup()
    cols = VGroup()
    for it in items:
        sym = Text(str(it["sym"]), font=R_FONT, font_size=spec.get("sym_size", 44),
                   color=INK, weight="BOLD")
        z = (Text(f"Z = {it['z']}", font=R_FONT, font_size=20, color=R_DIM,
                  weight="BOLD") if it.get("z") else VGroup())
        # the configuration, and the fragment that explains the point in gold
        cfg = MathTex(*( [it["cfg"]] if not it.get("mark")
                         else list(_split_mark(it["cfg"], it["mark"])) ),
                      color=R_BODY, font_size=spec.get("cfg_size", 34))
        if it.get("mark") and len(cfg) == 3:
            cfg[1].set_color(R_GOLD)
        card = RoundedRectangle(corner_radius=_u(10),
                                width=max(cfg.width, sym.width) + _u(46),
                                height=sym.height + cfg.height + _u(64))
        card.set_stroke(R_GOLD if it.get("mark") else R_GRID, 2.4).set_fill(R_PILL, 0.55)
        stack = VGroup(sym, z, cfg) if len(z) else VGroup(sym, cfg)
        stack.arrange(DOWN, buff=_u(8)).move_to(card)
        cols.add(VGroup(card, stack))
    cols.arrange(RIGHT, buff=_u(18))
    W = config.frame_width * 0.92
    if cols.width > W:
        cols.scale(W / cols.width)
    g = VGroup(cols)
    if len(title):
        title.next_to(cols, UP, buff=_u(TAG_GAP + 6))
        g.add(title)
    if spec.get("note"):
        note = r_wrap(spec["note"], W - _u(40), 24, R_TEAL)
        note.next_to(cols, DOWN, buff=_u(14))
        g.add(note)
    self.place(g, y=spec.get("y", 0.25), grow=False)
    # the cards land one at a time, left to right, so the eye reads the series
    # in the order the narration names it
    reveal = spec.get("reveal_at") or []
    for k, col in enumerate(cols):
        if k < len(reveal):
            col.set_opacity(0)

            def show(col=col):
                self.cue("reveal", gain=-3.0)
                self.play(col.animate.set_opacity(1), run_time=0.4)
            self._later(reveal[k], show)
    return _lg(g)


def _split_mark(cfg: str, mark: str):
    """cfg split into (before, mark, after) so the marked fragment can be gold."""
    i = cfg.find(mark)
    if i < 0:
        return (cfg,)
    return (cfg[:i] or r"\,", mark, cfg[i + len(mark):] or r"\,")



def beat_figure(self, spec):
    """A figure that is a PICTURE, with its names set in the margins.

    The base scene's `figure` beat draws from Manim primitives or traces a scan,
    and hangs each label on the drawing at a fraction of its own box. That is
    right for an apparatus with four names on it. It is wrong for a सचित्र
    question whose answer IS a labelled diagram: BIO-C2-SA-02 carries FIFTEEN,
    the parts they name are clustered (three uterine walls within 5% of each
    other, six tube and ovary parts inside a tenth of the frame), and placing
    each name at its own part piled them on top of one another — एम्पुला over
    इस्थमस over अंडवाहिनी — with अंडाशय pushed off the frame edge. Nudging them
    apart one at a time only moved the collision somewhere else.

    So the names go into two MARGIN COLUMNS and a leader line carries each back
    to its part. Columns cannot collide by construction: each side is a stack of
    evenly spaced slots running the full height of the stage, which is about
    twice the figure's own height. It is also how the book prints it.

    Anything that is not `draw: "image"` is left to the base scene.
    """
    if spec.get("type") != "figure" or spec.get("draw") != "image":
        return _orig_build_beat(self, spec)

    name = spec.get("name", "figure")
    img = ImageMobject(str(ROOT / "assets" / f"{name}.png"))
    # SIZED HERE. The stage fit below only ever GROWS a figure, and this one
    # arrives wider than the frame — left alone it ran off both edges and took
    # the ovaries with it. Narrow on purpose: the margins carry the names.
    img.scale_to_fit_width(config.frame_width * float(spec.get("width", 0.88)))
    g = Group(img)

    # NAMED ANCHORS THAT RIDE WITH THE PICTURE, from anchors.json — fractions of
    # the image, placed on the artwork and checked against it by
    # tools/figure_anchor_gate.py. A leader drawn to a scene coordinate would
    # land somewhere else the moment the figure is rescaled; these are invisible
    # dots INSIDE the group, so they scale and move with it.
    import json as _j
    af = ROOT / "anchors.json"
    if af.is_file():
        marks, ul, w, h = {}, img.get_corner(UL), img.width, img.height
        for key, (fx, fy) in _j.loads(af.read_text(encoding="utf-8")).items():
            # EVERY ANCHOR GETS A MIRROR TWIN, "<name>#m", at 1-fx. A tract that
            # is drawn on both sides can be named from either margin by pointing
            # at its own other copy — without it, ten of fifteen anchors fell
            # left of centre and one column carried ten names to the other's
            # five. The gate refuses a mirror anchor on an asymmetric figure.
            for nm, px in ((key, fx), (key + "#m", 1.0 - fx)):
                d = Dot(radius=0.001).set_opacity(0)
                d.move_to(ul + np.array([px * w, -fy * h, 0]))
                marks[nm] = d
                g.add(d)
        g.anchors = marks

    c0, bw, bh = self.stage_box()
    want = float(spec.get("fill", 0.92))
    if g.height > 0 and g.width > 0:
        k = min((bw * want) / g.width, (bh * want) / g.height)
        if k > 1.0:
            g.scale(k)
        # CENTRED EITHER WAY. The fit only grows, so a beat that deliberately
        # asks for a SMALL figure never reached move_to and sat at the origin —
        # and the band is the upper region, not centred on the origin, so the
        # picture hung below the floor and the layout guard reported sixty
        # frames out of band.
        g.move_to(c0)

    self._labels = []
    tag = id(g)
    mark_group(g, tag)
    _px = _u(1)
    # The margin is what is left either side of the picture. Names are scaled to
    # FIT it rather than set at a fixed size: the long ones decide the size, and
    # letting them overrun is what pushed अंडाशय off the frame edge.
    margin = max((bw - g.width) / 2.0 - _u(10), _u(120))
    sides = {}
    for l in spec.get("labels", []):
        sides.setdefault(l.get("col", "l"), []).append(l)

    # ONE TYPE SIZE FOR THE WHOLE SET, decided by the LONGEST name.
    # Scaling each label only when it personally overran the margin gave a
    # diagram whose names were set in four different sizes — फिंब्री and योनि
    # large, गर्भाशय फंडस and इन्फन्डीबुलम visibly smaller beside them — which
    # reads as a mistake rather than as emphasis. A labelled diagram is one
    # piece of typography: every name is the same size, and the longest one is
    # what that size has to be.
    _ref_h = Text("क", font=R_FONT, font_size=40, weight="BOLD").height
    _widest = 0.0
    for l in spec.get("labels", []):
        _t = Text(str(l["text"]), font=R_FONT, font_size=40, weight="BOLD")
        _t.scale(float(l.get("rel", 0.055)) * g.height / _ref_h)
        _widest = max(_widest, _t.width)
    _fit = min(1.0, margin / _widest) if _widest else 1.0
    for side, items in sides.items():
        items.sort(key=lambda l: l.get("slot", 0))
        n = len(items)
        top, bot = c0[1] + bh / 2 - _u(30), c0[1] - bh / 2 + _u(30)
        for idx, l in enumerate(items):
            y = top if n == 1 else top - (top - bot) * idx / (n - 1)
            t = Text(str(l["text"]), font=R_FONT, font_size=40,
                     color=R_BODY, weight="BOLD")
            # Sized against a REFERENCE glyph, not its own height: Devanagari
            # height depends on which matras a word happens to carry, so scaling
            # every label to one box makes a short word tower over a long one.
            t.scale(float(l.get("rel", 0.055)) * g.height / _ref_h * _fit)
            t.move_to([c0[0] - bw / 2, y, 0],
                      aligned_edge=LEFT) if side == "l" else \
                t.move_to([c0[0] + bw / 2, y, 0], aligned_edge=RIGHT)
            lab, anchors, part = t, getattr(g, "anchors", None), l.get("part")
            if anchors and part in (anchors or {}):
                tgt = anchors[part].get_center()
                # The leader leaves the name on the side FACING the figure and
                # turns once, so it reads as a pointer rather than a line drawn
                # across the drawing.
                start = (t.get_right() + RIGHT * _u(6)) if side == "l" \
                    else (t.get_left() + LEFT * _u(6))
                elbow = np.array([start[0] + (_u(18) if side == "l" else -_u(18)),
                                  tgt[1], 0])
                arm = VMobject().set_points_as_corners([start, elbow, tgt])
                arm.set_stroke(R_BODY, 2.2)
                lab = VGroup(arm, Dot(tgt, radius=_u(5), color=R_BODY), t)
            mark_group(lab, tag)
            self._labels.append((int(l["at"]), lab))
    return g


PyqPart.caption = _ref_caption
PyqPart._later = _later
PyqPart._rtag = _rtag
REF_BEATS = ("rtable", "rlist", "statement", "facts", "rchain", "notes",
             "ions", "pedigree", "loop", "codons", "shrink", "pyramid",
             "complex", "config", "figure")
for _n in REF_BEATS:
    setattr(PyqPart, f"beat_{_n}", globals()[f"beat_{_n}"])

_orig_build_beat = PyqPart.build_beat



def _build_beat_ref(self, spec):
    fn = getattr(self, f"beat_{spec['type']}", None)
    if spec["type"] in REF_BEATS:
        return fn(spec)
    return _orig_build_beat(self, spec)


PyqPart.build_beat = _build_beat_ref

