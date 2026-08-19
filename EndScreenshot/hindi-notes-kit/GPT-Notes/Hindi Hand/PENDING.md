# Status — Hindi Hand

All six board chapters are rendered, QA'd and published under `chapters/`. 59 pages.

| chapter | pages | state |
|---|---|---|
| MP/Ch3 — जनन स्वास्थ्य | 5 | complete |
| MP/Ch4 — वंशागति तथा विविधता | 6 + 2 dia | complete (dia-02 flagged below) |
| MP/Ch5 — वंशागति का आणविक आधार | 6 + 2 dia | complete |
| Rajasthan/Ch3 | 8 | complete |
| Rajasthan/Ch4 | 9 + 1 dia | complete |
| Rajasthan/Ch5 | 9 + 1 dia | complete (2 pages off-spec, see below) |
| Common/Ch3 | 0 / 5 | never rendered — see below |

Rebuild any chapter with `python gen_hindi.py <ids>` then `python publish.py`.

## Open items

**1. `Common/Ch3` — 5 pages, never rendered.** The board-less `Ch3_Top5_PYQ_Hindi.html`. Its
content covers the same जनन स्वास्थ्य ground as MP/Ch3 and Rajasthan/Ch3, both already done, so it
may be redundant rather than a third board. Render with:

    python gen_hindi.py ch3-page-01 ch3-page-02 ch3-page-03 ch3-page-04 ch3-page-05

**2. `MP/Ch4/dia-02` (dihybrid Punnett square) — recommended for DELETION.** Two of sixteen
genotypes are wrong after two attempts and its Hindi labels garble (झुर्रीदार → सुरीदार). The same
Punnett square already appears, all sixteen cells correct, as a hand-ruled [[TABLE]] on
MP/Ch4/page-05. To remove: delete `page-contents/mp-ch4-dia-02.md` and `chapters/MP/Ch4/dia-02.jpg`,
then re-run publish.py.
*General rule:* figures that are mostly text-in-cells belong in a [[TABLE]] on a theory page.
Diagram pages earn their keep on structural drawings (helix, phage, crosses, transcription unit).

**3. `Rajasthan/Ch4/dia-01` (HbS) — draws more than the source.** After the anchor-leak fix it no
longer copies the style anchor's helix, but it still adds nucleotide chains with pentagon sugars and
a sickle-cell shape that are not in the source figure. Biologically correct and arguably better for
a student; not a faithful copy. Keep, or re-roll for strictness.

**4. `Rajasthan/Ch5` page-08 and page-09 — letter height off-spec** (19 px and 31 px against the
24.5 px target). Two re-rolls each landed the same way, because the cause is NOT sampling variance:
page-08 carries more content than the 30-row budget so the model shrinks the writing to fit, and
page-09 is the chapter's short tail page so it enlarges. The real fix is rebalancing the content
across that chapter's last pages (`ROWS_PER_PAGE` / the per-block row estimate in import_htmls.py)
and re-rendering the tail — not more re-rolls.

## Boards

There is no UP board in this pipeline — `top5_pyq_html/Class12/Biology_PYQs/Hindi/` holds only MP,
Rajasthan and the board-less Ch3. `import_htmls.py` already maps a `UP/` folder the same way, so
dropping `UP/ChN/UP_ChN_Top5_PYQ_Hindi.html` files in would convert with no code change.
(The UP set in `GPT-Notes/Bio PYQ Top5/` belongs to a different pipeline and a different style.)
