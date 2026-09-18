#!/usr/bin/env python3
"""Generate the reconciliation logs, finish schedules and project SUMMARY.

Reads  logs/boq_parsed.json, logs/room_schedule.json, logs/<room>_objects.json
Writes logs/<room>_reconciliation.md, logs/<room>_finish_schedule.csv,
       logs/SUMMARY.md
Idempotent: rewrites every output on each run.
"""
import json, os, csv, datetime, collections

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
L = os.path.join(ROOT, 'logs')
BOQ = json.load(open(os.path.join(L, 'boq_parsed.json')))
ROOMS = {r['id']: r for r in json.load(open(os.path.join(L, 'room_schedule.json')))}
Q = BOQ['quotation']
TODAY = datetime.date.today().isoformat()
VAR_LIMIT = 5.0     # % - flag anything larger

ROOM_TITLES = {
 'entrance_salon':      'Ground Floor - Entrance Salon',
 'powder_room_aziza':   'First Floor - Powder Room, Mrs. Aziza',
 'bathroom_aziza':      'First Floor - Bathroom, Mrs. Aziza',
 'office':              'First Floor - Office',
 'powder_room_mohammed':'First Floor - Powder Room, Mr. Mohammed',
 'bathroom_mohammed':   'First Floor - Bathroom, Mr. Mohammed',
 'hallways':            'First Floor - Hallways',
 'kitchenette':         'First Floor - Kitchenette',
 'master_bedroom':      'First Floor - Master Bedroom',
}

# room key -> (space id or None, confidence, reasoning)
LOCATION = {
 'master_bedroom': ('FF-NW-BED', 'ASSUMED - medium',
   'This is the only first-floor bedroom with a wall measuring exactly 4260 mm, '
   'and it has two of them, facing each other. BOQ items 31 and 33 are both '
   'joinery runs of exactly W=4260 mm on facing walls, which is what joinery '
   'made to fill a wall looks like. '
   'This is suggestive, not conclusive: FF-NE-BED (4140x4950) and FF-SE-BED '
   '(4185x5265) have longer walls on which a 4260 mm run would also fit, with '
   'a gap, so neither can be ruled out. FF-SW-BED (3930x4170) can: no wall is '
   'long enough. '
   'Against this reading: once modelled, the 4260 mm runs do NOT fit '
   'FF-NW-BED either, because one 4260 wall carries a window and the other '
   'carries a 2630 mm recess (V-01, V-02). Either the joinery needs '
   're-measuring or this room assumption is wrong.'),
 'entrance_salon': ('GF-EAST', 'ASSUMED - low',
   'The main entrance door (1095 mm leaf, the largest on either drawing) opens '
   'into this space, and its 5425 mm clear wall can take the W=5000 mm cladding '
   'of BOQ item 1. BUT the paint quantity does not corroborate it - see V-03.'),
 'hallways': ('FF-STAIR', 'ASSUMED - low',
   'Stair core is the only delineated circulation. The hallways proper are not '
   'enclosed by walls on the drawings, so no boundary can be measured.'),
 'powder_room_aziza':    (None, 'NOT LOCATED', ''),
 'bathroom_aziza':       (None, 'NOT LOCATED', ''),
 'office':               (None, 'NOT LOCATED', ''),
 'powder_room_mohammed': (None, 'NOT LOCATED', ''),
 'bathroom_mohammed':    (None, 'NOT LOCATED', ''),
 'kitchenette':          (None, 'NOT LOCATED', ''),
}

CEILING = {'master_bedroom': (3000, 'BOQ items 31/33 specify H=3000 mm '
                                    'floor-to-ceiling joinery'),
           'entrance_salon': (3000, 'ASSUMED; BOQ item 1 specifies H=2800 mm '
                                    'cladding, so the ceiling is at least that'),
           'hallways':       (2800, 'ASSUMED from the 2800 mm joinery heights '
                                    'used throughout the BOQ')}

