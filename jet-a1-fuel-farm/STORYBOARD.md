# Jet A-1 Fuel Farm: Five Controlled Steps
**A 3D technical explainer of airport depot operations to JIG 2, for the board**

| | |
|---|---|
| Deliverable | `jet-a1-fuel-farm.mp4`: 1920×1080, 24 fps, H.264 (CRF 16) + AAC 192 kb/s stereo, 81.3 s, captions burned in |
| Audience | Board members: non-specialist, decision-level |
| Core idea (cause → effect) | Water and dirt are the threat to jet fuel. **Each compartment of the farm is a barrier that removes them, and each step is proven before fuel moves on.** |
| Opening question | What has to happen before a litre of Jet A-1 is allowed into a wing? |
| Reveal | The tank is designed around gravity: water sinks to a sump, and fuel is drawn from the top. |
| Final image | An aerial view of the whole farm with one amber fuel path from pipeline to wing, and five teal numbered barriers along it. |
| Narration | 173 words, ~150 wpm while speaking, 128 wpm across the runtime (target 135). Male voice, measured and serious. |

## Look and feel (production calls)

- **Real-time 3D (Three.js, physically based materials)** rendered headless at 1080p and 24 fps, with ACES tone mapping, soft directional key light and shadows, and image-based fill.
- **One continuous camera flight** through one modelled facility, following the fuel's own route: pipeline → receipt filter → bunded tank compound → QC lab → pumps and filter water separators → buried hydrant main → dispenser → wing. There are no cuts. Every transition travels along the pipe that connects the two compartments.
- **Cutaways** use live section planes. Tank T-101 and filter water separator FWS-1 open up to show the internals: the cone-down floor and sump, the water layer, the floating suction, and the coalescer and separator elements.
- **Colour is functional, not decorative.** Amber = fuel flow, teal = water and barriers, coral = valves and alerts. Equipment is neutral white or steel on a graphite ground with a faint survey grid. Tanks carry the EI 1542 grade marking (black band, white "JET A-1").
- **Graphics:** a step chip top-left (STEP 0x + name), a five-step tracker top-right, leader-line callouts that name components and specs the voice does not say, data panels (certificate, recertification test, daily control), and captions bottom-centre inside title-safe.
- **Sound:** a low tonal pad (one chord per section), facility room tone, a pump hum under filtration, soft UI ticks on callouts and checks, a low thud on the release stamp, and soft air whooshes on camera moves. All of it is ducked under the voice. Mix integrated loudness is −15.3 LUFS.
- **What the paper version had and this one drops:** the hand-made textures, boil and pixel-bot narrator, as requested.

---

## Timestamped storyboard

### 0 · OVERVIEW: 00:00.0 – 00:12.8
| Time | Picture | On-screen graphics | Sound |
|---|---|---|---|
| 00:00 | Fade up on a high aerial of the whole depot: the pipeline from the left, receipt filter, bunded compound with two fixed-roof tanks, QC lab, pump and filter skid, and the apron with an aircraft on stand and a hydrant dispenser. Slow drift. | Title: **Jet A-1 Fuel Farm**, with *JIG 2 · Airport depot operations* and *From pipeline to wing: five controlled steps* | Pad fades in, room tone |
| 00:03.0 – 00:05.0 | Five station markers rise one by one. | 01 RECEIPT · 02 STORAGE · 03 RELEASE · 04 FILTRATION · 05 DELIVERY | |
| **Move** 00:11.0 – 00:14.4 | The camera dives down to pipeline level and settles beside the incoming line. | | whoosh |

### 1 · RECEIPT: 00:12.8 – 00:23.1
| Time | Picture | On-screen graphics | Sound |
|---|---|---|---|
| 00:12.8 | Tracking along the pipeline toward the receipt filter. | STEP 01 RECEIPT · tracker | |
| 00:14.8 | Amber flow chevrons run along the pipeline. | Callout: *Cross-country pipeline — Jet A-1 batch from refinery*. Panel: **Certificate of Quality**, Jet A-1 · DEF STAN 91-091 / AFQRJOS, batch 0427, density 801.4 kg/m³, freezing point −51 °C, flash point 42 °C | ticks |
| 00:18.6 | Flow passes through the receipt filter and runs on to the tank manifold. | Callouts: *Receipt filtration — removes water and particulates on intake*; *Sample point — density vs certificate · Δ ≤ 3.0 kg/m³* | ticks |
| **Move** 00:22.5 – 00:25.3 | The camera follows the inlet line into the bund and swings round to face T-101. | | whoosh |

