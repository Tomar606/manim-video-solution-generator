# inbox

Source material for videos that start from a document rather than a topic
string — a faculty brief, a storyboard, a reference sheet.

Drop files here and point the pipeline at them:

```bash
video new "Sickle cell anaemia" --from inbox/sickle_cell.docx
```

Supported: `.docx`, `.md`, `.txt`. Reference images (frame examples, style
references) can go here too.

This folder is read-only as far as the pipeline is concerned — nothing here is
modified or deleted, and the parsed result lands in `projects/<slug>/`.
