part1.mp4 is a splice of two HeyGen takes of the same script (user, 23 Oct 2026: "use motion_prompt for the
beginning since its clip is better, and when it ends use the other one"):
  motion_prompt.mp4  0.00 - 32.92 s   "MP Board ..." through "... तो Reel को पूरा देखना।"
  full_take.mp4     35.70 s - end     from the silence (-65 dB) before "तो सवाल है" to the end
Rebuild: ffmpeg -i motion_prompt.mp4 -ss 35.70 -i full_take.mp4 -filter_complex "...concat=n=2:v=1:a=1..." part1.mp4

v2 (23 Oct 2026): both takes re-rendered with the t-shirt logo removed ("logo removed avar 4" for the
opening, because the main take's logo distorts there; "physics_new_final" for the rest).  Their audio is
bit-identical to v1 (and so are the srts), so the cut, words_part1.json, lines_part1.json and every cue
are unchanged.  The head sits ~65 px further right after the cut; the cut lands on the beat change to the
question sheet, so it reads as a scene cut.  v1 sources are in src/v1/.