CONFLICTS = [
 ('C-01','CRITICAL','BOQ workbook',
  'The workbook holds three sheets. Only "nabati rest. (3)" (Quotation '
  f'{Q}, 20/07/2026, "Mr. Mohammed & Mrs. Aziza Villa - Jeddah") is this '
  'project. Sheet "nabati rest. (2)" is a different job - "Privet Villa - Al '
  'nuoras - Jeddah", quotation RF-635 R3-25, addressed to M/S Subair General '
  'Construction, SAR 255,535.75 incl. VAT. Sheet "nabati rest." is a 2024 '
  'Riyadh delivery note. Both are unrelated to this villa.',
  'Applied hierarchy rule 2: only sheet (3) governs. The other two are ignored. '
  'Confirm no one is pricing this villa off the SAR 255,535.75 figure.'),
 ('C-02','CRITICAL','Ground floor plan',
  'A red hatched zone stamped "NOT THE ACTUAL AS-BUILT" covers the ground-floor '
  'WC block (space GF-WC, 2230 x 3895 mm). The drawing\'s own author disclaims '
  'that area. The same note is present in the DWG (MTEXT on layer A_DIM).',
  'Geometry inside that hatch is treated as UNVERIFIED. Nothing is modelled '
  'there. A re-survey is required before that area can be priced or built.'),
 ('C-03','CRITICAL','All drawings',
  'The drawings carry NO room names. Verified in the source DWG: layers A_TEXT '
  'and ara-TEXT are empty, and all 64 MTEXT entities are dimension values or '
  'the disclaimer. Neither PDF carries a room label either.',
  'Room identity for all nine BOQ rooms is INFERENCE, not fact. Seven of the '
  'nine cannot be located at all. This is the single decision blocking the '
  'remaining models - see "Owner decisions required".'),
 ('C-04','HIGH','All drawings',
  'No sections, elevations or ceiling plans were supplied - only two 1:100 '
  'floor plans. Ceiling heights, bulkheads, sill and head heights are therefore '
  'not given anywhere.',
  'Ceiling heights DERIVED from the BOQ joinery heights (2800 / 2860 / 3000 mm '
  'floor-to-ceiling items). Sill 900 / head 2400 / door height 2100 mm are '
  'ASSUMED and tagged as such on every affected object.'),
 ('C-05','MEDIUM','All drawings',
  'No north arrow on either plan or in the DWG.',
  'Plan north ASSUMED to be world +Y for the Jeddah daylight study '
  '(21.49 N, 39.19 E, 16:00 local). Sun elevation 32.39 deg, azimuth 257.81 deg. '
  'If the true orientation differs, every daylight render must be re-run.'),
 ('C-06','MEDIUM','Reference render',
  'No designer\'s reference render was supplied. inputs/reference/ is empty.',
  'Aesthetic intent cannot be checked. Palette and finish character are driven '
  'solely by the BOQ material specifications.'),
 ('C-07','LOW','BOQ arithmetic',
  f'Item {Q}/3 (six wall shelves, G.F. Salon): quantity 1 x unit price SAR 2,200 '
  'but the line total reads SAR 2,000.',
  'Sub-total is understated by SAR 200. Sheet total SAR 170,127 excl. VAT.'),
 ('C-08','HIGH','Room register vs BOQ',
  'BOQ item 5 prices wall cladding and ceiling paint at a "G.F. Guests '
  'Bathroom". No guests bathroom appears in the nine-room register supplied.',
  'Treated as a TENTH priced room. It needs a location and a specification '
  'before it can be modelled.'),
 ('C-09','HIGH','BOQ vs as-built geometry',
  'The master-bedroom joinery cannot be installed as quoted in the room it '
  'must belong to. See variances V-01 and V-02.',
  'Modelled as-measured, with the shortfall carried as a variance. Either the '
  'joinery is re-measured or the room assumption (C-03) is wrong.'),
 ('C-10','LOW','BOQ terminology',
  '"doku paint" appears on four items (2, 3, 17). Not a standard finish name.',
  'Read as Duco (nitrocellulose lacquer) on MDF. Confirm before fabrication - '
  'the BOQ warns that any specification change is re-priced at 100%.'),
 ('C-11','LOW','BOQ terminology',
  'Marble named "Rossi Levanto" (items 14, 24) and "Verde Guatemale" (item 29).',
  'Read as Rosso Levanto and Verde Guatemala respectively. Modelled to those.'),
]

