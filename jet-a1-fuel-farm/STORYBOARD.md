# Keeping Water Out of the Wing
**How a Jet A-1 fuel farm works under JIG standards: an 86-second explainer for the board**

| | |
|---|---|
| Deliverable | `jet-a1-fuel-farm.mp4`: 1920×1080, 24 fps, H.264 + AAC stereo, 86.5 s, open captions burned in |
| Audience | Board members: non-specialist, decision-level |
| Core idea (cause → effect) | **Water is heavier than fuel, so it sinks. JIG design and routine let gravity, time and testing remove it before fuel reaches an aircraft.** |
| Opening question | "Fuel arrives certified. Why does the farm spend hours refusing to use it?" |
| Surprising reveal | The waiting *is* the cleaning. Gravity does the work, and the tank is designed around it. |
| Final image | The narrator holds up one sample jar against a rising paper sun: clear, bright, nothing at the bottom. |
| Narration | 191 words, ~148 wpm while speaking, ~132 wpm across the runtime (target 135) |

---

## Production calls I made

- **Narrator voice:** Piper neural TTS (`en_US-lessac-high`), slowed 20% with 0.45 s sentence pauses for a warm, unhurried read. Swap in a human VO by replacing `build/vo/*.wav` and re-running `audio.py` and `render.py`. The timing re-flows from the new audio automatically.
- **One continuous paper world.** Every scene lives on the same diorama, and a camera moves between them, so there are no cuts at all. The narrator bot is drawn in screen space at a fixed 100×100 px (10 px cells), so its scale never changes even when the camera zooms 2×.
- **Boil:** every paper edge, crayon line and letter is re-jittered every 3 frames ("on threes", 8 drawings/s), by 1–2 px.
- **Palette:** coral `#E4705A`, mustard `#E3A83A`, teal `#2F8C88`, cream `#F3E8CF`, charcoal `#2D2A28`, plus tints of these only. Fuel = pale mustard, water = teal, everywhere.
- **Captions** sit on a cream paper strip at y 900–1004, inside the 90% title-safe area (bottom margin ≥ 54 px, side margin ≥ 330 px).
- **On-screen labels** only add facts the narration doesn't say: spec numbers, densities, temperatures, standard references. None of them repeats a narration line.
- **Scene 6 (consequence)** is kept because it is the "why it matters" for a board: it's the only place the risk to an aircraft is shown.

---

## Timestamped storyboard

Times are mm:ss.s from the start of the film. "VO" marks the narration line spoken in that scene.

### 1 · HOOK: 00:00.0 – 00:09.6
| Time | Picture | On-screen text (non-narrated) | Sound |
|---|---|---|---|
| 00:00.4 | A torn-paper **Certificate of Quality** slides onto the stage over cardboard hills. The bot watches from the right. | `CERTIFICATE OF QUALITY` · `Jet A-1 · DEF STAN 91-091 / AFQRJOS` · test rows: density @ 15 °C 801.4 kg/m³, freezing point −51 °C, flash point 42 °C, appearance clear & bright | paper rustle |
| 00:03.2 | A teal **REFINERY ✓** stamp lands. | `REFINERY` | soft thump |
| 00:05.7 | The bot shrugs. A coral **?** pops above it. | (glyph only) | tap |
| 00:07.5 | A mustard **padlock** clips onto the certificate: the fuel is on hold. | (icon only) | tap |
| **Transition** 00:09.4 – 00:11.0 | **Lines become paths:** the certificate's four ruled result lines stretch and thicken into the farm's four pipelines, and the certificate shrinks away into the inlet. | | pencil drag |

### 2 · FAMILIAR WORLD: 00:10.6 – 00:21.6
| Time | Picture | On-screen text | Sound |
|---|---|---|---|
| 00:10.7 | Paper pieces drop onto the pipes in order: receipt filter, two white storage tanks (grade plates `JET A-1`, sight gauges), filter water separator with ΔP gauge, hydrant pit and hose, aircraft, depot sign. The bot hops left and points. | `JIG 2 · airport depot` | six small rustles, hop taps |
| 00:12.3 | Mustard flow-dashes run in through the receipt filter to both tanks. | | |
| 00:14.2 | The tank sight gauges rise. | | |
| 00:16.6 | Flow runs out through the separator to the aircraft. | | |
| 00:19.9 | Three zone labels are pencilled under the diorama, one per beat of "In, rest, out." | `receipt` · `storage` · `issue` | three pencil marks |
| **Transition** 00:20.6 – 00:23.4 | The sun sinks behind the hills and the moon rises (night tint). The camera pushes into Tank 1, and its front panel **peels down like paper**, revealing a cutaway full of fuel. | | long rustle |

