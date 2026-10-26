part1.mp4 is a splice of two HeyGen takes of the same script (user, 23 Oct 2026: "use motion_prompt for the
beginning since its clip is better, and when it ends use the other one"):
  motion_prompt.mp4  0.00 - 32.92 s   "MP Board ..." through "... तो Reel को पूरा देखना।"
  full_take.mp4     35.70 s - end     from the silence (-65 dB) before "तो सवाल है" to the end
Framing matches (centre x 321 vs 324 px in the crop, head top 34 vs 38 px), so the cut does not jump.
Rebuild: ffmpeg -i motion_prompt.mp4 -ss 35.70 -i full_take.mp4 -filter_complex "...concat=n=2:v=1:a=1..." part1.mp4