VARIANCES = [
 ('V-01', 'master_bedroom', f'{Q}/31', 'Wardrobe run width',
  4260, 2630, 'mm',
  'BOQ specifies W=4260 mm. The wardrobe recess in FF-NW-BED measures 2630 x '
  '480 mm. A 4260 mm run does not fit the recess.'),
 ('V-02', 'master_bedroom', f'{Q}/33', 'TV-area run width',
  4260, 3140, 'mm',
  'BOQ specifies W=4260 mm on the TV wall. The facing west wall is 4260 mm long '
  'but is interrupted by a 1000 mm window, leaving 3260 mm of wall in two '
  'pieces. 120 mm at the north end is held clear of the headboard, so 3140 mm '
  'is installable: 1450 + 1690.'),
 ('V-03', 'entrance_salon', f'{Q}/7', 'Wall & ceiling paint',
  70.0, 151.5, 'm2',
  'BOQ qty 70 m2. The assumed location GF-EAST (6060 x 9550 mm) gives '
  '93.7 m2 of wall at 3000 mm plus 57.9 m2 of ceiling = 151.5 m2. A 70 m2 '
  'quantity corresponds to a room of roughly 4.5 x 4.5 m. Either the room '
  'assumption is wrong or the quantity is partial.'),
 ('V-04', 'hallways', f'{Q}/28', 'Wall & ceiling paint',
  80.0, None, 'm2',
  'BOQ qty 80 m2. The hallways are not enclosed on the drawings, so no '
  'boundary can be measured and the quantity cannot be checked.'),
]

PHASE2 = [
 ('All lighting fixtures', 'BOQ note: "all lighting are not included ( will be '
  'submited The Price after selecting the type and model"', 'every room'),
 ('All electrical work', 'BOQ note: "The Electrice work will be submit price '
  'after checking what is required"', 'every room'),
 ('Sinks, mixers and sanitary ware', 'BOQ note: "The Sink and Mixer and other '
  'Sanitary will be priced after checking what kind of required"',
  'both bathrooms, both powder rooms, guests bathroom'),
 ('Master bedroom door-leaf panels', f'Items {Q}/31 and {Q}/33: "the panel for '
  'door leaf will be wall paper or fabric the price will be separate"',
  'master bedroom'),
 ('Headboard fabric', f'Item {Q}/32: "The Fabric supply By Client"',
  'master bedroom'),
]

DECISIONS = [
 ('D-01', 'Room identification',
  'Owner will mark up logs/space_key_GF.png and logs/space_key_FF.png to '
  'name each measured space. The remaining eight rooms are HELD until that '
  'mark-up arrives - nothing is modelled on a guessed location.'),
 ('D-02', 'Master bedroom joinery (items 31 and 33)',
  'Owner instructed that the joinery be re-measured to the room rather than '
  'the room re-assigned. Items 31 and 33 are modelled and reported at their '
  'installable lengths (2630 mm and 3140 mm), and a change note has been '
  'issued for the contractor to re-quote: '
  'logs/change_note_master_bedroom_joinery.md. Indicative delta '
  'SAR -8,922 excl. VAT.'),
]

def items_for(room):
    return [i for i in BOQ['items'] if i['room'] == room]

