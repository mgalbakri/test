# Mr. Mohammed & Mrs. Aziza Villa, Jeddah — 3D room package

Start with **[logs/SUMMARY.md](logs/SUMMARY.md)**. It is BLUF-first and carries
the conflict register, the cost-affecting variances and the decisions needed
from the owner.

## The one thing blocking this package

The as-built drawings carry **no room names**. Verified in the source DWG: the
`A_TEXT` and `ara-TEXT` layers are empty, and all 64 MTEXT entities are
dimension values or the "NOT THE ACTUAL AS-BUILT" disclaimer. Neither PDF
carries a room label either.

Geometry is sound and fully measured. Identity is not. Seven of the nine priced
rooms therefore cannot be placed on the drawings.

**Mark up [logs/space_key_GF.png](logs/space_key_GF.png) and
[logs/space_key_FF.png](logs/space_key_FF.png)** — every measured space is
labelled with an ID, its clear size and its area. Naming those spaces unblocks
the remaining eight models.

## Layout

| Path | What it is |
|---|---|
| `inputs/drawings/` | As-built DWG (AutoCAD 2018), the DXF converted from it, and the two 1:100 PDF plans |
| `inputs/boq/` | Bill of Quantities workbook |
| `inputs/reference/` | **Empty — no designer's render was supplied** (conflict C-06) |
| `scenes/<room>.blend` | One Blender file per room |
| `scenes/scripts/` | Every script, re-runnable and idempotent |
| `renders/` | `<room>_cam01..n.png` and `<room>_plan.png` |
| `logs/` | Reconciliations, finish schedules, SUMMARY, space keys, extracted geometry |

## Rebuilding from scratch

```bash
python3 scenes/scripts/parse_boq.py        # BOQ  -> logs/boq_parsed.{csv,json}
python3 scenes/scripts/extract_dxf.py      # DWG  -> logs/asbuilt_geometry.json  (verifies units)
python3 scenes/scripts/extract_walls.py    # PDFs -> logs/plan_linework.json     (verifies 1:100 scale)
python3 scenes/scripts/rooms.py            # room schedule, verified against the wall grid
python3 scenes/scripts/plot_space_key.py   # annotated space keys

blender -b --factory-startup -P scenes/scripts/build_master_bedroom.py
blender -b scenes/master_bedroom.blend -P scenes/scripts/render_room.py -- master_bedroom draft 150
blender -b scenes/master_bedroom.blend -P scenes/scripts/render_room.py -- master_bedroom final 600

python3 scenes/scripts/generate_logs.py    # reconciliations, finish schedules, SUMMARY
```

Every build script clears and rebuilds its scene, so re-running is safe.

## Conventions

- **Metric only.** Blender scenes are Metric, unit scale 1.0, length in metres.
  Every builder API takes **millimetres** and converts once, at the boundary.
  All reporting is in millimetres.
- **No invented dimensions.** Anything not measurable from the drawings is
  derived from another drawing or from the BOQ; if it is still unknown it is
  tagged `ASSUMED` both in the logs and in the object's custom properties.
- **BOQ traceability.** Every object carries a `boq_item` custom property.
  Objects with no BOQ line carry `boq_item = NONE` and are listed in section 5
  of that room's reconciliation.
- **Phase 2** (unpriced) items use neutral `PH2_*` placeholder materials and are
  never presented as confirmed.
- **Source hierarchy.** As-built drawings govern geometry; the BOQ governs
  materials and quantities; the reference render would govern aesthetic intent
  only. Conflicts are logged, never silently resolved.
