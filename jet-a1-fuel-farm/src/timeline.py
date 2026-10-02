"""Timing derived from the synthesized narration: scene starts, sentence spans, caption chunks."""
import json, os, wave
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(HERE, '..')
NARR = json.load(open(os.path.join(ROOT, 'narration.json')))
VO_DIR = os.path.join(ROOT, 'build', 'vo')
LEAD, GAP, TAIL = 1.0, 0.8, 3.3
SCENES = [k for k, _ in NARR]


def _load(i, k):
    w = wave.open(os.path.join(VO_DIR, f'{i}_{k}.wav'))
    a = np.frombuffer(w.readframes(w.getnframes()), np.int16).astype(np.float32) / 32768
    return a, w.getframerate()


def _sentences(text):
    out, cur = [], ''
    for tok in text.split(' '):
        cur = (cur + ' ' + tok).strip()
        if tok.endswith(('.', '?', '!')):
            out.append(cur); cur = ''
    if cur:
        out.append(cur)
    return out


def _speech_spans(a, sr, n_sent):
    hop = int(sr * .02)
    e = np.array([np.sqrt(np.mean(a[i:i + hop] ** 2)) for i in range(0, len(a) - hop, hop)])
    on = e > .01
    gaps, st = [], None
    for i, v in enumerate(on):
        if not v and st is None:
            st = i
        if v and st is not None:
            gaps.append(((i - st) * .02, st * .02, i * .02)); st = None
    first = np.argmax(on) * .02; last = (len(on) - np.argmax(on[::-1])) * .02
    # sentence breaks = the (n_sent-1) longest internal gaps, in time order
    gaps = sorted(sorted(gaps, reverse=True)[:n_sent - 1], key=lambda g: g[1])
    spans, s0 = [], first
    for _, g0, g1 in gaps:
        spans.append((s0, g0)); s0 = g1
    spans.append((s0, last))
    return spans


ST, DUR, VO, SENT = {}, {}, [], []
t = LEAD
for i, (k, text) in enumerate(NARR):
    a, sr = _load(i, k)
    d = len(a) / sr
    ST[k], DUR[k] = t, d
    VO.append((t, os.path.join(VO_DIR, f'{i}_{k}.wav')))
    sents = _sentences(text)
    for s, (a0, a1) in zip(sents, _speech_spans(a, sr, len(sents))):
        SENT.append((k, t + a0, t + a1, s))
    t += d + GAP
END = ST[SCENES[-1]] + DUR[SCENES[-1]] + TAIL
NFRAMES = int(round(END * 24))


def _chunks(s, maxc=104):
    """split a sentence into caption chunks (<= 2 lines of ~56 chars)."""
    if len(s) <= maxc:
        return [s]
    words = s.split(' '); best, bi = 1e9, 1
    for i in range(1, len(words)):
        left = ' '.join(words[:i])
        score = abs(len(left) - len(s) / 2) - (25 if left.endswith(',') else 0)
        if score < best:
            best, bi = score, i
    return _chunks(' '.join(words[:bi]), maxc) + _chunks(' '.join(words[bi:]), maxc)


CAPS = []
for k, a0, a1, s in SENT:
    parts = _chunks(s)
    tot = sum(len(p) for p in parts); c = a0
    for p in parts:
        d = (a1 - a0) * len(p) / tot
        CAPS.append((c, c + d, p)); c += d


def wrap(s, maxc=56):
    if len(s) <= maxc:
        return [s]
    words = s.split(' '); best, bi = 1e9, 1
    for i in range(1, len(words)):
        l = len(' '.join(words[:i])); r = len(' '.join(words[i:]))
        if max(l, r) < best:
            best, bi = max(l, r), i
    return [' '.join(words[:bi]), ' '.join(words[bi:])]


if __name__ == '__main__':
    for k in SCENES:
        print(f'{k:12s} start {ST[k]:6.2f}  dur {DUR[k]:5.2f}')
    print('END', END, 'frames', NFRAMES)
    for c in CAPS:
        print(f'{c[0]:6.2f}-{c[1]:6.2f}  {wrap(c[2])}')