def write_reconciliation(room):
    its = items_for(room)
    sid, conf, why = LOCATION[room]
    sp = ROOMS.get(sid)
    ch = CEILING.get(room)
    vs = [v for v in VARIANCES if v[1] == room]
    out = [f'# Reconciliation - {ROOM_TITLES[room]}', '',
           f'Quotation {Q} - generated {TODAY}', '',
           '## 1. Location', '']
    if sp:
        out += [f'- Space ID: **{sid}**  (confidence: **{conf}**)',
                f'- Measured clear size: **{sp["size_mm"][0]} x {sp["size_mm"][1]} mm**',
                f'- Floor area: **{sp["area_m2"]:.2f} m2**, wall perimeter '
                f'**{sp["perimeter_m"]:.2f} m**',
                f'- Ceiling height: **{ch[0]} mm** - {ch[1]}' if ch else '',
                f'- Basis: {why}', '']
    else:
        out += [f'- **{conf}.** This room cannot be located on the as-built '
                'drawings.',
                '- The drawings carry no room names (conflict C-03) and nothing '
                'in the BOQ text identifies a position for this room.',
                '- **No model has been built.** Building one would mean '
                'inventing a location.', '']
    out += ['## 2. BOQ lines for this room', '',
            '| Ref | Description | Unit | Qty | Unit price | Total |',
            '|---|---|---|---|---|---|']
    for i in its:
        d = i['description'][:150] + ('...' if len(i['description']) > 150 else '')
        out.append(f'| {i["boq_item"]} | {d} | {i["unit"]} | {i["qty"]} | '
                   f'{i["unit_price"]:,.0f} | {i["total"]:,.0f} |')
    out += ['', f'**Room sub-total: SAR {sum(i["total"] or 0 for i in its):,.2f}**', '']
    out += ['## 3. Quantity variances (drawing vs BOQ)', '']
    if vs:
        out += ['| Ref | BOQ line | Item | BOQ qty | Measured | Unit | Variance | Note |',
                '|---|---|---|---|---|---|---|---|']
        for vid, _, ref, label, boq, meas, unit, note in vs:
            if meas is None:
                var = 'NOT MEASURABLE'
            else:
                pct = (meas - boq) / boq * 100.0
                var = f'{pct:+.1f}%' + ('  **FLAG**' if abs(pct) > VAR_LIMIT else '')
            out.append(f'| {vid} | {ref} | {label} | {boq} | '
                       f'{meas if meas is not None else "-"} | {unit} | {var} | {note} |')
    else:
        out += ['No quantity in this room can be checked against geometry, '
                'because the room is not located (C-03).']
    out += ['', '## 4. BOQ items with no location', '']
    if sp:
        out += ['All lines above are assigned to the space named in section 1, '
                'subject to that assumption being confirmed.']
    else:
        out += [f'All {len(its)} lines listed above have **no location**.']
    out += ['', '## 5. Render elements with no BOQ line', '']
    op = os.path.join(L, f'{room}_objects.json')
    if os.path.exists(op):
        objs = json.load(open(op))
        none = [o for o in objs if o['boq_item'] in ('NONE', f'{Q}/NONE')]
        if none:
            out += ['| Object | Material | Status | Why |', '|---|---|---|---|']
            for o in none:
                out.append(f'| {o["object"]} | {o["material"]} | {o["status"]} | '
                           f'{o["note"] or "no BOQ line covers this element"} |')
        else:
            out += ['None - every modelled element carries a BOQ reference.']
    else:
        out += ['Not applicable - no model built for this room.']
    out += ['', '## 6. Phase 2 (unpriced) in this room', '']
    rel = [p for p in PHASE2 if room.replace('_',' ') in p[2] or p[2] == 'every room']
    if rel:
        for n, why_, _ in rel: out.append(f'- **{n}** - {why_}')
    else:
        out.append('None recorded.')
    out.append('')
    p = os.path.join(L, f'{room}_reconciliation.md')
    open(p,'w').write('\n'.join(x for x in out if x is not None))
    return p

ASSEMBLY_SUFFIXES = ('_Carcass', '_Plinth', '_Leaf', '_Dwr', '_Upr',
                     '_RailB', '_RailT', '_RailL', '_RailR', '_Panel')

def assembly_of(name):
    """Roll a cabinet_run part name back to its assembly, so the schedule lists
    joinery runs rather than every individual rail."""
    for tag in ('_Carcass', '_Plinth', '_Leaf', '_Dwr', '_Upr'):
        i = name.find(tag)
        if i > 0:
            base = name[:i]
            return base.replace('PH2_', 'JOI_') if base.startswith('PH2_') else base
    return name

