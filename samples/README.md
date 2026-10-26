# Sample reels

The three latest delivered reels, as the standard to match. The videos are attached to the GitHub Release
[`samples-2026-10-26`](https://github.com/Tomar606/manim-video-solution-generator/releases/tag/samples-2026-10-26)
(GitHub does not take files over 100 MB inside a repository). Everything that built them is in this repo.

| Video | What it shows best | Build files |
|---|---|---|
| **HIS-C6-SA-04**: भक्ति संतों के उपदेश (2:42) | Veo behind every beat; real period paintings in a gallery that fills in and returns at the recap; the `pothi` theme | `lab/kit_test/make_his_c6_04_plans.py`, `lab/kit_test/plan_his_c6_sa_04_p1.json`, `lab/kit_test/themes/pothi.css`, `projects/his-c6-sa-04/` (meta, captions, Veo prompts and shot list, exam sheets, answer page), `library/backgrounds/photos/history/bhakti/`, plates `bk-boats`, `bk-card` |
| **HIS-C11-SA-01**: जननेता गाँधी (2:15) | 1930 photographs, the `khadi` theme; hook and question at 1.2×, the rest at 1.1× | `lab/kit_test/make_his_c11_01_plans.py`, `lab/kit_test/plan_his_c11_sa_01_p1.json`, `lab/kit_test/themes/khadi.css`, `projects/his-c11-sa-01/`, `library/backgrounds/photos/history/gandhi/`, `history/c11/`, plates `kh-salt`, `kh-card` |
| **CHE — मोलरता** (2:02) | Realistic glassware drawn as stage elements, the presenter grade every reel now uses, the answer page at the narrator's cue; the `chemlab` theme | `lab/kit_test/make_che_molarity_plans.py`, `lab/kit_test/plan_che_molarity_p1.json`, `lab/kit_test/themes/chemlab.css`, `projects/che-molarity/`, `library/backgrounds/photos/chemistry/molarity/`, plates `cl-lab-wall`, `card-chem-light` |

To rebuild one (the HeyGen clip is not in the repo; put it at `projects/<slug>/src/part1.mp4`):

```
.venv-tools/bin/python lab/kit_test/make_<id>_plans.py
.venv-tools/bin/python lab/kit_test/render_reel.py <slug> --wait
```

What a reel must be is in [`lab/kit_test/STANDARD.md`](../lab/kit_test/STANDARD.md); how one is made, step by step, is the `reel`
skill (`.claude/skills/reel/SKILL.md`).
