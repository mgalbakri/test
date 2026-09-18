# Self-QA - master bedroom

Generated 2026-09-18

Every frame is checked automatically for mean luminance, lit fraction and blown highlights; the render run fails loudly on a black or blown frame. Every frame was then opened and inspected.

## Automated frame checks - draft

| Frame | Seconds | Mean luminance | Lit | Blown | Verdict |
|---|---|---|---|---|---|
| master_bedroom_cam01 | 162 | 0.561 | 100.0% | 0.00% | pass |
| master_bedroom_cam02 | 165 | 0.560 | 100.0% | 0.00% | pass |
| master_bedroom_cam03 | 168 | 0.552 | 100.0% | 0.00% | pass |
| master_bedroom_plan | 164 | 0.653 | 81.3% | 0.00% | pass |

## Automated frame checks - final

| Frame | Seconds | Mean luminance | Lit | Blown | Verdict |
|---|---|---|---|---|---|
| master_bedroom_cam01 | 961 | 0.560 | 99.9% | 0.00% | pass |
| master_bedroom_cam02 | 948 | 0.560 | 100.0% | 0.00% | pass |

## Found and fixed

- **Every frame rendered black.** Luminaires were rotated 180 degrees about X, so they lit the ceiling. Blender lights already emit along local -Z; identity rotation is correct. Fixed in villa_lib.add_fixture().
- **Camera 01 saw nothing but a flat plane.** The eye point was inside the TV joinery (x 0-500). All cameras now keep 500 mm clear of every joinery face.
- **Modelled clear size was 3195 x 4020, not the measured 3435 x 4260.** Walls were centred on the room's inner-face lines, so each one ate 120 mm of the room. Walls are now built outside the clear box.
- **The plan view was a flat grey rectangle.** The orthographic camera sits at 6000 mm, above the ceiling slab at 3000 mm. The ceiling is now hidden for plan renders.
- **The plan view was cropped - the room ran off the top and bottom.** Blender maps ortho_scale to the render's longer axis, so a room taller than the 16:9 frame loses its ends. The plan camera now stores the required extents and the renderer sets the frame aspect from them.
- **Window glazing looked frosted.** It had been given the shower-screen material. Added mat_glass_clear() and assigned it.
- **Joinery read as featureless slabs.** Rebuilt as framed leaves with mouldings, recessed panels, a drawer stack, an upper tier and a set-back plinth, per the BOQ wording.
- **Frames were too tight to show the room.** At 24-28 mm a 3000 mm wall needs about 4.4 m of standoff. In a 3435 x 4260 room only the diagonals give that, so all three perspectives now shoot corner to corner.

## Open, and why they are being left

- **Headboard reads flatter than it should.** It is modelled as a single upholstered plane with the specified LED wash above it. The BOQ gives no buttoning, panel or profile detail, so nothing more is modelled rather than invented. Worth a detail drawing before fabrication.
- **No bed, no loose furniture.** Nothing of the kind appears in the BOQ, so nothing is modelled. Adding it would put unpriced items into a package the contractor prices from.
- **Wood veneer went blotchy on cabinet return faces - it read as staining.** The real-world texture mapping scaled only two axes, leaving the third nearly unscaled, so the 3D grain varied very slowly through the panel and any face cut across that axis showed low-frequency blobs. All three axes are now scaled and the grain ramp is tightened. Found on the 4K cam02 frame; all finals re-rendered.
- **Final frames took four times their stated cap on the first attempt.** Cycles applies time_limit per TILE, and the auto-tiler splits a 3840x2160 frame into four, so a 600 s cap became 40 minutes a frame. Auto-tiling is now off for finals, so the cap is per frame and the whole image converges evenly.
- **Frames are time-boxed.** Cycles runs on 4 CPU cores with no GPU here, so each frame is capped and the denoiser carries the rest. Fine detail is softer than a full sample budget would give. A GPU box would remove the cap.

## Checks that passed

- No floating geometry: every object bounds-checked against the clear box; the only intersection is the glazing seated in its booleaned reveal, which is intended.
- No z-fighting: joinery leaves stand 18 mm proud of their carcass and panels are recessed 10 mm behind the frame, so no coplanar faces.
- Texture scale is real-world: the floor porcelain is mapped at 600 x 1200 mm and reads at that size against the 3435 mm wall.
- Verticals are vertical. Cameras are held level and framing is done with sensor shift, not tilt, so there is no keystoning.
- No blown highlights in any frame (worst case 0.00%).