### 2 · STORAGE & SETTLING: 00:23.1 – 00:33.9
| Time | Picture | On-screen graphics | Sound |
|---|---|---|---|
| 00:23.7 – 00:25.5 | A section plane sweeps through T-101, opening the front half. Inside: fuel, the cone-down floor, the sump, and the floating suction arm. Teal droplets appear through the fuel. | STEP 02 | |
| 00:25.4 | | Callouts: *Cone-down floor — low point at the tank centre*; *Epoxy-lined shell — fixed roof · free-vent* | ticks |
| 00:28.0 – 31.5 | The droplets sink, slide down the slope to the centre, and build a teal water layer in the sump. | *Jet A-1 — ρ 775–840 kg/m³* (amber); *Free water — ρ ≈ 1000 kg/m³* (teal) | ticks |
| 00:31.5 – 00:34.0 | The drain valve turns, teal flow runs out of the sump line, and the water layer shrinks. The camera pushes low toward the sump. | *Water drain-off — sump drained to slops* | tick |

### 3 · RELEASE: 00:33.9 – 00:42.4
| Time | Picture | On-screen graphics | Sound |
|---|---|---|---|
| 00:33.9 – 00:36.5 | The camera rises and pulls back to frame T-101 with the QC laboratory in the foreground. A coral status tag sits above the tank. | Callout: *Quality control laboratory*. Tag: **T-101 · QUARANTINE** | whoosh |
| 00:35.7 – 00:38.6 | The recertification panel builds row by row with teal checks. | **Recertification test · T-101**: settling period complete ✓ · appearance clear & bright ✓ · free water (detector) pass ✓ · density @ 15 °C 801.2 kg/m³ (Δ 0.2) ✓ | four ticks |
| 00:38.1 – 00:39.2 | A signature is drawn and a stamp lands. The tank tag flips to teal. | **RELEASED FOR ISSUE** · **T-101 · RELEASED** | low thud |

### 4 · FILTRATION: 00:42.4 – 00:55.8
| Time | Picture | On-screen graphics | Sound |
|---|---|---|---|
| 00:42.4 – 00:45.7 | The camera drops back into the open tank, low on the floating suction. The float glows briefly, and amber flow runs from the float, down the arm and out of the shell. | STEP 04 · *Pontoon float — rides the fuel surface* · *Pivoting draw-off arm — outlet clear of bottom water* | ticks, pump hum begins |
| 00:45.7 – 00:50.4 | **Move along the issue line:** the flow leads the camera out of the bund, past the pumps, to the filter water separators. FWS-1 opens in section. | | whoosh |
| 00:50.0 – 00:55.0 | Amber flow passes through the white coalescer elements. Teal droplets grow, fall and collect in the sump boot, while the teal separator elements stand behind. The ΔP gauge needle rises gently. | *Stage 1 · Coalescer elements — merge fine droplets into drops*; *Stage 2 · Separator elements — hydrophobic screens repel water*; *Water sump — drained and checked daily*; *Differential pressure gauge — EI 1581 vessel · ΔP logged* | ticks |

### 5 · DELIVERY: 00:55.8 – 01:06.0
| Time | Picture | On-screen graphics | Sound |
|---|---|---|---|
| 00:55.8 – 00:58.8 | The camera follows the outlet line as it dives below grade. The ground turns translucent to reveal the buried hydrant main, and amber flow races toward the apron. T-101's cutaway closes behind. | STEP 05 · *Hydrant main — buried · cathodically protected* | whoosh |
| 00:60.4 – 01:06.0 | The camera arrives under the left wing. Flow rises through the pit valve and the inlet hose into the hydrant dispenser, then through its filter and up the delivery hose to the underwing coupling. | *Hydrant pit valve* · *Hydrant dispenser — filter · meter · deadman control* · *Wing refuelling coupling — pressure refuel, underwing* | ticks |

### 6 · DAILY CONTROL & RECAP: 01:06.0 – 01:21.3
| Time | Picture | On-screen graphics | Sound |
|---|---|---|---|
| 01:05.6 – 01:11.5 | The camera rises steadily from the wing into a full aerial of the depot. | Panel: **Daily quality control**: tank & vessel low-point samples ✓ · chemical water detector ✓ · filter ΔP readings trended ✓ · hydrant low-point drains ✓ · records signed & retained ✓ | five ticks |
| 01:11.6 – 01:15.0 | The whole route lights up in amber at once, from the pipeline to the wing. | Numbered teal barriers rise one by one: **1** Receipt filter · **2** Settling & sump · **3** Release test · **4** Filter water separator · **5** Dispenser filter | five rising ticks |
| 01:15.8 – 01:21.3 | **Final image:** the aerial holds on one amber path with five teal barriers. Fade to graphite. | CLEAN · DRY · ON-SPECIFICATION · PROVEN | low thud, pad resolves |

