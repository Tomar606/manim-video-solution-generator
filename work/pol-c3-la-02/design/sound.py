"""The sound palette of POL-C3-LA-02, "दो स्याही": a printed poster on cream
paper. Paper and print-shop sounds, quiet and dry; nothing musical, nothing with
a pitch on top of the voice.

This file is DATA FOR tools/reel/audio.py, which does the levelling, the ducking
and the 1-4 kHz check against the voice. numpy only; nothing here reads a file,
runs a process or knows what a part is.

    VOICES[kind](dur, rng, sr) -> mono (n,) or stereo (n, 2) float array, any level
        dur   the cue's own "dur" in seconds, or None when the cue has none
        rng   a numpy Generator seeded by the engine from the cue: same cue, same sound
    BED(t0, dur, sr) -> stereo (n, 2): the bed for ABSOLUTE seconds [t0, t0+dur)
        on one clock that runs through the whole video, so part 2 picks the room
        up at the sample part 1 left it. Every phase and every noise block is
        fixed by that clock; it may be asked for in pieces and the pieces butt.
    LEVELS  where each of them sits, in dB against the narration's loudness.

Where each sound keeps out of the voice's way: the weight of every effect is
either under 1 kHz (thumps, the knock of a pin) or above 4 kHz (the air of a
sheet, the bite of graphite), with only as much left in 1-4 kHz as it takes to
still read as paper. The engine measures what is left against the syllable it
lands on and turns the cue down if that is not enough.

WHEN A CUE'S `t` IS (design/kit.mjs writes them): the moment the thing starts to
move, and the sound starts there too, with two exceptions that follow the kit's
own animation:
  stamp  the kit's stamp is still in the air at t -- 'slam' lands 0.14 s later,
         'press' settles over 0.18 s -- so the thud comes 0.10 s after t
         (LEVELS["offset_s"]). An ear forgives a sound that is a frame late far
         more than one that is a frame early.
  drop   the kit puts the cue at 80 % of the fall (the fall eases in, so that is
         where it gets fast) with no dur. The whoosh starts there and the thud
         lands 0.22 s later, which is the end of a fall of about a second.
         With a `dur`, the whoosh lasts dur and the thud lands at t + dur.
`slide`, `scratch`, `flip` last `dur` when it is given.
"""
import numpy as np

SEED = 30502


# ----------------------------------------------------------------- helpers --
def _fast_len(n):
    """Smallest 2^a 3^b 5^c >= n."""
    best, p5 = None, 1
    while p5 < 2 * n:
        p35 = p5
        while p35 < 2 * n:
            m = p35
            while m < n:
                m *= 2
            best = m if best is None or m < best else best
            p35 *= 3
        p5 *= 5
    return best


def _lp(fc, order=2):
    return lambda f: 1 / np.sqrt(1 + (f / fc) ** (2 * order))


def _hp(fc, order=2):
    return lambda f: 1 / np.sqrt(1 + (fc / np.maximum(f, 1e-3)) ** (2 * order))


def _bp(lo, hi, order=2):
    return lambda f: _lp(hi, order)(f) * _hp(lo, order)(f)


def _bump(fc, width_oct):
    """A log-gaussian resonance centred on fc."""
    return lambda f: np.exp(-0.5 * (np.log2(np.maximum(f, 20) / fc) / width_oct) ** 2)


def _filt(x, sr, gain_fn):
    """Zero-phase magnitude filter by FFT; gain_fn(hz) -> linear gain."""
    n = _fast_len(len(x) + 4096)
    return np.fft.irfft(np.fft.rfft(x, n=n) * gain_fn(np.fft.rfftfreq(n, 1 / sr)), n=n)[:len(x)]


def _noise(rng, n, sr, gain_fn):
    """Shaped noise, peak 1."""
    y = _filt(rng.standard_normal(n), sr, gain_fn)
    return y / (np.abs(y).max() + 1e-12)


def _rms(x):
    return float(np.sqrt(np.mean(np.square(x)))) + 1e-12


def _swept(rng, n, sr, f_a, f_b, width_oct, floor_hz, ceil_hz=11000.0):
    """Noise through a log-gaussian band whose centre glides f_a -> f_b."""
    N, H = 1024, 128
    win = np.hanning(N)
    f = np.fft.rfftfreq(N, 1 / sr)
    lf = np.log2(np.maximum(f, 20))
    edge = _hp(floor_hz, 2)(f) * _lp(ceil_hz, 3)(f)
    src = rng.standard_normal(n + N)
    out, norm = np.zeros(n + N), np.zeros(n + N)
    for s in range(0, n, H):
        fc = f_a * (f_b / f_a) ** (s / max(n, 1))
        g = np.exp(-0.5 * ((lf - np.log2(fc)) / width_oct) ** 2) * edge
        out[s:s + N] += np.fft.irfft(np.fft.rfft(src[s:s + N] * win) * g, n=N) * win
        norm[s:s + N] += win * win
    y = (out / np.maximum(norm, 1e-3))[:n]
    return y / (np.abs(y).max() + 1e-12)


