# Mr. Mohammed & Mrs. Aziza Villa, Jeddah - 3D room package

Quotation R1-M.A.740-26 (20/07/2026) - report generated 2026-09-18

## BLUF

**1 of 9 rooms modelled. 7 of 9 cannot be modelled at all, because the as-built drawings contain no room names and nothing else identifies where those rooms are.**

- The drawings are dimensionally sound. Scale was verified twice: the PDFs reproduce six independent dimensions each to within 3.3 mm at 1:100, and the DWG's own DIMENSION entities return nine values that match the printed text exactly. Geometry is trustworthy.
- What is missing is **identity**, not measurement. The DWG's text layers (A_TEXT, ara-TEXT) are empty; all 64 MTEXT entities are dimension values. No room on either floor is labelled.
- Only the **master bedroom** could be pinned down with confidence, and only because BOQ items 31 and 33 are both exactly 4260 mm wide and one bedroom has walls of exactly 4260 mm.
- When that room was modelled to the measured geometry, **the quoted joinery did not fit** (V-01, V-02). That is a real cost and programme risk today, not a modelling artefact.
- **A stale quotation for a different villa (SAR 255,535.75) is sitting in the same workbook.** Make sure nobody is pricing this job off it.

## Rooms completed and outstanding

| Room | BOQ value (SAR) | Location | Status |
|---|---|---|---|
| Ground Floor - Entrance Salon | 44,911 | GF-EAST (ASSUMED - low) | Located, not yet modelled |
| First Floor - Powder Room, Mrs. Aziza | 14,450 | - (NOT LOCATED) | **BLOCKED - not located** |
| First Floor - Bathroom, Mrs. Aziza | 22,260 | - (NOT LOCATED) | **BLOCKED - not located** |
| First Floor - Office | 19,350 | - (NOT LOCATED) | **BLOCKED - not located** |
| First Floor - Powder Room, Mr. Mohammed | 9,950 | - (NOT LOCATED) | **BLOCKED - not located** |
| First Floor - Bathroom, Mr. Mohammed | 17,110 | - (NOT LOCATED) | **BLOCKED - not located** |
| First Floor - Hallways | 2,800 | FF-STAIR (ASSUMED - low) | Located, not yet modelled |
| First Floor - Kitchenette | 8,466 | - (NOT LOCATED) | **BLOCKED - not located** |
| First Floor - Master Bedroom | 30,830 | FF-NW-BED (ASSUMED - high) | Modelled + rendered |
| **Total** | **170,127** | | |

## Owner decisions required

**1. Confirm which physical room is which.** This is the one decision blocking 7 of the 9 models. The measured spaces are:

| Space | Floor | Measured clear size (mm) | Area (m2) | What is in it |
|---|---|---|---|---|
| FF-NW-BED | FF | 3435 x 4260 | 14.63 | bedroom |
| FF-SW-BED | FF | 3930 x 4170 | 16.39 | bedroom |
| FF-NE-BED | FF | 4140 x 4950 | 20.49 | bedroom |
| FF-SE-BED | FF | 4185 x 5265 | 22.03 | bedroom |
| FF-BATH-W | FF | 2195 x 1755 | 3.85 | bathroom |
| FF-BATH-S | FF | 1350 x 2430 | 3.28 | bathroom |
| FF-BATH-C | FF | 2805 x 1335 | 3.74 | bathroom |
| FF-BATH-N | FF | 1560 x 2955 | 4.61 | bathroom |
| FF-STAIR | FF | 2550 x 3500 | 8.93 | circulation |
| FF-VOID | FF | 1290 x 3500 | 4.51 | void |
| FF-RM-S1 | FF | 2430 x 2380 | 5.78 | room |
| FF-RM-S2 | FF | 1380 x 1965 | 2.71 | room |
| FF-RM-S3 | FF | 2910 x 1965 | 5.72 | room |
| GF-WEST | GF | 5425 x 10540 | 57.18 | open shell |
| GF-EAST | GF | 6060 x 9550 | 57.87 | open shell |
| GF-WC | GF | 2230 x 3895 | 8.69 | wc |
| GF-STAIR | GF | 2550 x 3500 | 8.93 | circulation |

**2. Confirm or correct the master bedroom joinery** - it is quoted at 4260 mm but the room cannot take it (V-01, V-02).