### 3 · DISRUPTION: 00:22.4 – 00:31.1
| Time | Picture | On-screen text | Sound |
|---|---|---|---|
| 00:22.4 | Beside the tank, a paper thermometer's coral column falls. | | |
| 00:25.0 | Teal crayon wisps of damp air curl in through the roof vent. Condensation beads on the inner walls above the fuel. | `vent` | pencil |
| 00:27.3 – 00:30.4 | Tiny teal droplets appear throughout the fuel: water coming out of solution. | | |
| **Transition** 00:31.0 – 00:32.1 | **Particles regroup:** droplets start to fall, and the flat tank floor tilts into a cone-down slope. | | |

### 4 · MECHANISM: 00:31.5 – 00:47.6
| Time | Picture | On-screen text | Sound |
|---|---|---|---|
| 00:31.5 | Droplets sink, slide down the slope and pool as a teal layer at the bottom. Two paper tags on strings appear. | `Jet A-1 ≈ 0.80 kg/L` · `water 1.00 kg/L` | two rustles |
| 00:34.8 | Dashed pencil construction lines and a dimension line sketch over the tank (the design). The bot points. | | pencil |
| 00:38.0 | Pencil arrows run down both floor slopes. A coral ring circles the low point, and the sump drain and valve appear. | | tap |
| 00:41.6 | A paper hourglass flips, and its sand runs while the last slow droplets settle. | | rustle |
| 00:44.7 | The floating-suction arm swings up from the floor on its pivot, its coral float riding the surface. Fuel flows from near the top, out through the wall. | | tap |
| **Transition** 00:47.6 – 00:49.4 | **Line becomes path:** the sump drain line extends past the valve and rises to a sampling spout. The camera eases back. | | pencil |

### 5 · DISCOVERY: 00:48.4 – 00:59.6
| Time | Picture | On-screen text | Sound |
|---|---|---|---|
| 00:48.4 | The hourglass holds center frame. | | |
| 00:50.8 | It hands off to a heavy charcoal **gravity arrow** drawn down through the fuel onto the water layer. | | pencil |
| 00:52.4 | Day returns: the sun rises and the tint lifts. | | |
| 00:53.4 | A strip of seven paper day-squares is ticked off one by one. | (checks only) | seven soft taps |
| 00:55.2 | The coral valve turns. Water drips from the spout into a slops bucket, and the tank's water layer empties. | | valve tap, drips |
| 00:56.5 | A glass jar slides under the spout and fills with pale, bright fuel. Paper glints appear. | | rustle |
| 00:58.0 | Two test tags pop up with drawn checkmarks. | `water detector ✓` · `density @ 15 °C ✓` | two taps |
| **Transition** 00:59.6 – 01:01.6 | A dashed pencil **flight path** leaves the tank outlet. One teal droplet (the one that "skipped a step") rides it up and out. The camera follows into the sky. | | pencil, rustle |

### 6 · CONSEQUENCE: 01:00.5 – 01:09.4
| Time | Picture | On-screen text | Sound |
|---|---|---|---|
| 01:01.6 | A cut-paper wing cross-section among clouds: a fuel tank between the spars, a pylon, a coral engine nacelle, and a mesh fuel filter on the feed line. The droplet and three followers enter the tank. | | |
| 01:03.5 | Two tags appear. | `water: ice at 0 °C` · `Jet A-1 stays liquid to −47 °C` | taps |
| 01:05.1 | **Particles regroup into objects:** each droplet shrinks and crystallizes into a teal ice star. | | four high ticks |
| 01:06.1 | The crystals drift down onto the filter mesh, more arrive, and the screen clogs. The mustard flow to the engine slows, turns coral, and stops. | | ticks |
| 01:08.5 | A coral warning triangle pops up. | (icon only) | low tap |
| **Transition** 01:09.2 – 01:11.2 | The flight path retracts back down to the farm, and the camera pulls out to the full diorama (front panel restored). | | rustle |

### 7 · RECAP: 01:10.3 – 01:26.5
| Time | Picture | On-screen text | Sound |
|---|---|---|---|
| 01:10.3 | A paper magnifier opens over the separator: coalescer elements with small drops merging and falling into its sump while fuel flows through. | `EI 1581` | rustle, tap |
| 01:13.3 | A clipboard drops in. Four checks are ticked, a signature is scribbled, and a teal stamp lands. | `Batch 0427 · Tank 1` · appearance / water / density / filter pressure | pencil, pencil, thump |
| 01:17.1 | Three paper icons pop up in turn: **gravity arrow, hourglass, sample jar**. | (icons only) | three taps |
| 01:19.7 – 01:21.1 | **Objects regroup:** the arrow and hourglass slide into the jar. A fresh cream sheet slides up over the farm, and the bot hops to center and raises its arms. | | long rustle, hop |
| 01:20.9 – 01:26.5 | **FINAL IMAGE:** the jar settles into the bot's hands above its head as a big gouache sun rises behind it and crayon rays draw on. The fuel is clear and bright, with nothing at the bottom. Hold, then a soft paper fade. | | bed resolves to D |

