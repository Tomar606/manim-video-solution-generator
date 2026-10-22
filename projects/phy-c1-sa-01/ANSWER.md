# PHY-C1-SA-01 — the reference answer

From the sheet's Answer column, cross-checked against the Q/A image
(textbook scan, "प्रश्न 5 ... (म.प्र. 2022)").

## The question has THREE parts and the video must answer all three

1. **विद्युत् फ्लक्स क्या है ?**
   विद्युत् क्षेत्र में स्थित किसी क्षेत्रफल से अभिलम्बवत् गुजरने वाली क्षेत्र
   रेखाओं की संख्या को विद्युत् फ्लक्स कहते हैं। प्रतीक phi_E.

2. **कितने प्रकार का होता है ?** दो —
   - **धनात्मक**: क्षेत्र रेखाएँ पृष्ठ से बाहर की ओर जा रही हों
   - **ऋणात्मक**: क्षेत्र रेखाएँ पृष्ठ के अन्दर की ओर आ रही हों

3. **सिद्ध कीजिए** that a surface PARALLEL to the field carries zero flux:
   - if E makes an angle theta with the NORMAL to an area ds:
       phi_E = E . ds . cos(theta)
   - a surface parallel to the field means theta = 90 degrees
   - phi_E = E . ds . cos 90 = 0     (because cos 90 = 0)

## What that means for the screen

"सिद्ध कीजिए" sets the strategy: a derivation built step by step, not a list.
Every step above is a diagram or an equation:

  - field lines crossing a surface, and the count that defines flux
  - the same surface with lines going OUT (positive) and coming IN (negative)
  - the normal to the surface, and theta between E and that normal
  - the surface turned parallel: theta = 90, the lines now GRAZE it and cross
    nothing, and cos 90 collapses the formula to zero

The last one is the whole question: the picture has to show lines sliding past
a surface they never pierce, at the moment cos 90 = 0 appears.

## Devanagari and formulae do not mix

phi_E, theta, 90 degrees and the dot product go through MathTex; every Hindi
word goes through Text(). Never glue a Devanagari subscript onto a symbol.
