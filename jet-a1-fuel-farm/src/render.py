"""Render all frames in parallel chunks to H.264 segments, then mux with the mix."""
import os, subprocess, sys
from multiprocessing import Pool
from timeline import NFRAMES, ROOT

BUILD = os.path.join(ROOT, 'build')
WORKERS = int(os.environ.get('WORKERS', os.cpu_count() or 4))


def chunk(args):
    i, f0, f1 = args
    import scenes
    out = os.path.join(BUILD, f'seg_{i:02d}.mp4')
    p = subprocess.Popen(['ffmpeg', '-y', '-loglevel', 'error', '-f', 'rawvideo', '-pix_fmt', 'rgb24',
                          '-s', '1920x1080', '-r', '24', '-i', '-', '-c:v', 'libx264', '-preset', 'slow',
                          '-crf', '17', '-pix_fmt', 'yuv420p', '-tune', 'animation', out], stdin=subprocess.PIPE)
    for f in range(f0, f1):
        p.stdin.write(scenes.render(f).tobytes())
        if (f - f0) % 48 == 0:
            print(f'seg {i}: frame {f}/{f1}', flush=True)
    p.stdin.close(); p.wait()
    return out


def main():
    n = int(sys.argv[1]) if len(sys.argv) > 1 else NFRAMES
    segs = WORKERS * 3
    step = -(-n // segs)
    jobs = [(i, i * step, min(n, (i + 1) * step)) for i in range(segs) if i * step < n]
    with Pool(WORKERS) as pool:
        outs = pool.map(chunk, jobs, chunksize=1)
    lst = os.path.join(BUILD, 'segs.txt')
    open(lst, 'w').write(''.join(f"file '{o}'\n" for o in outs))
    final = os.path.join(ROOT, 'jet-a1-fuel-farm.mp4')
    subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-f', 'concat', '-safe', '0', '-i', lst,
                    '-i', os.path.join(BUILD, 'mix.wav'), '-c:v', 'copy', '-c:a', 'aac', '-b:a', '192k',
                    '-movflags', '+faststart', '-shortest', final], check=True)
    print('wrote', final)


if __name__ == '__main__':
    main()
