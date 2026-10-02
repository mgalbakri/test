"""Synthesize narration with Piper and write build/timeline.json (scene starts, sentence spans, captions).

usage: python3 tools/tts.py /path/to/en_US-ryan-high.onnx
"""
import json, os, subprocess, sys, wave
import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
VO = os.path.join(ROOT, 'build', 'vo')
LEAD, GAP, TAIL = 1.6, 1.1, 4.0
LENGTH_SCALE, SENT_SIL = 1.2, 0.45


def sentences(text):
    out, cur = [], ''
    for tok in text.split(' '):
        cur = (cur + ' ' + tok).strip()
        if tok.endswith(('.', '?', '!')):
            out.append(cur); cur = ''
    if cur:
        out.append(cur)
    return out


def spans(a, sr, n):
    hop = int(sr * .02)
    e = np.array([np.sqrt(np.mean(a[i:i + hop] ** 2)) for i in range(0, len(a) - hop, hop)])
    on = e > .012
    gaps, st = [], None
    for i, v in enumerate(on):
        if not v and st is None:
            st = i
        if v and st is not None:
            gaps.append(((i - st) * .02, st * .02, i * .02)); st = None
    first = np.argmax(on) * .02; last = (len(on) - np.argmax(on[::-1])) * .02
    gaps = sorted(sorted(gaps, reverse=True)[:n - 1], key=lambda g: g[1])
    out, s0 = [], first
    for _, g0, g1 in gaps:
        out.append((s0, g0)); s0 = g1
    out.append((s0, last))
    return out


def chunks(s, maxc=90):
    if len(s) <= maxc:
        return [s]
    words = s.split(' '); best, bi = 1e9, 1
    for i in range(1, len(words)):
        left = ' '.join(words[:i])
        score = abs(len(left) - len(s) / 2) - (30 if left.endswith((',', ':')) else 0)
        if score < best:
            best, bi = score, i
    return chunks(' '.join(words[:bi]), maxc) + chunks(' '.join(words[bi:]), maxc)


def main(model):
    os.makedirs(VO, exist_ok=True)
    narr = json.load(open(os.path.join(ROOT, 'narration.json')))
    t = LEAD
    scenes, caps, sents, vo = [], [], [], []
    for i, (key, text) in enumerate(narr):
        path = os.path.join(VO, f'{i}_{key}.wav')
        subprocess.run([sys.executable, '-m', 'piper', '-m', model, '--length-scale', str(LENGTH_SCALE),
                        '--sentence-silence', str(SENT_SIL), '-f', path], input=text.encode(), check=True,
                       capture_output=True)
        w = wave.open(path); sr = w.getframerate()
        a = np.frombuffer(w.readframes(w.getnframes()), np.int16).astype(np.float32) / 32768
        d = len(a) / sr
        ss = sentences(text)
        sp = spans(a, sr, len(ss))
        scenes.append(dict(key=key, start=round(t, 3), dur=round(d, 3),
                           sentences=[dict(t0=round(t + a0, 3), t1=round(t + a1, 3), text=s)
                                      for s, (a0, a1) in zip(ss, sp)]))
        for s, (a0, a1) in zip(ss, sp):
            parts = chunks(s); tot = sum(len(p) for p in parts); c = t + a0
            for p in parts:
                dd = (a1 - a0) * len(p) / tot
                caps.append(dict(t0=round(c, 3), t1=round(c + dd, 3), text=p)); c += dd
        vo.append(dict(t=round(t, 3), file=f'build/vo/{i}_{key}.wav'))
        t += d + GAP
    end = scenes[-1]['start'] + scenes[-1]['dur'] + TAIL
    out = dict(fps=24, end=round(end, 3), frames=int(round(end * 24)), scenes=scenes, captions=caps, vo=vo)
    json.dump(out, open(os.path.join(ROOT, 'build', 'timeline.json'), 'w'), indent=1)
    words = sum(len(x[1].split()) for x in narr)
    speech = sum(s['dur'] for s in scenes)
    print(f'end {end:.2f}s  words {words}  wpm(speech) {words / speech * 60:.0f}  wpm(overall) {words / end * 60:.0f}')
    for s in scenes:
        print(f"{s['key']:11s} {s['start']:6.2f} +{s['dur']:5.2f}")
        for x in s['sentences']:
            print(f"     {x['t0']:6.2f}-{x['t1']:6.2f} {x['text']}")


if __name__ == '__main__':
    main(sys.argv[1])
