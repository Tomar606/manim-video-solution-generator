**1. Factually wrong**

- **ΔT_b = T_b − T_b⁰ is written with the wrong symbols.** NCERT convention: **T_b⁰ = शुद्ध विलायक का क्वथनांक**, **T_b = विलयन का क्वथनांक**. The answer says "T_b का मान T_b⁰ से अधिक है" — that part is right — but many question banks flip the superscript. Keep it as **ΔT_b = T_b − T_b⁰**, and state explicitly that the ⁰ (or subscript-free) symbol belongs to the *pure solvent*.
- Heavy OCR corruption: क्वथनांक appears as "ववथनांक / ब्वथनांक / प्वथनांक / बव्रनांक", विलयन as "विसमयन", वाष्पदाब as "वाष्यदाब / याष्पदाब", घोलने as "षोलरने". All must be corrected — a video repeating these is unusable.

**2. Missing for full marks**

- The **relation ΔT_b = K_b · m** (m = मोललता), and that **K_b = मोलल उन्नयन स्थिरांक / क्वथनांक स्थिरांक**, unit **K kg mol⁻¹**.
- Statement that this is an **अणुसंख्य गुणधर्म** (colligative property) — depends on विलेय कणों की संख्या, not their nature.
- The molar-mass application: **M₂ = (1000 × K_b × w₂)/(ΔT_b × w₁)**.
- Explicit reason: अवाष्पशील विलेय surface पर जगह घेरकर विलायक अणुओं के वाष्पन को घटाता है → वाष्पदाब का अवनमन → उबलने के लिए अधिक ताप चाहिए.

**3. Frozen NCERT Hindi terminology**

क्वथनांक का उन्नयन · वाष्पदाब · वाष्पदाब का आपेक्षिक अवनमन · अवाष्पशील विलेय · शुद्ध विलायक · विलयन · वायुमण्डलीय दाब · मोललता · मोलल उन्नयन स्थिरांक · अणुसंख्य गुणधर्म · ताप

**4. Derivation order**

1. क्वथनांक की परिभाषा (वाष्पदाब = वायुमण्डलीय दाब, 1.013 bar).
2. अवाष्पशील विलेय → वाष्पदाब घटता है (राउल्ट का नियम).
3. इसलिए 1.013 bar तक पहुँचने के लिए अधिक ताप → T_b > T_b⁰.
4. ΔT_b = T_b − T_b⁰.
5. तनु विलयन में ΔT_b ∝ m ⇒ ΔT_b = K_b·m.
6. m = (w₂×1000)/(M₂×w₁) प्रतिस्थापित कर M₂ का सूत्र.

**Commonly reversed:** ΔT_b = T_b⁰ − T_b (wrong sign), and confusing K_b with K_f. Also: elevation depends on **मोललता**, not मोलरता.

**5. Animation**

Draw vapour-pressure vs temperature curves: **solvent curve above, solution curve below**, both rising, **never crossing**. Horizontal line at 1.013 bar; drop verticals to the x-axis marking **T_b⁰ (left)** and **T_b (right)**; brace between them = ΔT_b.

Avoid: solution curve above solvent; curves intersecting; T_b left of T_b⁰; straight lines instead of curves; ΔT_b marked on the pressure axis. Hindi labels via `Text()`, T_b/T_b⁰/ΔT_b via `MathTex()` — never mixed.