**3. Release a re-survey of the ground-floor WC block** stamped "NOT THE ACTUAL AS-BUILT" (C-02).

**4. Identify the "G.F. Guests Bathroom"** priced in item 5 but absent from the nine-room register (C-08).

## Top conflicts

| Ref | Severity | Source | Conflict | Resolution applied |
|---|---|---|---|---|
| C-01 | CRITICAL | BOQ workbook | The workbook holds three sheets. Only "nabati rest. (3)" (Quotation R1-M.A.740-26, 20/07/2026, "Mr. Mohammed & Mrs. Aziza Villa - Jeddah") is this project. Sheet "nabati rest. (2)" is a different job - "Privet Villa - Al nuoras - Jeddah", quotation RF-635 R3-25, addressed to M/S Subair General Construction, SAR 255,535.75 incl. VAT. Sheet "nabati rest." is a 2024 Riyadh delivery note. Both are unrelated to this villa. | Applied hierarchy rule 2: only sheet (3) governs. The other two are ignored. Confirm no one is pricing this villa off the SAR 255,535.75 figure. |
| C-02 | CRITICAL | Ground floor plan | A red hatched zone stamped "NOT THE ACTUAL AS-BUILT" covers the ground-floor WC block (space GF-WC, 2230 x 3895 mm). The drawing's own author disclaims that area. The same note is present in the DWG (MTEXT on layer A_DIM). | Geometry inside that hatch is treated as UNVERIFIED. Nothing is modelled there. A re-survey is required before that area can be priced or built. |
| C-03 | CRITICAL | All drawings | The drawings carry NO room names. Verified in the source DWG: layers A_TEXT and ara-TEXT are empty, and all 64 MTEXT entities are dimension values or the disclaimer. Neither PDF carries a room label either. | Room identity for all nine BOQ rooms is INFERENCE, not fact. Seven of the nine cannot be located at all. This is the single decision blocking the remaining models - see "Owner decisions required". |
| C-04 | HIGH | All drawings | No sections, elevations or ceiling plans were supplied - only two 1:100 floor plans. Ceiling heights, bulkheads, sill and head heights are therefore not given anywhere. | Ceiling heights DERIVED from the BOQ joinery heights (2800 / 2860 / 3000 mm floor-to-ceiling items). Sill 900 / head 2400 / door height 2100 mm are ASSUMED and tagged as such on every affected object. |
| C-05 | MEDIUM | All drawings | No north arrow on either plan or in the DWG. | Plan north ASSUMED to be world +Y for the Jeddah daylight study (21.49 N, 39.19 E, 16:00 local). Sun elevation 32.39 deg, azimuth 257.81 deg. If the true orientation differs, every daylight render must be re-run. |
| C-06 | MEDIUM | Reference render | No designer's reference render was supplied. inputs/reference/ is empty. | Aesthetic intent cannot be checked. Palette and finish character are driven solely by the BOQ material specifications. |
| C-07 | LOW | BOQ arithmetic | Item R1-M.A.740-26/3 (six wall shelves, G.F. Salon): quantity 1 x unit price SAR 2,200 but the line total reads SAR 2,000. | Sub-total is understated by SAR 200. Sheet total SAR 170,127 excl. VAT. |
| C-08 | HIGH | Room register vs BOQ | BOQ item 5 prices wall cladding and ceiling paint at a "G.F. Guests Bathroom". No guests bathroom appears in the nine-room register supplied. | Treated as a TENTH priced room. It needs a location and a specification before it can be modelled. |
| C-09 | HIGH | BOQ vs as-built geometry | The master-bedroom joinery cannot be installed as quoted in the room it must belong to. See variances V-01 and V-02. | Modelled as-measured, with the shortfall carried as a variance. Either the joinery is re-measured or the room assumption (C-03) is wrong. |
| C-10 | LOW | BOQ terminology | "doku paint" appears on four items (2, 3, 17). Not a standard finish name. | Read as Duco (nitrocellulose lacquer) on MDF. Confirm before fabrication - the BOQ warns that any specification change is re-priced at 100%. |
| C-11 | LOW | BOQ terminology | Marble named "Rossi Levanto" (items 14, 24) and "Verde Guatemale" (item 29). | Read as Rosso Levanto and Verde Guatemala respectively. Modelled to those. |

## Quantity variances affecting cost