def write_finish_schedule(room):
    its = {i['boq_item']: i for i in items_for(room)}
    op = os.path.join(L, f'{room}_objects.json')
    rows = []
    if os.path.exists(op):
        objs = json.load(open(op))
        groups = collections.OrderedDict()
        for o in objs:
            key = (assembly_of(o['object']), o['boq_item'])
            groups.setdefault(key, []).append(o)
        for (asm, ref), parts in groups.items():
            boq = its.get(ref)
            mats = sorted({p['material'] for p in parts if p['material']})
            statuses = {p['status'] for p in parts if p['status']}
            status = ('Phase 2' if statuses == {'Phase 2'} else
                      'Confirmed + Phase 2 panels' if 'Phase 2' in statuses and
                      'Confirmed' in statuses else
                      ('Assumed' if 'Assumed' in statuses else
                       (sorted(statuses)[0] if statuses else 'Confirmed')))
            bw = next((p.get('boq_width_mm') or p.get('boq_length_mm')
                       for p in parts
                       if p.get('boq_width_mm') or p.get('boq_length_mm')), None)
            mw = next((p.get('modelled_width_mm') for p in parts
                       if p.get('modelled_width_mm')), None)
            if mw is None:
                # governing run length = largest plan dimension in the assembly
                mw = max((max(p['dims_mm'][0], p['dims_mm'][1]) for p in parts),
                         default=0)
            if bw:
                qm, qb, var = f'{mw} mm', f'{bw} mm', f'{(mw-bw)/bw*100:+.1f}%'
            elif parts[0]['type'] == 'LIGHT':
                qm, qb, var = f'{len(parts)} no.', (boq['qty'] if boq else ''), ''
            else:
                d = parts[0]['dims_mm']
                qm = f'{d[0]}x{d[1]}x{d[2]} mm'
                qb, var = (boq['qty'] if boq else ''), ''
            rows.append({'object': asm, 'material': ' + '.join(mats),
                         'boq_ref': ref, 'qty_modelled': qm, 'qty_boq': qb,
                         'variance': var, 'status': status})
    else:
        for ref, i in sorted(its.items()):
            rows.append({'object': 'NOT MODELLED - room not located (C-03)',
                         'material': '', 'boq_ref': ref, 'qty_modelled': '',
                         'qty_boq': i['qty'], 'variance': '',
                         'status': 'Blocked - awaiting room identification'})
    # A single BOQ line can be split across several assemblies (e.g. a run
    # interrupted by a window). Report each piece, then one combined row, so the
    # variance is measured against the whole line and not against each fragment.
    bymm = collections.defaultdict(list)
    for r in rows:
        if r['variance'] and r['qty_modelled'].endswith(' mm'):
            bymm[r['boq_ref']].append(r)
    out = []
    for r in rows:
        if len(bymm.get(r['boq_ref'], [])) > 1:
            r = dict(r, variance='see combined row')
        out.append(r)
    for ref, grp in bymm.items():
        if len(grp) < 2: continue
        tot = sum(int(g['qty_modelled'].split()[0]) for g in grp)
        bw  = int(grp[0]['qty_boq'].split()[0])
        out.append({'object': f'-- combined for {ref} ({len(grp)} pieces)',
                    'material': grp[0]['material'], 'boq_ref': ref,
                    'qty_modelled': f'{tot} mm', 'qty_boq': f'{bw} mm',
                    'variance': f'{(tot-bw)/bw*100:+.1f}%',
                    'status': grp[0]['status']})
    p = os.path.join(L, f'{room}_finish_schedule.csv')
    with open(p, 'w', newline='') as f:
        w = csv.DictWriter(f, fieldnames=['object','material','boq_ref',
                                          'qty_modelled','qty_boq','variance','status'])
        w.writeheader(); w.writerows(out)
    return p

