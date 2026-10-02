// Headless render: node tools/render.mjs [stills t1 t2 ...] | [all]
import { chromium } from 'playwright-core';
import http from 'http'; import fs from 'fs'; import path from 'path'; import { spawn } from 'child_process';
const ROOT = path.resolve(path.dirname(new URL(import.meta.url).pathname), '..');
const BUILD = path.join(ROOT, 'build');
const TYPES = { '.js': 'text/javascript', '.mjs': 'text/javascript', '.html': 'text/html', '.json': 'application/json', '.ttf': 'font/ttf' };
const srv = http.createServer((q, s) => {
  const f = path.join(ROOT, decodeURIComponent(q.url.split('?')[0]));
  fs.readFile(f, (e, d) => { if (e) { s.writeHead(404); s.end(); return; } s.writeHead(200, { 'Content-Type': TYPES[path.extname(f)] || 'application/octet-stream' }); s.end(d); });
}).listen(0);
const PORT = srv.address().port;
const CHROME = process.env.CHROME || '/opt/pw-browsers/chromium-1194/chrome-linux/chrome';
const ARGS = ['--use-gl=angle', '--use-angle=swiftshader', '--enable-unsafe-swiftshader', '--ignore-gpu-blocklist'];

async function openPage() {
  const b = await chromium.launch({ executablePath: CHROME, args: ARGS });
  const p = await b.newPage({ viewport: { width: 1920, height: 1080 } });
  p.on('console', m => { if (m.type() === 'error' || m.type() === 'warning') console.log('[page]', m.text()); });
  p.on('pageerror', e => console.log('[pageerror]', e.message));
  await p.goto(`http://localhost:${PORT}/web/index.html`);
  await p.waitForFunction('window.ready === true', null, { timeout: 120000 });
  return { b, p };
}
const decode = (url) => Buffer.from(url.slice(url.indexOf(',') + 1), 'base64');

const mode = process.argv[2] || 'all';
if (mode === 'stills') {
  const { b, p } = await openPage();
  for (const t of process.argv.slice(3).map(Number)) {
    const t0 = Date.now(); const url = await p.evaluate(t => renderAt(t), t);
    fs.writeFileSync(path.join(BUILD, `still_${t.toFixed(1).padStart(5, '0')}.jpg`), decode(url));
    console.log('still', t, Date.now() - t0, 'ms');
  }
  await b.close();
} else {
  const TL = JSON.parse(fs.readFileSync(path.join(BUILD, 'timeline.json')));
  const N = TL.frames, W = +(process.env.WORKERS || 4), SEG = W * 2;
  const step = Math.ceil(N / SEG); const jobs = [];
  for (let i = 0; i < SEG; i++) if (i * step < N) jobs.push([i, i * step, Math.min(N, (i + 1) * step)]);
  let next = 0; const t00 = Date.now(); let done = 0;
  async function worker() {
    const { b, p } = await openPage();
    while (next < jobs.length) {
      const [i, f0, f1] = jobs[next++];
      const out = path.join(BUILD, `seg_${String(i).padStart(2, '0')}.mp4`);
      const ff = spawn('ffmpeg', ['-y', '-loglevel', 'error', '-f', 'image2pipe', '-framerate', '24', '-c:v', 'mjpeg', '-i', '-',
        '-c:v', 'libx264', '-preset', 'slow', '-crf', '16', '-pix_fmt', 'yuv420p', '-r', '24', out], { stdio: ['pipe', 'inherit', 'inherit'] });
      for (let f = f0; f < f1; f++) {
        const url = await p.evaluate(t => renderAt(t), f / 24);
        if (!ff.stdin.write(decode(url))) await new Promise(r => ff.stdin.once('drain', r));
        done++; if (done % 48 === 0) console.log(`${done}/${N} frames  ${((Date.now() - t00) / 1000).toFixed(0)}s`);
      }
      ff.stdin.end(); await new Promise(r => ff.on('close', r));
    }
    await b.close();
  }
  await Promise.all(Array.from({ length: W }, worker));
  const list = path.join(BUILD, 'segs.txt');
  fs.writeFileSync(list, jobs.map(([i]) => `file '${path.join(BUILD, `seg_${String(i).padStart(2, '0')}.mp4`)}'`).join('\n') + '\n');
  const final = path.join(ROOT, 'jet-a1-fuel-farm.mp4');
  await new Promise((res, rej) => spawn('ffmpeg', ['-y', '-loglevel', 'error', '-f', 'concat', '-safe', '0', '-i', list, '-i', path.join(BUILD, 'mix.wav'),
    '-c:v', 'copy', '-c:a', 'aac', '-b:a', '192k', '-movflags', '+faststart', '-shortest', final], { stdio: 'inherit' }).on('close', c => c ? rej(c) : res()));
  console.log('wrote', final, ((Date.now() - t00) / 1000).toFixed(0), 's');
}
srv.close();
