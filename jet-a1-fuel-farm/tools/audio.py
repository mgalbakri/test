"""Soundtrack: narration + low tonal bed + facility room tone + soft UI ticks and camera whooshes,
with everything except the voice ducked under speech.  Writes build/mix.wav (48 kHz stereo)."""
import json, os, wave
import numpy as np
from scipy.signal import butter, sosfilt, resample_poly

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TL = json.load(open(os.path.join(ROOT, 'build', 'timeline.json')))
S = {s['key']: s['start'] for s in TL['scenes']}
SEN = {s['key']: [x['t0'] for x in s['sentences']] for s in TL['scenes']}
END = TL['end']
SR = 48000
N = int((END + .3) * SR)
rs = np.random.RandomState(4)
t_all = np.arange(N) / SR


def bp(x, lo, hi, o=2): return sosfilt(butter(o, [lo, hi], 'bandpass', fs=SR, output='sos'), x)
def lp(x, f, o=2): return sosfilt(butter(o, f, 'lowpass', fs=SR, output='sos'), x)
def hp(x, f, o=2): return sosfilt(butter(o, f, 'highpass', fs=SR, output='sos'), x)


def tick(f=1800, g=1.0):
    n = int(.09 * SR); t = np.arange(n) / SR
    s = np.sin(2 * np.pi * f * t) * np.exp(-t / .012) + .4 * np.sin(2 * np.pi * f * 1.5 * t) * np.exp(-t / .006)
    return s * .07 * g


def thud(f=90, g=1.0):
    n = int(.5 * SR); t = np.arange(n) / SR
    s = np.sin(2 * np.pi * f * t * (1 - .25 * t)) * np.exp(-t / .12)
    return s * .22 * g


def whoosh(dur, g=1.0):
    n = int(dur * SR); t = np.arange(n) / SR
    x = rs.randn(n)
    env = np.sin(np.pi * t / dur) ** 2
    # sweep a band-pass upward by crossfading two filtered layers
    lo, hi = bp(x, 150, 900), bp(x, 600, 3000)
    k = t / dur
    return (lo * (1 - k) + hi * k * .6) * env * .05 * g


EV = []
def add(t, sig, pan=0.0): EV.append((t, sig, pan))


# camera moves
for a, b in [(S['receipt'] - 1.8, S['receipt'] + 1.6), (S['storage'] - .6, S['storage'] + 2.2),
             (S['release'] - .3, S['release'] + 2.6), (SEN['filtration'][2] + .2, SEN['filtration'][2] + 2.0),
             (S['delivery'] - .2, SEN['delivery'][1] + .8), (S['control'] - .4, SEN['control'][1] - .6)]:
    add(a, whoosh(b - a + .6), 0)
# callouts / panels (times mirror web/scene.js)
r, s, rl, f, d, c = SEN['receipt'], SEN['storage'], SEN['release'], SEN['filtration'], SEN['delivery'], SEN['control']
callouts = [r[1] + .2, r[1] + .8, r[2] + .1, r[2] + 1.5,
            s[1] + .1, s[1] + 1.0, s[2] + .1, s[2] + .8, s[2] + 3.6,
            S['release'] + .5, rl[1] - .2,
            f[1] + .1, f[1] + .8, f[2] + 1.6, f[2] + 2.4, f[2] + 3.2, f[2] + 3.9,
            d[1] + .3, d[1] + 2.4, d[1] + 3.0, d[1] + 4.0, S['control'] + .3]
for i, t in enumerate(callouts):
    add(t, tick(1500 + (i % 3) * 200, .9), (-.3, 0, .3)[i % 3])
for i in range(4):
    add(rl[1] + .6 + i * .55, tick(2400, .6), .3)
for i in range(5):
    add(S['control'] + .9 + i * .7, tick(2400, .6), -.3)
add(rl[1] + 3.0, thud(80, 1.0), .3)                    # release stamp
for i in range(5):
    add(c[1] + .3 + i * .55, tick(1100 + i * 110, 1.0), -.6 + i * .3)  # barrier pins
