---
# ── Frontmatter (YAML) ─────────────────────────────────────────────
title: Gauss's Law
orientation: landscape          # landscape | portrait
theme: slate-grid               # midnight | charcoal | slate-grid | deep-space | blackboard | ivory | paper-grid
chroma: none                    # none | lower_third | bottom_half | left_half | right_half | full
speakers:
  narrator: { voice: Alice }    # any voice NAME (or voice_id) from your ElevenLabs library
  student:  { voice: Liam }     # (this account also has: Roger, Sarah, Laura, Charlie, George, River, Will, Matilda, ...)
# ───────────────────────────────────────────────────────────────────
---

[narrator] Gauss's law connects the electric field on a closed surface to the charge trapped inside it. Here is the integral form.
$$ \oint \vec{E} \cdot d\vec{A} = \frac{Q_{\text{enc}}}{\varepsilon_0} $$

[student] What does that circle on the integral sign mean?

[narrator] It means we integrate over a closed surface — a Gaussian surface — that fully encloses the charge. The left side is the electric flux through it.
$$ \Phi_E = \oint \vec{E} \cdot d\vec{A} $$

[narrator] The flux depends only on the enclosed charge and the permittivity of free space, epsilon-nought.
$$ \Phi_E = \frac{Q_{\text{enc}}}{\varepsilon_0} $$

[narrator] Let's apply it to a point charge. By symmetry we choose a sphere of radius r, where the field has constant magnitude and points radially outward.
%% show a sphere with radial field arrows if you extend this later
$$ \oint \vec{E} \cdot d\vec{A} = E \, (4 \pi r^2) $$

[narrator] Setting that equal to the enclosed charge over epsilon-nought and solving for E recovers Coulomb's field.
$$ E \, (4 \pi r^2) = \frac{q}{\varepsilon_0} \quad\Rightarrow\quad E = \frac{1}{4 \pi \varepsilon_0} \frac{q}{r^2} $$

[narrator] Finally, the differential form. Using the divergence theorem, Gauss's law becomes a statement about charge density at every point.
$$ \nabla \cdot \vec{E} = \frac{\rho}{\varepsilon_0} $$
