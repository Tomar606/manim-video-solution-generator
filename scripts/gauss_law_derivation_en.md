---
title: Gauss's Law Derivation
orientation: portrait
theme: slate-grid
chroma: none
speakers:
  narrator: { voice: Alice }   # premade voice — works on the free ElevenLabs plan
---

[narrator]
Let's walk through the derivation of Gauss's law.

%% Fade in the blueprint-style mathematical background with a subtle engineering grid. The title "Gauss's Law Derivation" appears briefly before fading away.
[narrator]
For a point charge, the electric field comes from Coulomb's law.

$$
\vec{E}=\frac{1}{4\pi\varepsilon_0}\frac{Q}{r^2}\hat r
$$

%% The equation should build from left to right. Highlight Q in yellow, then r squared, then epsilon-nought.
[narrator]
Now we bring in the definition of electric flux.

$$
\Phi=\oint_S \vec E\cdot d\vec A
$$

%% Morph smoothly from the previous equation. Keep the previous equation faintly visible for a second before replacing it.
[narrator]
We substitute the electric field into this equation.

$$
\Phi
=
\oint_S
\left(
\frac{Q}{4\pi\varepsilon_0r^2}
\hat r
\right)
\cdot d\vec A
$$

%% Animate the Coulomb's Law expression moving directly into the flux equation instead of simply replacing it.
[narrator]
The charge Q is the same everywhere, and the radius r stays constant over the entire Gaussian surface. So we can pull both of them outside the integral.

$$
\Phi
=
\frac{Q}{4\pi\varepsilon_0r^2}
\oint_S
\hat r\cdot d\vec A
$$

%% Highlight Q and r squared in yellow while moving them outside the integral. The integral sign remains fixed.
[narrator]
Now notice. The area vector always points outward, and on a sphere the area vector and the radial vector point in the same direction. So their dot product is simply dA.

$$
\hat r\cdot d\vec A=dA
$$

%% Show the dot product collapsing into dA. Animate the vector arrow fading while dA enlarges.
[narrator]
Now the equation becomes even simpler.

$$
\Phi
=
\frac{Q}{4\pi\varepsilon_0r^2}
\oint_S dA
$$

%% Smoothly substitute the previous simplification into the main equation.
[narrator]
And adding up every small patch of area over the surface gives the total surface area of the sphere.

$$
\oint_S dA=4\pi r^2
$$

%% Highlight the integral in blue and transform it into 4 pi r squared with a gentle morph instead of a cut.
[narrator]
Now we substitute this value in.

$$
\Phi
=
\frac{Q}{4\pi\varepsilon_0r^2}
\left(4\pi r^2\right)
$$

%% Animate the value sliding into the equation from below.
[narrator]
The four-pi-r-squared on the top and bottom cancels out.

$$
\Phi
=
\frac{Q}{\varepsilon_0}
$$

%% Instead of drawing cancellation marks, fade the matching 4 pi and r squared terms simultaneously until only Q over epsilon-nought remains.
[narrator]
And this is exactly what we call Gauss's law.

$$
\boxed{
\oint_S
\vec E\cdot d\vec A
=
\frac{Q_{\text{enclosed}}}{\varepsilon_0}
}
$$

%% Hold the final equation in the center for two seconds. Everything else fades away. Give the equation a subtle white glow with the current term highlighted in yellow before the glow fades.