def _t(dur, sr):
    return np.arange(int(round(dur * sr))) / sr


def _attack(t, a):
    return np.clip(t / a, 0.0, 1.0)


def _glide_phase(t, f_end, f_start, tau):
    """Phase of a tone falling f_start -> f_end as f_end + (f_start-f_end)exp(-t/tau)."""
    return 2 * np.pi * (f_end * t + (f_start - f_end) * tau * (1 - np.exp(-t / tau)))


def _thud(rng, t, sr, f_end, f_start, decay, drive=2.0, knock=1.5):
    """A dull landing: a falling low tone pushed into soft saturation, low body
    noise, and the KNOCK of the table at 260-800 Hz. The knock carries as much
    as the low tone on purpose: a phone speaker has nothing under 300 Hz, so a
    thud made of its low tone alone is silent on the thing this is watched on.
    No click: 3 ms attack."""
    low = np.tanh(drive * np.sin(_glide_phase(t, f_end, f_start, 0.025))) / np.tanh(drive)
    low *= np.exp(-t / decay)
    body = _noise(rng, len(t), sr, _lp(240, 2)) * np.exp(-t / (0.6 * decay))
    kn = _noise(rng, len(t), sr, lambda f: _hp(260, 2)(f) * _lp(800, 4)(f)) * np.exp(-t / (0.45 * decay))
    return (low + 0.35 * body + knock * kn) * _attack(t, 0.003)


def _pan(mono, p):
    a = (np.clip(p, -1, 1) + 1) * np.pi / 4
    return np.stack([mono * np.cos(a), mono * np.sin(a)], axis=1)


# ------------------------------------------------------------ the effects ---
def slide(dur, rng, sr):
    """A sheet of paper sliding in: a soft swish, its air rising as the sheet
    comes, a little dull body under it, the fibres giving it a faint flutter.
    Drifts left to right, the way the sheet is dealt."""
    d = float(np.clip(dur if dur else 0.25, 0.18, 0.60))
    n = int(d * sr)
    u = np.linspace(0, 1, n)
    env = np.sin(np.pi * u ** 0.7) ** 1.6
    air = _swept(rng, n, sr, 3600, 6400, 0.55, 1500)
    side = _swept(rng, n, sr, 3600, 6400, 0.55, 1500)
    body = _swept(rng, n, sr, 420, 700, 0.5, 150)
    t = u * d
    flutter = 1 + 0.2 * np.sin(2 * np.pi * 47 * t + 2 * np.sin(2 * np.pi * 7 * t) + rng.uniform(0, 6.28))
    mid = (air * flutter + 0.3 * body) * env
    out = _pan(mid, 0.0)
    drift = -0.3 + 0.6 * u
    out[:, 0] *= 1 - 0.35 * drift
    out[:, 1] *= 1 + 0.35 * drift
    s = 0.35 * side * env
    out[:, 0] += s
    out[:, 1] -= s
    return out


def stamp(dur, rng, sr):
    """A rubber stamp coming down on the page: a low thump, the knock of the
    table under it, and a short papery slap. Dry; gone in a fifth of a second."""
    t = _t(0.22, sr)
    y = _thud(rng, t, sr, 68, 150, 0.05, drive=1.8, knock=3.4)
    slap = _noise(rng, len(t), sr, _bp(1300, 5500, 2)) * np.exp(-t / 0.011) * _attack(t, 0.001)
    return y + 0.5 * slap


