"""Figures for docs/writeups/2026-11-co-review-corpus.md (stdlib only).

    python3 docs/writeups/figures/make_figures.py

Colour roles: violet = data, green = model processing, blue = what reviewers use,
amber = external sources, grey = people.
"""
from pathlib import Path

OUT = Path(__file__).parent
FONT = "IBM Plex Sans, Helvetica, Arial, sans-serif"
C = {  # fill, stroke
    "data": ("#EEE8FA", "#6B4FA8"), "model": ("#E6F4EA", "#1E7A43"),
    "use": ("#EAF1FC", "#1D5BB8"), "ext": ("#FDF3E1", "#B7791F"), "person": ("#F1F2F4", "#5F6673"),
}


def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def box(x, y, w, h, role, title, lines=()):
    f, s = C[role]
    out = [f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="8" fill="{f}" stroke="{s}" stroke-width="1.5"/>',
           f'<text x="{x + 12}" y="{y + 22}" font-size="14" font-weight="600" fill="#15181D">{esc(title)}</text>']
    for i, ln in enumerate(lines):
        out.append(f'<text x="{x + 12}" y="{y + 42 + i * 17}" font-size="12" fill="#2B3038">{esc(ln)}</text>')
    return out


def arrow(x1, y1, x2, y2, label=""):
    out = [f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="#4B5260" stroke-width="1.5" marker-end="url(#a)"/>']
    if label:
        out.append(f'<text x="{(x1 + x2) / 2 + 6}" y="{(y1 + y2) / 2 - 4}" font-size="11" fill="#4B5260">{esc(label)}</text>')
    return out


def legend(x, y, roles):
    out, cx = [], x
    for role, name in roles:
        f, s = C[role]
        out += [f'<rect x="{cx}" y="{y}" width="14" height="14" rx="3" fill="{f}" stroke="{s}"/>',
                f'<text x="{cx + 20}" y="{y + 11}" font-size="12" fill="#2B3038">{esc(name)}</text>']
        cx += 30 + 7 * len(name)
    return out


def svg(w, h, body):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" '
            f'font-family="{FONT}"><defs><marker id="a" viewBox="0 0 10 10" refX="9" refY="5" '
            'markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0,0 L10,5 L0,10 z" '
            f'fill="#4B5260"/></marker></defs><rect width="{w}" height="{h}" fill="#FFFFFF"/>'
            + "".join(body) + "</svg>\n")


def pipeline():
    b = []
    b += box(20, 20, 250, 96, "ext", "GitHub issue threads", ["Contributions (legacy, 2016–2025)",
                                                            "BiocContributions (2026–)", "90,211 comments, 4,376 issues"])
    b += box(20, 150, 250, 96, "data", "Review corpus", ["assignee, not bot or submitter,", "> 1,500 characters",
                                                       "2,433 comments · 1,657 submissions"])
    b += arrow(145, 116, 145, 150, "select")
    stages = [("1. Extract", "Haiku 5.5 · 2,433 calls", "kind, findings, structure, tone"),
              ("2. Cluster", "Sonnet 5.5 · 16 calls", "26,669 findings → 336 items"),
              ("3. Assign", "Haiku 5.5 · 326 batches", "each finding → one item (95%)"),
              ("4. Report", "Sonnet 5.5 + counting", "tables, shares, quotes, examples")]
    for i, (t, m, d) in enumerate(stages):
        b += box(330, 20 + i * 90, 260, 70, "model", t, [m, d])
    for i in range(3):
        b += arrow(460, 90 + i * 90, 460, 110 + i * 90)
    b += arrow(270, 198, 330, 55)
    outs = [("checklist.md", "16 categories, ranked items"), ("structure.md", "how reviews are laid out"),
            ("examples.md", "3 anonymised reviews")]
    for i, (t, d) in enumerate(outs):
        b += box(650, 20 + i * 76, 230, 58, "data", t, [d])
    b += arrow(590, 325, 650, 49)
    b += box(650, 268, 230, 70, "use", "Co-review skills", ["First review, Follow-up", "(app/skills/*.md)"])
    b += arrow(765, 230, 765, 268, "condensed")
    b += legend(20, 384, [("ext", "external source"), ("data", "data / outputs"), ("model", "model step"),
                          ("use", "used in the app")])
    (OUT / "corpus-pipeline.svg").write_text(svg(900, 410, b))


def pane():
    b = []
    b += box(20, 20, 400, 300, "person", "Review detail (left)", ["package, submitter, reviewer, stage", "whose move, days waiting",
                                                                   "issue timeline", "current checks (r-universe)", "versions"])
    b += box(450, 20, 270, 150, "use", "Co-review chat (top right)", ["skill buttons: Follow-up,",
                                                                      "Check triage, First review,",
                                                                      "Fit & overlap, Nudge",
                                                                      "answers cite comments and",
                                                                      "code lines; tool calls shown"])
    b += box(450, 190, 270, 130, "use", "Shared draft (bottom right)", ["agent edits it directly",
                                                                        "diff + undo; Edit / Preview /",
                                                                        "Split / pop-out preview",
                                                                        "reviewer copies and posts it"])
    b += box(750, 20, 140, 86, "ext", "Agent reads", ["thread, checks,", "logs, source at", "built commit"])
    b += box(750, 126, 140, 70, "data", "Skill text", ["corpus checklist,", "review structure"])
    b += arrow(750, 63, 720, 63)
    b += arrow(750, 161, 720, 140)
    b += box(20, 350, 400, 70, "person", "Reviewer", ["asks, edits, decides, posts", "(the agent never posts)"])
    b += arrow(420, 385, 450, 300)
    b += legend(20, 446, [("person", "existing page / person"), ("use", "co-review pane"),
                          ("ext", "agent context"), ("data", "from the corpus")])
    (OUT / "review-pane.svg").write_text(svg(910, 472, b))


if __name__ == "__main__":
    pipeline()
    pane()