| Ref | Room | BOQ line | Item | BOQ qty | Measured | Unit | Variance |
|---|---|---|---|---|---|---|---|
| V-01 | First Floor - Master Bedroom | R1-M.A.740-26/31 | Wardrobe run width | 4260 | 2630 | mm | -38.3% **FLAG** |
| V-02 | First Floor - Master Bedroom | R1-M.A.740-26/33 | TV-area run width | 4260 | 3140 | mm | -26.3% **FLAG** |
| V-03 | Ground Floor - Entrance Salon | R1-M.A.740-26/7 | Wall & ceiling paint | 70.0 | 151.5 | m2 | +116.4% **FLAG** |
| V-04 | First Floor - Hallways | R1-M.A.740-26/28 | Wall & ceiling paint | 80.0 | - | m2 | NOT MEASURABLE |

Every variance above exceeds the 5% reporting threshold or cannot be measured at all.

## Phase 2 - unpriced, pending specification

| Item | Why it is unpriced | Where |
|---|---|---|
| All lighting fixtures | BOQ note: "all lighting are not included ( will be submited The Price after selecting the type and model" | every room |
| All electrical work | BOQ note: "The Electrice work will be submit price after checking what is required" | every room |
| Sinks, mixers and sanitary ware | BOQ note: "The Sink and Mixer and other Sanitary will be priced after checking what kind of required" | both bathrooms, both powder rooms, guests bathroom |
| Master bedroom door-leaf panels | Items R1-M.A.740-26/31 and R1-M.A.740-26/33: "the panel for door leaf will be wall paper or fabric the price will be separate" | master bedroom |
| Headboard fabric | Item R1-M.A.740-26/32: "The Fabric supply By Client" | master bedroom |

Phase 2 elements are modelled with neutral `PH2_*` placeholder materials and are never presented as confirmed.

## Method and verification

- Source DWG is AutoCAD 2018 (AC1032), converted to DXF with LibreDWG. It contains BOTH floor plans in one modelspace.
- Scale verified before any modelling, per two independent routes (PDF vector lengths at 1:100; DWG DIMENSION entities). Both agree.
- Measured wall thicknesses: 240 mm external and partition, 150 mm and 90 mm secondary partitions.
- Blender scene: Metric, unit scale 1.0, length in metres. All builder APIs take millimetres and convert once at the boundary.
- Every modelled object carries a `boq_item` custom property; objects with no BOQ line carry `boq_item = NONE` and are listed in section 5 of each room reconciliation.
- Daylight: Jeddah 21.49 N, 39.19 E, 16:00 local, sun elevation 32.39 deg, azimuth 257.81 deg. Orientation ASSUMED (C-05).
- Renders: Cycles, AgX view transform, OpenImageDenoise, 1920x1080 draft and 3840x2160 final.

## Render budget - read this before asking for the other eight rooms

This machine has 4 CPU cores and no GPU. A single 1920x1080 interior frame takes about 2.5 minutes at a capped sample budget, and a 3840x2160 frame about 10. One room is 4 views, so roughly 10 minutes of draft and 40 minutes of final per room.

At nine rooms that is about 1.5 hours of draft and 6 hours of final rendering, before any re-render after QA. Frames are therefore time-boxed (Cycles `time_limit`) and the denoiser carries the remainder; that is a deliberate trade, not a defect. If photographic finals are wanted at pace, the renders should move to a GPU box.

## Self-QA

Every frame is checked automatically for mean luminance, lit fraction and blown highlights, and the run fails loudly on a black or blown frame. Issues found and fixed during this build:

- Luminaires were rotated 180 degrees and lit the ceiling - every frame came back black. Fixed; Blender lights already emit along local -Z.
- Camera 01 was standing inside the TV joinery. All eye points now keep 500 mm clear of every joinery face.
- Walls were centred on the room's inner faces, eating 120 mm off each dimension. Walls are now built outside the clear box, so the modelled clear size equals the measured 3435 x 4260 mm.
- The plan camera was above the ceiling slab and returned a flat grey rectangle. The ceiling is now hidden for plan views.
- Joinery was modelled as plain slabs. It is now built as framed leaves with mouldings, recessed panels, drawers, an upper tier and a set-back plinth, per the BOQ wording.
- Window glazing had been given the frosted shower-screen material. Now clear.