---

## Final narration script

| Section | Time in | Line |
|---|---|---|
| Overview | 00:01.6 | Every litre of Jet A-1 at this airport passes through a fuel farm built to JIG standards. |
| Overview | 00:08.2 | Its job: deliver clean, dry fuel, and prove it. |
| 1 · Receipt | 00:12.8 | Step one, receipt. |
| 1 · Receipt | 00:14.6 | Fuel arrives by pipeline with a refinery certificate. |
| 1 · Receipt | 00:18.5 | It is filtered on the way in, and sampled against that certificate. |
| 2 · Storage | 00:23.1 | Step two, storage. |
| 2 · Storage | 00:25.3 | Tank floors slope down to a sump. |
| 2 · Storage | 00:27.9 | Water is heavier than fuel, so it sinks, settles, and is drained away. |
| 3 · Release | 00:33.9 | Step three, release. |
| 3 · Release | 00:35.9 | Only after settling and a passed test does an authorised person release the tank for use. |
| 4 · Filtration | 00:42.4 | Step four, filtration. |
| 4 · Filtration | 00:44.9 | A floating suction draws fuel from near the top. |
| 4 · Filtration | 00:48.4 | Filter water separators then strip out remaining water and dirt, while gauges monitor every filter. |
| 5 · Delivery | 00:55.8 | Step five, delivery. |
| 5 · Delivery | 00:58.0 | Fuel flows through the underground hydrant network to the aircraft stand, and a dispenser filters it once more into the wing. |
| Control & recap | 01:05.9 | Every day, sumps are drained, samples must be clear and bright, and every result is recorded. |
| Control & recap | 01:12.2 | Because water left in jet fuel can freeze at altitude, each step is a barrier. |

---

## Technical accuracy notes (for review by the fuel QA lead)

- **Standards referenced:** JIG 2 (airport depots), EI/JIG 1530 (quality assurance from refinery to airport), DEF STAN 91-091 / AFQRJOS (Jet A-1 specification and checklist), EI 1581 (filter water separators) and EI 1542 (product identification marking).
- **Receipt:** product arrives with a refinery Certificate of Quality and is filtered into storage. Receipt samples are compared with the certificate. The 3.0 kg/m³ density-difference criterion shown is the usual EI/JIG 1530 comparison limit. **Please confirm it against your site's current QA manual.**
- **Storage:** the cone-down floor and sump are drawn **exaggerated** so they read on screen (real slopes are shallow). The film deliberately states no settling duration, because the requirement depends on tank configuration and the applicable standard.
- **Release:** the tank stays in quarantine until settling is complete and a recertification test passes (appearance, free water, density), after which an authorised person releases it. All values shown are illustrative but within specification. Batch 0427 is fictitious.
- **Filtration:** issue is via a floating suction, then filter water separators to EI 1581 (coalescer stage + separator stage + water sump), with differential pressure monitored.
- **Delivery:** the buried hydrant main runs to a pit valve, and a hydrant dispenser (with its own filtration, meter and deadman control) pressure-refuels through the underwing coupling.
- **Consequence:** free water can freeze into ice in aircraft fuel systems at altitude. That is why every barrier exists.
- **Simplifications:** a single tank and FWS are shown in section, with no product-recovery or slops system detail, no bonding or lightning protection, no fire systems, and a single generic narrowbody aircraft.

---

## Rebuilding

```bash
npm install                                   # three + playwright-core (uses /opt/pw-browsers chromium)
pip install numpy scipy piper-tts
python3 tools/tts.py path/to/en_US-ryan-high.onnx   # → build/vo/*.wav + build/timeline.json
python3 tools/audio.py                        # → build/mix.wav
WORKERS=4 node tools/render.mjs all           # → jet-a1-fuel-farm.mp4
node tools/render.mjs stills 17 46 79.5       # optional: preview frames into build/
```
The narration lives in `narration.json`. Every graphic, flow and camera beat is anchored to the measured sentence times in `build/timeline.json`, so editing a line and re-running the three steps re-times the whole film. A human voice-over can replace the synthetic one. Record the seven lines, adjust `tools/tts.py` to read those WAVs instead of synthesizing, and re-run all three steps. The timing and every visual beat will follow the new read.
