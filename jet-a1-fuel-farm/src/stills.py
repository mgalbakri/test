import sys, time
from PIL import Image
import scenes
from timeline import END
ts = [float(x) for x in sys.argv[1:]]
for t in ts:
    t0 = time.time()
    img = scenes.render(int(round(t * 24)))
    Image.fromarray(img).save(f'../build/still_{t:05.1f}.png')
    print(t, round(time.time() - t0, 2), 's')