def scratch(dur, rng, sr):
    """Pencil on paper for as long as the line is drawn. Graphite, not hiss: the
    noise is band-shaped with the bite of the point around 5 kHz and the hollow
    of the desk around 700 Hz, and it comes in GRAINS -- the point catching the
    tooth of the paper several hundred times a second -- with the pressure of the
    hand wandering a little under it."""
    d = max(float(dur if dur else 0.6), 0.12)
    n = int(d * sr)
    t = np.arange(n) / sr

    def shape(f):
        return (_hp(1100, 2)(f) * _lp(8500, 2)(f) * (0.35 + 1.6 * _bump(5200, 0.35)(f) + 0.5 * _bump(2700, 0.3)(f))
                + 0.2 * _bump(700, 0.3)(f))

    base = _noise(rng, n, sr, shape)
    # grains: a Poisson train of 2-5 ms catches of uneven weight
    hits = np.zeros(n)
    k = rng.poisson(600 * d)
    if k:
        np.add.at(hits, rng.integers(0, n, k), rng.lognormal(0.0, 0.55, k))
    kern = np.hanning(int(0.0035 * sr))
    grain = np.convolve(hits, kern, mode="same")
    grain /= grain.mean() + 1e-9
    # the hand: a slow uneven pressure, never a beat
    f1, f2 = rng.uniform(2.3, 3.4), rng.uniform(5.2, 7.4)
    hand = (1 + 0.16 * np.sin(2 * np.pi * f1 * t + rng.uniform(0, 6.28) + 0.9 * np.sin(2 * np.pi * 0.7 * t))
            + 0.09 * np.sin(2 * np.pi * f2 * t + rng.uniform(0, 6.28)))
    env = _attack(t, 0.025) * np.clip((d - t) / 0.07, 0, 1)
    return base * (0.4 + 0.6 * grain) * hand * env


def tick(dur, rng, sr):
    """A pencil tick, or a pin going into the board: a small wooden knock under
    1.4 kHz with a hair of click above the voice. Every one a shade different."""
    t = _t(0.07, sr)
    k = 2 ** (rng.uniform(-0.6, 0.6) / 12)
    knock = (np.sin(2 * np.pi * 820 * k * t) * np.exp(-t / 0.008)
             + 0.5 * np.sin(2 * np.pi * 1340 * k * t + 0.6) * np.exp(-t / 0.005))
    click = _noise(rng, len(t), sr, _bp(4300, 9000, 2)) * np.exp(-t / 0.0025)
    return (knock + 0.7 * click) * _attack(t, 0.0005)


def flip(dur, rng, sr):
    """A card turning over: two quick paper flutters -- up and over -- and the
    soft pat of it lying flat."""
    d = float(np.clip(dur if dur else 0.30, 0.24, 0.50))
    n = int(d * sr)
    out = np.zeros(n)
    t = np.arange(n) / sr
    for at, ln, fa, fb, amp in ((0.0, 0.37 * d, 2800, 6500, 0.85), (0.47 * d, 0.40 * d, 6500, 3000, 1.0)):
        m = int(ln * sr)
        a = int(at * sr)
        u = np.linspace(0, 1, m)
        tt = u * ln
        y = _swept(rng, m, sr, fa, fb, 0.5, 900) * np.sin(np.pi * u) ** 1.5
        y *= 0.55 + 0.45 * np.sin(2 * np.pi * 62 * tt + rng.uniform(0, 6.28))
        out[a:a + m] += amp * y[:n - a]
    ts = np.maximum(t - 0.86 * d, 0)
    pat = _noise(rng, n, sr, _bp(600, 3000, 2)) * np.exp(-ts / 0.010) * (t >= 0.86 * d)
    return out + 0.4 * pat


def drop(dur, rng, sr):
    """Something heavy falling and landing: a short whoosh that falls in pitch
    and grows as it comes, cut off by a dull thud. `dur` is the fall."""
    fall = float(np.clip(dur if dur else 0.22, 0.15, 0.80))
    nf = int(fall * sr)
    t = _t(fall + 0.42, sr)
    u = np.linspace(0, 1, nf)
    wh = _swept(rng, nf, sr, 1500, 260, 0.6, 120, 5000.0) * u ** 1.8
    k = int(0.008 * sr)
    wh[-k:] *= np.linspace(1, 0, k)
    out = np.zeros(len(t))
    out[:nf] = 0.7 * wh
    tl = t[nf:] - t[nf]
    land = _thud(rng, tl, sr, 46, 105, 0.11, drive=2.2, knock=2.8)
    rattle = _noise(rng, len(tl), sr, _bp(1500, 4500, 2)) * np.exp(-tl / 0.012)
    out[nf:] += land + 0.12 * rattle
    return out


VOICES = {"slide": slide, "stamp": stamp, "scratch": scratch, "tick": tick, "flip": flip, "drop": drop}


# --------------------------------------------------------------- the bed ----
# A quiet print room. Two things, neither of them music:
#   the ROOM  air moving in a closed room -- noise with all its weight between
#             120 and 600 Hz (22 dB down by 1.5 kHz, 44 dB down by 3 kHz), a
#             different draw in each ear, each ear drifting a decibel on its own;
#   the HUM   one low machine note at 92 Hz with its octave and twelfth far
#             quieter above it and a sub below. One pitch, held: no interval, so
#             nothing to hear as a chord. Two copies 0.07 Hz apart, one in each
#             ear, turn slowly against each other -- that is all the movement.
# Over both, one breath every 34 s or so (it wanders), 3 dB deep.
HUM_HZ = 92.0
#        harmonic  level   wander period s, phase
HUM = [(0.5, 0.45, 53.0, 1.1),
       (1.0, 1.00, 41.0, 0.2),
       (2.0, 0.30, 29.0, 2.6),
       (3.0, 0.14, 37.0, 4.4)]
