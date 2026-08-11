---
title: Derivative of x Squared from First Principles
orientation: landscape
theme: midnight
chroma: none
speakers:
  narrator: { voice: George }
---

[narrator]
Aaj hum ek simple sawaal se shuru karte hain: ek curve ka slope kisi ek point par kaise nikalein?
%% Fade in a dark grid, draw the parabola y = x squared in cyan, place a glowing dot on the curve.
$$ y = x^2 $$

[narrator]
Problem ye hai ki slope ke liye do points chahiye, lekin humein sirf ek hi point par slope chahiye.
%% Show a straight line through two points with rise-over-run triangle, then shrink to a single point and flash a question mark.
$$ \text{slope} = \frac{\text{rise}}{\text{run}} $$

[narrator]
Toh trick ye hai: pehle point x lo, aur uske thoda paas doosra point x plus h lo.
%% Mark point A at x and point B at x plus h on the parabola, label the small gap h in yellow.
$$ A = (x,\; x^2), \quad B = (x+h,\; (x+h)^2) $$

[narrator]
In dono points ko jodne wali line ko secant kehte hain, aur uska slope hum easily nikaal sakte hain.
%% Draw a magenta secant line through A and B, highlight the vertical and horizontal gaps.
$$ m = \frac{f(x+h) - f(x)}{h} $$

[narrator]
Ab function ki values daal dete hain: upar aayega x plus h ka square minus x square.
%% Substitute into the fraction, letters sliding into place, numerator highlighted in white.
$$ m = \frac{(x+h)^2 - x^2}{h} $$

[narrator]
Numerator ko expand karte hain: x square plus two x h plus h square, minus x square.
%% Expand the bracket term by term, each term popping in one at a time.
$$ m = \frac{x^2 + 2xh + h^2 - x^2}{h} $$

[narrator]
Dekho, x square aur minus x square cancel ho gaye, sirf do term bache.
%% Strike through both x squared terms with a red slash, then fade them out.
$$ m = \frac{2xh + h^2}{h} $$

[narrator]
Ab numerator se h common lo, aur denominator ke h ke saath cancel kar do.
%% Factor h out, show h over h cancelling with a satisfying pop.
$$ m = \frac{h(2x + h)}{h} = 2x + h $$

[narrator]
Yahan magic hai: jaise jaise h zero ke paas jaata hai, secant line tangent ban jaati hai.
%% Animate point B sliding toward A, the magenta secant rotating until it rests as a green tangent.
$$ \lim_{h \to 0} (2x + h) $$

[narrator]
Aur limit lene par h gayab ho jaata hai, toh humein milta hai two x.
%% Fade h to zero, leaving 2x glowing large in the centre of the frame.
$$ \frac{dy}{dx} = 2x $$

[narrator]
Check karte hain: x equal to three par slope hoga chhe, yaani curve wahan tez chadh raha hai.
%% Move the tangent point to x equals three, display slope value six beside a steep green tangent.
$$ \left. \frac{dy}{dx} \right|_{x=3} = 6 $$

[narrator]
Yahi first principles hai — har derivative formula isi ek limit se nikalta hai.
%% Show the general definition boxed in gold, with y = x squared and 2x below as a solved example.
$$ f'(x) = \lim_{h \to 0} \frac{f(x+h) - f(x)}{h} $$
