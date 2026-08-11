---
title: Gauss's Law Derivation
orientation: landscape
theme: slate-grid            # blueprint-style: dark navy + faint engineering grid
chroma: none
speakers:
  narrator: { voice: George }   # Hinglish via eleven_multilingual_v2; swap voice freely
---

[narrator]
Ab derivation dekhte hain.

%% Fade in the blueprint-style mathematical background with a subtle engineering grid. The title "Gauss's Law Derivation" appears briefly before fading away.
[narrator]
Point charge ke liye Electric Field hume Coulomb's Law se milti hai.

$$
\vec{E}=\frac{1}{4\pi\varepsilon_0}\frac{Q}{r^2}\hat r
$$

%% The equation should build from left to right. Highlight Q in yellow, then r², then epsilon-nought.
[narrator]
Ab Electric Flux ki definition use karte hain.

$$
\Phi=\oint_S \vec E\cdot d\vec A
$$

%% Morph smoothly from the previous equation. Keep the previous equation faintly visible for a second before replacing it.
[narrator]
Ab Electric Field ki value is equation mein substitute karte hain.

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
Charge Q har jagah same hai.

Aur radius r bhi poori Gaussian Surface par constant rehta hai.

Isliye in dono ko integral ke bahar le sakte hain.

$$
\Phi
=
\frac{Q}{4\pi\varepsilon_0r^2}
\oint_S
\hat r\cdot d\vec A
$$

%% Highlight Q and r² in yellow while moving them outside the integral. The integral sign remains fixed.
[narrator]
Ab dhyaan dijiye.

Area Vector hamesha bahar ki taraf hota hai.

Aur sphere ke liye Area Vector aur Radius Vector dono ek hi direction mein hote hain.

Isliye inka dot product sirf dA ban jaata hai.

$$
\hat r\cdot d\vec A=dA
$$

%% Show the dot product collapsing into dA. Animate the vector arrow fading while dA enlarges.
[narrator]
Ab equation aur simple ho jaati hai.

$$
\Phi
=
\frac{Q}{4\pi\varepsilon_0r^2}
\oint_S dA
$$

%% Smoothly substitute the previous simplification into the main equation.
[narrator]
Aur surface ke har chhote area ko jodne par hume poori sphere ka surface area milta hai.

$$
\oint_S dA=4\pi r^2
$$

%% Highlight the integral in blue and transform it into 4πr² with a gentle morph instead of a cut.
[narrator]
Ab is value ko substitute karte hain.

$$
\Phi
=
\frac{Q}{4\pi\varepsilon_0r^2}
\left(4\pi r^2\right)
$$

%% Animate the value sliding into the equation from below.
[narrator]
Ab upar aur neeche wala chaar pi r square cancel ho jaata hai.

$$
\Phi
=
\frac{Q}{\varepsilon_0}
$$

%% Instead of drawing cancellation marks, fade the matching 4π and r² terms simultaneously until only Q over epsilon-nought remains.
[narrator]
Aur isi ko hum Gauss's Law kehte hain.

$$
\boxed{
\oint_S
\vec E\cdot d\vec A
=
\frac{Q_{\text{enclosed}}}{\varepsilon_0}
}
$$

%% Hold the final equation in the center for two seconds. Everything else fades away. Give the equation a subtle white glow with the current term highlighted in yellow before the glow fades.
