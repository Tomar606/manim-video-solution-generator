# Style corpus

What the presenter sounds like. Two inputs, both optional:

## `samples/`

Drop **real scripts you have already shipped and approved** here, as `.md` or
`.txt`. They can be full pipeline scripts (frontmatter is stripped automatically)
or just the spoken lines. These carry more weight than any written instruction —
the writer matches their rhythm, sentence length and Hindi/English balance.

Three to six varied samples work better than twenty similar ones. Include a short
video and a long one, an easy topic and a hard one.

## `variations.yaml`

The recurring lines — how a video opens, how it moves between steps, how the
answer lands, how it signs off — with every approved alternative. The writer
picks a different one each time, which is what stops a run of videos sounding
identical.

Add as many slots as you like; the names are just conventions.

## Checking it works

```bash
video style                 # what's loaded
video eval <project>        # score an existing script against it
```
