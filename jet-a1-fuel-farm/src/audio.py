"""Sound: narration + synthesized paper rustles, pencil marks, soft taps and a low tonal bed,
with the bed and effects ducked under speech.  Writes build/mix.wav (48 kHz stereo)."""
import os, wave
import numpy as np
from scipy.signal import butter, sosfilt, resample_poly
from timeline import ST, END, VO, ROOT
from scenes import MOVES

SR = 48000
h, w, d, m, k, q, r = (ST[s] for s in ('hook', 'world', 'disruption', 'mechanism', 'discovery', 'consequence',
                                         'recap'))
rs = np.random.RandomState(21)
N = int((END + .5) * SR)


def bp(x, lo, hi, order=2):
    return sosfilt(butter(order, [lo, hi], 'bandpass', fs=SR, output='sos'), x)


def lp(x, f, order=2):
    return sosfilt(butter(order, f, 'lowpass', fs=SR, output='sos'), x)


def env_ad(n, a, dcy):
    t = np.arange(n) / SR
    return np.minimum(1, t / max(a, 1e-4)) * np.exp(-np.maximum(0, t - a) / dcy)


def rustle(dur):
    n = int(dur * SR)
    x = bp(rs.randn(n), 900, 7000)
    crackle = lp((rs.rand(n) < 220 / SR).astype(float) * rs.rand(n) * 40, 300)
    shape = np.sin(np.linspace(0, np.pi, n)) ** .7
    return x * (.35 + np.clip(crackle, 0, 3)) * shape * .10


def pencil(dur):
    n = int(dur * SR); t = np.arange(n) / SR
    strokes = np.abs(np.sin(2 * np.pi * (5.5 + 2 * rs.rand()) * t + rs.rand() * 6)) ** 1.5
    x = bp(rs.randn(n), 2200, 9000) * (.6 + .4 * bp(rs.randn(n), 20, 120) * 8)
    fade = np.minimum(1, np.minimum(t / .03, (dur - t) / .05))
    return x * strokes * fade * .055


def tap(f=520, g=1.0, dcy=.045):
    n = int(.25 * SR); t = np.arange(n) / SR
    body = np.sin(2 * np.pi * f * t) * env_ad(n, .002, dcy)
    body += .5 * np.sin(2 * np.pi * f * 2.3 * t) * env_ad(n, .001, dcy * .5)
    click = lp(rs.randn(n), 3000) * env_ad(n, .0005, .006)
    return (body * .5 + click * .35) * .32 * g


def drip():
    n = int(.12 * SR); t = np.arange(n) / SR
    f = 900 + 900 * t / .12
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * env_ad(n, .002, .025) * .07


EV = []          # (time, signal, pan)


def add(t, sig, pan=0.0):
    EV.append((t, sig, pan))


# --- hook
add(h - 0.6, rustle(.9), -.3)
add(h + 2.2, tap(300, 1.3, .07), .1)
add(h + 4.7, tap(640, .7), .3)
add(h + 6.5, tap(420, 1.0), .1)
# --- world
add(w - 1.2, pencil(1.4), -.2)
for i in range(6):
    add(w + .1 + i * .18, rustle(.35) * .8, -.5 + i * .2)
for i in range(3):
    add(w + 9.25 + i * .5, pencil(.32), -.4 + i * .4)
# --- disruption
add(d - 0.2, rustle(1.1), 0)
add(d + 2.6, pencil(.35), .1)
# --- mechanism
add(m + .6, rustle(.3) * .7, .3); add(m + 1.6, rustle(.3) * .7, .3)
add(m + 3.3, pencil(2.0), 0)
add(m + 6.5, pencil(.9), 0)
add(m + 8.4, tap(380), 0)
add(m + 10.1, rustle(.45), -.3)
add(m + 13.2, tap(560, .8), .2)
# --- discovery
add(k - .6, pencil(1.4), -.2)
add(k + 2.4, pencil(.6), 0)
for i in range(7):
    add(k + 5.0 + i * .28, tap(600 + i * 25, .6, .03), -.6 + i * .1)
add(k + 6.8, tap(340, .9), -.2)
for i in range(9):
    add(k + 7.0 + i * .13 + .3, drip(), -.3)
add(k + 8.1, rustle(.4) * .7, -.3)
add(k + 9.6, tap(700, .6), -.4); add(k + 10.3, tap(740, .6), -.4)
# --- consequence
add(q - .9, pencil(2.0) * .8, .3)
add(q - .8, rustle(1.4) * .6, .3)
add(q + 3.1, tap(660, .6), -.3); add(q + 4.0, tap(700, .6), .3)
for i in range(4):
    add(q + 4.7 + i * .17, tap(1300 + i * 120, .35, .02), .1)
for i in range(4):
    add(q + 6.6 + i * .35, tap(1200 + i * 90, .3, .02), .1)
