---
title: Deriving the Quadratic Formula
orientation: landscape          # landscape | portrait
theme: midnight                 # named theme (see src/themes.py) or inline mapping
chroma: none                    # none | lower_third | bottom_half | ...
speakers:
  narrator: { voice: Alice }   # "Alice - Clear, Engaging Educator"
  student:  { voice: Liam }    # "Liam - Energetic, Social Media Creator"
---

[narrator] Let's derive the quadratic formula from scratch. We begin with the general quadratic equation.
$$ a x^2 + b x + c = 0 $$

[student] Where do we even start with something this general?

[narrator] First, divide every term by a. This normalises the leading coefficient to one.
$$ x^2 + \frac{b}{a} x + \frac{c}{a} = 0 $$

[narrator] Now move the constant term to the right-hand side.
$$ x^2 + \frac{b}{a} x = -\frac{c}{a} $$

[narrator] Here is the key idea: we complete the square by adding the square of half the x-coefficient to both sides.
%% highlight the added term on both sides
$$ x^2 + \frac{b}{a} x + \left(\frac{b}{2a}\right)^2 = \left(\frac{b}{2a}\right)^2 - \frac{c}{a} $$

[narrator] The left-hand side is now a perfect square, and we combine the fractions on the right.
$$ \left(x + \frac{b}{2a}\right)^2 = \frac{b^2 - 4ac}{4a^2} $$

[student] So now we just take the square root of both sides?

[narrator] Exactly. Taking the square root introduces a plus-or-minus.
$$ x + \frac{b}{2a} = \pm \frac{\sqrt{b^2 - 4ac}}{2a} $$

[narrator] Finally, isolate x, and we arrive at the quadratic formula.
$$ x = \frac{-b \pm \sqrt{b^2 - 4ac}}{2a} $$