def write_summary():
    built  = [r for r in ROOM_TITLES
              if os.path.exists(os.path.join(L, f'{r}_objects.json'))]
    placed = [r for r in ROOM_TITLES if LOCATION[r][0]]
    unloc  = [r for r in ROOM_TITLES if not LOCATION[r][0]]
    total  = sum(i['total'] or 0 for i in BOQ['items'])
    o = []
    A = o.append
    A('# Mr. Mohammed & Mrs. Aziza Villa, Jeddah - 3D room package')
    A(f'\nQuotation {Q} (20/07/2026) - report generated {TODAY}\n')
    A('## BLUF\n')
    A(f'**{len(built)} of 9 rooms modelled. The other 8 are on hold: the '
      'as-built drawings contain no room names, so their locations are '
      'unknown until the owner marks up the space key (decision D-01).**\n')
    A('- The drawings are dimensionally sound. Scale was verified twice: the '
      'PDFs reproduce six independent dimensions each to within 3.3 mm at '
      '1:100, and the DWG\'s own DIMENSION entities return nine values that '
      'match the printed text exactly. Geometry is trustworthy.')
    A('- What is missing is **identity**, not measurement. The DWG\'s text '
      'layers (A_TEXT, ara-TEXT) are empty; all 64 MTEXT entities are dimension '
      'values. No room on either floor is labelled.')
    A('- The **master bedroom** is the one room with a usable clue: BOQ items 31 '
      'and 33 are both exactly 4260 mm wide, on facing walls, and exactly one '
      'bedroom has a pair of facing 4260 mm walls. That is suggestive, not '
      'proof - two other bedrooms have longer walls that would also take the '
      'run. It has been modelled on that basis and tagged ASSUMED throughout.')
    A('- Modelling it surfaced a harder problem: **the quoted joinery does not '
      'fit that room either.** One 4260 mm wall carries a window, the other '
      'carries a 2630 mm recess (V-01, V-02). So either the joinery needs '
      're-measuring before fabrication, or the room assumption is wrong. Both '
      'are worth knowing now rather than on site.')
    A('- **A stale quotation for a different villa (SAR 255,535.75) is sitting '
      'in the same workbook.** Make sure nobody is pricing this job off it.\n')
    A('## Rooms completed and outstanding\n')
    A('| Room | BOQ value (SAR) | Location | Status |')
    A('|---|---|---|---|')
    for r, t in ROOM_TITLES.items():
        v = sum(i['total'] or 0 for i in items_for(r))
        sid, conf, _ = LOCATION[r]
        st = ('Modelled + rendered' if r in built else
              ('Located (low confidence), on hold under D-01' if sid else
               '**HELD under D-01** - awaiting the owner\'s space-key mark-up'))
        A(f'| {t} | {v:,.0f} | {sid or "-"} ({conf}) | {st} |')
    A(f'| **Total** | **{total:,.0f}** | | |\n')
    A('## Owner decisions required\n')
    A('**1. Confirm which physical room is which.** This is the one decision '
      'blocking 7 of the 9 models. The measured spaces are:\n')
    A('| Space | Floor | Measured clear size (mm) | Area (m2) | What is in it |')
    A('|---|---|---|---|---|')
    for rid, r in ROOMS.items():
        A(f'| {rid} | {r["floor"]} | {r["size_mm"][0]} x {r["size_mm"][1]} | '
          f'{r["area_m2"]:.2f} | {r["kind"]} |')
    A('\n**2. Confirm or correct the master bedroom joinery** - it is quoted at '
      '4260 mm but the room cannot take it (V-01, V-02).')
    A('\n**3. Release a re-survey of the ground-floor WC block** stamped '
      '"NOT THE ACTUAL AS-BUILT" (C-02).')
    A('\n**4. Identify the "G.F. Guests Bathroom"** priced in item 5 but absent '
      'from the nine-room register (C-08).\n')
    A('## Deliverables in this package\n')
    A('| File | What it is |')
    A('|---|---|')
    rows = [
      ('logs/space_key_GF.png, logs/space_key_FF.png',
       'The as-built plans with every measured space labelled. **Mark these '
       'up to unblock the remaining eight rooms.**'),
      ('logs/change_note_master_bedroom_joinery.md',
       'Re-measure change note for items 31 and 33, for the contractor to '
       're-quote (decision D-02).'),
      ('logs/<room>_reconciliation.md',
       'Per room: location and its basis, every BOQ line, quantity '
       'variances, items with no location, modelled elements with no BOQ '
       'line, and Phase 2 scope.'),
      ('logs/<room>_finish_schedule.csv',
       'object / material / BOQ ref / qty modelled / qty BOQ / variance / '
       'status, generated from the model rather than retyped.'),
      ('logs/master_bedroom_qa.md',
       'Self-QA: automated per-frame checks plus what was found, fixed and '
       'deliberately left.'),
      ('logs/room_schedule.json',
       'Every measured space with its bounds, area and how much of each '
       'side is backed by a real wall.'),
      ('logs/asbuilt_geometry.json',
       'Walls, doors, windows, stairs and fixtures extracted from the DWG, '
       'in millimetres.'),
      ('logs/boq_parsed.csv, logs/boq_parsed.json',
       'The governing BOQ sheet parsed to 34 line items across 9 rooms, '
       'totalling SAR 170,127 excl. VAT.'),
      ('scenes/master_bedroom.blend',
       'The room model. Every object carries a boq_item property.'),
      ('renders/master_bedroom_cam01..03.png, _plan.png',
       'Three eye-level views at 1.60 m plus the top-down plan.'),
    ]
    for f, w in rows:
        A(f'| `{f}` | {w} |')
    A('')
    A('## Owner decisions taken\n')
    A('| Ref | Subject | Decision |')
    A('|---|---|---|')
    for did, subj, txt in DECISIONS:
        A(f'| {did} | {subj} | {txt} |')
    A('')
    A('## Top conflicts\n')
    A('| Ref | Severity | Source | Conflict | Resolution applied |')
    A('|---|---|---|---|---|')
    for cid, sev, src, what, res in CONFLICTS:
        A(f'| {cid} | {sev} | {src} | {what} | {res} |')
    A('\n## Quantity variances affecting cost\n')
    A('| Ref | Room | BOQ line | Item | BOQ qty | Measured | Unit | Variance |')
    A('|---|---|---|---|---|---|---|---|')
    for vid, room, ref, label, boq, meas, unit, note in VARIANCES:
        if meas is None: var = 'NOT MEASURABLE'
        else:
            pct = (meas-boq)/boq*100.0
            var = f'{pct:+.1f}%' + (' **FLAG**' if abs(pct) > VAR_LIMIT else '')
        A(f'| {vid} | {ROOM_TITLES[room]} | {ref} | {label} | {boq} | '
          f'{meas if meas is not None else "-"} | {unit} | {var} |')
    A('\nEvery variance above exceeds the 5% reporting threshold or cannot be '
      'measured at all.\n')
    A('## Phase 2 - unpriced, pending specification\n')
    A('| Item | Why it is unpriced | Where |')
    A('|---|---|---|')
    for n, why, where in PHASE2:
        A(f'| {n} | {why} | {where} |')
    A('\nPhase 2 elements are modelled with neutral `PH2_*` placeholder '
      'materials and are never presented as confirmed.\n')
    A('## Method and verification\n')
    A('- Source DWG is AutoCAD 2018 (AC1032), converted to DXF with LibreDWG. '
      'It contains BOTH floor plans in one modelspace.')
    A('- Scale verified before any modelling, per two independent routes '
      '(PDF vector lengths at 1:100; DWG DIMENSION entities). Both agree.')
    A('- Measured wall thicknesses: 240 mm external and partition, 150 mm and '
      '90 mm secondary partitions.')
    A('- Blender scene: Metric, unit scale 1.0, length in metres. All builder '
      'APIs take millimetres and convert once at the boundary.')
    A('- Every modelled object carries a `boq_item` custom property; objects '
      'with no BOQ line carry `boq_item = NONE` and are listed in section 5 of '
      'each room reconciliation.')
    A('- Daylight: Jeddah 21.49 N, 39.19 E, 16:00 local, sun elevation '
      '32.39 deg, azimuth 257.81 deg. Orientation ASSUMED (C-05).')
    A('- Renders: Cycles, AgX view transform, OpenImageDenoise, 1920x1080 '
      'draft and 3840x2160 final.\n')
    A('## Render budget - read this before asking for the other eight rooms\n')
    A('This machine has 4 CPU cores and no GPU. A single 1920x1080 interior '
      'frame takes about 2.5 minutes at a capped sample budget, and a '
      '3840x2160 frame about 10. One room is 4 views, so roughly 10 minutes of '
      'draft and 40 minutes of final per room.\n')
    A('At nine rooms that is about 1.5 hours of draft and 6 hours of final '
      'rendering, before any re-render after QA. Frames are therefore '
      'time-boxed (Cycles `time_limit`) and the denoiser carries the '
      'remainder; that is a deliberate trade, not a defect. If photographic '
      'finals are wanted at pace, the renders should move to a GPU box.\n')
    A('## Self-QA\n')
    A('Every frame is checked automatically for mean luminance, lit fraction '
      'and blown highlights, and the run fails loudly on a black or blown '
      'frame. Issues found and fixed during this build:\n')
    A('- Luminaires were rotated 180 degrees and lit the ceiling - every frame '
      'came back black. Fixed; Blender lights already emit along local -Z.')
    A('- Camera 01 was standing inside the TV joinery. All eye points now keep '
      '500 mm clear of every joinery face.')
    A('- Walls were centred on the room\'s inner faces, eating 120 mm off each '
      'dimension. Walls are now built outside the clear box, so the modelled '
      'clear size equals the measured 3435 x 4260 mm.')
    A('- The plan camera was above the ceiling slab and returned a flat grey '
      'rectangle. The ceiling is now hidden for plan views.')
    A('- Joinery was modelled as plain slabs. It is now built as framed leaves '
      'with mouldings, recessed panels, drawers, an upper tier and a set-back '
      'plinth, per the BOQ wording.')
    A('- Window glazing had been given the frosted shower-screen material. '
      'Now clear.\n')
    p = os.path.join(L, 'SUMMARY.md')
    open(p,'w').write('\n'.join(o))
    return p

def main():
    for room in ROOM_TITLES:
        write_reconciliation(room)
        write_finish_schedule(room)
    print('wrote', write_summary())
    print(f'wrote {len(ROOM_TITLES)} reconciliation logs + finish schedules')

if __name__ == '__main__':
    main()