add(c[1] + 3.6, thud(65, .8), 0)


def bed():
    # slow minor-ish pad, one chord per section
    chords = {'overview': [55, 82.4, 130.8, 164.8], 'receipt': [55, 82.4, 110, 164.8], 'storage': [49, 73.4, 116.5, 146.8],
              'release': [55, 82.4, 130.8, 164.8], 'filtration': [43.7, 65.4, 110, 130.8], 'delivery': [49, 73.4, 98, 146.8],
              'control': [55, 82.4, 110, 138.6, 164.8]}
    out = np.zeros(N); keys = list(chords)
    for i, k in enumerate(keys):
        t0 = S[k] - 1.0; t1 = S[keys[i + 1]] - 1.0 if i + 1 < len(keys) else END + 1
        g = np.clip((t_all - t0) / 2.0, 0, 1) * np.clip((t1 + 2.0 - t_all) / 2.0, 0, 1)
        idx = g > 0; tt = t_all[idx]; sig = np.zeros(idx.sum())
        for j, fr in enumerate(chords[k]):
            amp = .55 / (1 + j * .6)
            sig += amp * (np.sin(2 * np.pi * fr * tt) + .25 * np.sin(2 * np.pi * fr * 2.003 * tt + j)) * (1 + .2 * np.sin(2 * np.pi * .05 * tt + j))
        out[idx] += sig * g[idx]
    out = lp(out, 700)
    room = lp(hp(rs.randn(N), 60), 380) * .35                       # facility room tone
    hum = .12 * np.sin(2 * np.pi * 50 * t_all) * np.clip((t_all - (f[1] + 1.4)) / 1.5, 0, 1) * np.clip((S['delivery'] + 2 - t_all) / 1.5, 0, 1)
    fade = np.clip(t_all / 2.0, 0, 1) * np.clip((END - t_all) / 1.5, 0, 1)
    return (out + room + hum) * fade * .05


def voice():
    v = np.zeros(N)
    for item in TL['vo']:
        w = wave.open(os.path.join(ROOT, item['file']))
        a = np.frombuffer(w.readframes(w.getnframes()), np.int16).astype(float) / 32768
        a = resample_poly(a, 320, 147) if w.getframerate() == 22050 else a
        i = int(item['t'] * SR); v[i:i + len(a)] += a[:N - i]
    # gentle presence + de-boom for a broadcast feel
    v = hp(v, 80) + .15 * bp(v, 2500, 5000)
    return v / (np.sqrt(np.mean(v[np.abs(v) > .01] ** 2)) + 1e-9) * 10 ** (-17 / 20)


def main():
    vo = voice()
    e = lp(np.abs(vo), 6, 1); e = np.clip(e / (np.percentile(e[e > 1e-3], 60) + 1e-9), 0, 1)
    k = int(.4 * SR); duck = np.clip(np.convolve(e, np.ones(k) / k, 'same') * 1.6, 0, 1)
    L = np.zeros(N); R = np.zeros(N)
    b = bed() * (1 - .55 * duck); L += b; R += b
    for t, sig, pan in EV:
        i = int(t * SR)
        if 0 <= i < N:
            n = min(len(sig), N - i); p = np.clip(pan, -1, 1)
            L[i:i + n] += sig[:n] * np.sqrt((1 - p) / 2) * 1.4 * (1 - .35 * duck[i:i + n])
            R[i:i + n] += sig[:n] * np.sqrt((1 + p) / 2) * 1.4 * (1 - .35 * duck[i:i + n])
    L += vo; R += vo
    g = min(1.0, 10 ** (-1 / 20) / max(np.abs(L).max(), np.abs(R).max()))
    st = (np.stack([L, R], 1) * g * 32767).astype(np.int16)
    out = os.path.join(ROOT, 'build', 'mix.wav')
    w = wave.open(out, 'wb'); w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes(st.tobytes()); w.close()
    print('wrote', out, 'events', len(EV))


if __name__ == '__main__':
    main()