HUM_REL_DB = -5.0          # the hum's RMS against the room's
SWELL_S = 34.0


def _room_shape(f):
    return _hp(120, 2)(f) * _lp(520, 2)(f) * _lp(1400, 2)(f)


def _room(n0, n, sr, ch):
    """Room noise for absolute samples [n0, n0+n). Drawn one second at a time
    from a seed that names the second, filtered with a second of guard each side,
    so it depends on absolute time alone. Unit RMS by construction."""
    guard = sr
    a, b = n0 - guard, n0 + n + guard
    b0, b1 = a // sr, -(-b // sr)
    x = np.concatenate([np.random.default_rng([SEED, 7, ch, blk + 100000]).standard_normal(sr)
                        for blk in range(b0, b1)])
    x = x[a - b0 * sr: a - b0 * sr + (b - a)]
    m = _fast_len(len(x) + 4096)
    g = _room_shape(np.fft.rfftfreq(m, 1 / sr))
    y = np.fft.irfft(np.fft.rfft(x, n=m) * g, n=m)[guard: guard + n]
    return y / np.sqrt((2 * np.sum(g * g) - g[0] ** 2) / m)


def BED(t0, dur, sr):
    n0, n = int(round(t0 * sr)), int(round(dur * sr))
    t = (n0 + np.arange(n)) / sr
    out = np.empty((n, 2))
    common = _room(n0, n, sr, 2)
    for ch in range(2):
        own = _room(n0, n, sr, ch)
        drift = 1 + 0.07 * np.sin(2 * np.pi * t / 13.7 + 2.1 * ch) + 0.05 * np.sin(2 * np.pi * t / 23.1 + 0.8 + ch)
        out[:, ch] = (0.75 * common + 0.66 * own) * drift
    hum = np.zeros((n, 2))
    norm = np.sqrt(sum(a * a for _, a, _, _ in HUM) / 2)
    for h, a, per, ph in HUM:
        amp = a * (1 + 0.22 * np.sin(2 * np.pi * t / per + ph))
        for ch, det in ((0, 1 - 0.00038), (1, 1 + 0.00038)):
            hum[:, ch] += amp * np.sin(2 * np.pi * HUM_HZ * h * det * t + 1.7 * h + 0.9 * ch)
    hum_breath = 10 ** ((-2.0 + 4.0 * (0.5 - 0.5 * np.cos(2 * np.pi * t / 47.0 + 1.0))) / 20)
    out += (10 ** (HUM_REL_DB / 20) / norm) * hum * hum_breath[:, None]
    breath = 0.5 - 0.5 * np.cos(2 * np.pi * t / SWELL_S + 0.7 * np.sin(2 * np.pi * t / 101.0))
    return (out * (10 ** ((-3.0 + 3.0 * breath) / 20))[:, None]).astype(np.float32)


# -------------------------------------------------------------- levels ------
LEVELS = {
    # the bed's integrated loudness against PART 1's narration, before ducking
    "bed_rel_db": -25.0,
    "duck_db": 3.0,                  # how far the bed drops while he speaks
    "bed_fade_in_s": 1.0,            # part 1; later parts come in over 0.4 s
    "bed_fade_out_s": 0.4,
    # each effect's loudest 400 ms against the narration's integrated loudness
    "sfx_rel_db": {"slide": -24.0, "stamp": -19.0, "scratch": -28.0, "tick": -28.0, "flip": -24.0, "drop": -18.0},
    # each cue is slid LATER by up to max_shift_s, then turned down by up to
    # max_trim_db, until it sits target_margin_db under the voice in 1-4 kHz on
    # its own and sum_margin_db under it together with the bed and the effects
    # already sounding there
    "fit": {
        "target_margin_db": 6.0,
        "sum_margin_db": 4.5,
        "max_trim_db": 12.0,
        "max_shift_s": {"slide": 0.06, "stamp": 0.04, "scratch": 0.0, "tick": 0.08, "flip": 0.06, "drop": 0.04},
    },
    # seconds from a cue's t to the start of its sound (see "WHEN A CUE'S `t` IS")
    "offset_s": {"stamp": 0.10},
}