---

## Final narration script

| Scene | Time in | Line |
|---|---|---|
| 1 · Hook | 00:01.1 | Every litre of jet fuel at this airport arrives already certified. |
| 1 · Hook | 00:05.7 | So why does the fuel farm spend hours refusing to use it? |
| 2 · Familiar world | 00:10.7 | Here's the farm. |
| 2 · Familiar world | 00:12.3 | Fuel arrives by pipeline, rests in big storage tanks, then flows out through filters to the aircraft. |
| 2 · Familiar world | 00:19.9 | In, rest, out. |
| 3 · Disruption | 00:22.5 | But overnight, the air cools. |
| 3 · Disruption | 00:25.1 | The tanks breathe in damp air, and water dissolved in the fuel comes out as tiny droplets. |
| 4 · Mechanism | 00:31.6 | Water is heavier than fuel, so it sinks. |
| 4 · Mechanism | 00:34.8 | JIG design is built on that. |
| 4 · Mechanism | 00:38.0 | Tank floors slope down to a drain called a sump. |
| 4 · Mechanism | 00:41.6 | New fuel must settle before it moves. |
| 4 · Mechanism | 00:44.7 | And a floating suction draws only from near the top. |
| 5 · Discovery | 00:48.4 | So the waiting isn't slowness. |
| 5 · Discovery | 00:50.9 | It's gravity doing the cleaning. |
| 5 · Discovery | 00:53.4 | Every day, sumps are drained, and a sample jar must look clear and bright, with no free water. |
| 6 · Consequence | 01:00.5 | Skip a step, and water rides along. |
| 6 · Consequence | 01:03.5 | At cruising altitude it can freeze into ice crystals that clog an aircraft's fuel filters. |
| 7 · Recap | 01:10.4 | A final filter water separator strips the last drops, and every release is signed and recorded. |
| 7 · Recap | 01:17.1 | Gravity, time, and testing. |
| 7 · Recap | 01:20.0 | That is how a fuel farm keeps water out of the wing. |

---

## Accuracy notes (for a reviewer)

- **JIG 2** is the JIG standard for airport depots (fuel farms). It works alongside EI/JIG 1530 (quality assurance from manufacture to airport) and EI 1581 (filter water separator specification). Jet A-1 is supplied to DEF STAN 91-091 / the AFQRJOS checklist, with a refinery Certificate of Quality.
- **The hold on receipt is real.** Product received into depot storage is quarantined. It settles, the tank is sampled and tested (appearance, water, and density checked against the certificate), and an authorized person releases it before issue. The film's "refusing to use it" refers to this. It does not quote a specific settling time, because the required time depends on tank design and fuel depth under the applicable standard.
- **Water sources shown:** cooling lowers how much water fuel can hold, so dissolved water comes out as free droplets, and tanks "breathe" moist air through their vents as they cool.
- **Densities:** Jet A-1 is 775–840 kg/m³ at 15 °C (≈ 0.80 kg/L); water is ≈ 1.00 kg/L. That difference is why water sinks.
- **Tank design shown:** a cone-down (sloped) floor to a low-point sump drain, and a floating suction that draws from the upper layer. Both are standard features of JIG depot storage.
- **Daily checks:** daily sump draining and a visual "clear and bright" sample check with a chemical water detector are routine JIG depot checks.
- **Consequence:** Jet A-1's maximum freezing point is −47 °C, but free water freezes at 0 °C. At cruise, fuel in the wing can be well below 0 °C, and ice crystals can restrict aircraft fuel filters and heat exchangers. This was a factor in the 2008 BA38 accident.
- **Illustrative values:** the certificate values (801.4 kg/m³, −51 °C, 42 °C) and "Batch 0427" are illustrative but within specification. They are not from a real batch.
- **Simplifications:** the farm has two tanks and one separator. Real depots also have receipt filtration specs, product recovery tanks, bonding, and more checks on the filter/ΔP side. Those were left out because they don't serve the one cause-and-effect idea.

---

## Rebuilding

```bash
pip install pillow numpy scipy piper-tts      # + ffmpeg
cd src
python3 timeline.py      # prints scene starts and caption chunks
python3 audio.py         # build/mix.wav
WORKERS=4 python3 render.py
python3 stills.py 17 46.5 85   # optional: preview single frames
```
Narration text lives in `narration.json`. Piper voices are not committed; regenerate with
`python3 -m piper -m en_US-lessac-high.onnx --length-scale 1.2 --sentence-silence 0.45 -f build/vo/<i>_<scene>.wav`.