add(q + 8.0, tap(330, 1.1, .06), .2)
# --- recap
add(q + 8.8, rustle(1.2) * .6, 0)
add(r + 0.0, rustle(.5), .3)
add(r + 1.2, tap(620, .6), .2)
add(r + 3.0, rustle(.5), -.4)
add(r + 3.4, pencil(.8), -.4)
add(r + 3.7, pencil(1.5), -.4)
add(r + 5.5, tap(300, 1.2, .07), -.4)
for i, tt in enumerate((r + 6.8, r + 7.6, r + 8.3)):
    add(tt, tap(500 + 80 * i, .8), -.3 + .3 * i)
add(r + 9.6, rustle(1.5), 0)
# bot hop landings
for t0, t1, a, b in MOVES:
    hops = max(1, round(abs(b - a) / 230))
    for j in range(1, hops + 1):
        add(t0 + (t1 - t0) * j / hops, tap(240, .45, .03), (a + (b - a) * j / hops - 960) / 1200)


# --- tonal bed: one soft chord per scene, cross-faded
CH = {'hook': [73.42, 110.0, 146.83, 220.0], 'world': [73.42, 110.0, 185.0, 277.18],
      'disruption': [61.74, 92.5, 146.83, 220.0], 'mechanism': [65.41, 98.0, 164.81, 246.94],
      'discovery': [73.42, 110.0, 185.0, 246.94], 'consequence': [61.74, 92.5, 123.47, 185.0],
      'recap': [73.42, 110.0, 146.83, 220.0, 277.18]}


def bed():
    t = np.arange(N) / SR
    out = np.zeros(N)
    names = list(CH)
    for i, nm in enumerate(names):
        t0 = ST[nm] - 1.2
        t1 = (ST[names[i + 1]] - 1.2) if i + 1 < len(names) else END + 1
        g = np.clip((t - t0) / 1.6, 0, 1) * np.clip((t1 + 1.6 - t) / 1.6, 0, 1)
        idx = g > 0
        tt = t[idx]
        s = np.zeros(idx.sum())
        for j, f in enumerate(CH[nm]):
            amp = .5 / (1 + j * .7)
            trem = 1 + .25 * np.sin(2 * np.pi * (.07 + .03 * j) * tt + j)
            s += amp * trem * (np.sin(2 * np.pi * f * tt) + .3 * np.sin(2 * np.pi * f * 1.003 * tt + 1))
        out[idx] += s * g[idx]
    air = lp(rs.randn(N), 400) * .4
    out = lp(out, 900) + air
    fade = np.clip(t / 1.5, 0, 1) * np.clip((END - t) / 1.5, 0, 1)
    return out * fade * .045


def load_vo():
    v = np.zeros(N)
    for t0, path in VO:
        wv = wave.open(path)
        a = np.frombuffer(wv.readframes(wv.getnframes()), np.int16).astype(float) / 32768
        a = resample_poly(a, 320, 147)
        i = int(t0 * SR)
        v[i:i + len(a)] += a[:N - i]
    return v


def main():
    vo = load_vo()
    vo = vo / (np.sqrt(np.mean(vo[np.abs(vo) > .01] ** 2)) + 1e-9) * 10 ** (-17 / 20)
    # speech envelope for ducking
    e = lp(np.abs(vo), 8, 1)
    e = np.clip(e / (np.percentile(e[e > 1e-3], 60) + 1e-9), 0, 1)
    # slower release
    duck = np.maximum.accumulate(e[::-1])[::-1] * 0 + e
    k_ = int(.35 * SR)
    duck = np.convolve(duck, np.ones(k_) / k_, 'same')
    duck = np.clip(duck * 1.6, 0, 1)
    L = np.zeros(N); R = np.zeros(N)
    b = bed() * (1 - .6 * duck)
    L += b; R += b
    fx = np.zeros((2, N))
    for t0, sig, pan in EV:
        i = int(t0 * SR)
        if i < 0 or i >= N:
            continue
        n = min(len(sig), N - i)
        p = np.clip(pan, -1, 1)
        fx[0, i:i + n] += sig[:n] * np.sqrt((1 - p) / 2) * 1.4
        fx[1, i:i + n] += sig[:n] * np.sqrt((1 + p) / 2) * 1.4
    fx *= (1 - .45 * duck)
    L += fx[0] + vo; R += fx[1] + vo
    pk = max(np.abs(L).max(), np.abs(R).max())
    g = min(1.0, 10 ** (-1 / 20) / pk)
    st = (np.stack([L, R], 1) * g * 32767).astype(np.int16)
    out = os.path.join(ROOT, 'build', 'mix.wav')
    wv = wave.open(out, 'wb'); wv.setnchannels(2); wv.setsampwidth(2); wv.setframerate(SR)
    wv.writeframes(st.tobytes()); wv.close()
    print('wrote', out, 'peak gain', round(g, 3), 'events', len(EV))


if __name__ == '__main__':
    main()
