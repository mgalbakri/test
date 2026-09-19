#!/usr/bin/env python3
"""Material schedule for the three priced bathrooms.

Sources, per the project hierarchy:
  - Materials, finishes and quantities: BOQ R1-M.A.740-26 (sheet "nabati rest. (3)")
  - Geometry: as-built DWG
  - Aesthetic intent: no reference render was supplied (conflict C-06)

Outputs logs/bathroom_material_schedule.{md,csv}. Idempotent.
"""
import json, os, csv, datetime

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
L = os.path.join(ROOT, 'logs')
BOQ = json.load(open(os.path.join(L, 'boq_parsed.json')))
ROOMS = json.load(open(os.path.join(L, 'room_schedule.json')))
Q = BOQ['quotation']
TODAY = datetime.date.today().isoformat()

# material key -> (spec as written, what is missing, how it is modelled)
MATERIALS = [
 ('POR_Floor', 'Porcelain floor tile',
  f'{Q}/11, /23',
  'Porcelain, floor. "Installation of porcelain for flooring and wall @ shower area."',
  'Size, colour, finish, slip rating, manufacturer, grout colour. Nothing is given.',
  'Modelled 600 x 1200 mm ASSUMED, light warm grey, satin. Real-world UV.'),
 ('POR_Wall_Shower', 'Porcelain wall tile, shower area',
  f'{Q}/11, /23',
  'Porcelain, walls, shower area only.',
  'Size, colour, finish, extent (height, wrap), trim/edge detail.',
  'Modelled 600 x 1200 mm ASSUMED, matching floor, full height in shower zone.'),
 ('MRB_RossoLevanto', 'Marble vanity top + skirting',
  f'{Q}/14, /24',
  'Rosso Levanto marble (BOQ: "Rossi Levanto"), top W1100 x D500 x 20 mm thk, '
  'with marble skirting. Mrs Aziza skirting L1100 x H150 x 20 mm thk.',
  'Mr Mohammed skirting is undimensioned. Edge profile, finish (polished/honed), '
  'basin cut-out type (undermount / vessel / countertop), tap-hole drilling.',
  'Dark oxblood ground with white veining, polished, coat 0.6. Vein scale set '
  'to the 1100 mm slab so figure reads at real size.'),
 ('WD_Beech_Veneer', 'MDF with beech veneer, stain finish',
  f'{Q}/12, /13, /26',
  '3-leaf cabinet W1700 x H2800 x D500 (Mrs Aziza only). '
  'Vanity cabinet W1100 x H850 x D500 (both bathrooms).',
  'Stain colour/reference, sheen, whether carcass is moisture-resistant (W/R) - '
  'the bathroom cabinets say "MDF", the joinery elsewhere says "MDF W/R". '
  'Ironmongery, soft-close, internal fit-out.',
  'Quiet low-contrast beech figure, roughness 0.32, light coat. Deliberately '
  'subtle: grain direction is object-space, so a strong figure runs wrong on '
  'vertical parts.'),
 ('GLS_Frosted_10mm', 'Frosted glass shower door and partition',
  f'{Q}/15, /25',
  'Frosted glass (BOQ: "Forsted Galss"), 10 mm thk, W1600 x H1500.',
  'H1500 is low for a shower screen - see risk R-04. Hinge/track type, hardware '
  'finish, edge polish, toughening/safety marking.',
  'Transmission 1.0, roughness 0.38, IOR 1.52.'),
 ('PNT_Wall_Ceiling', 'Wall and ceiling paint',
  f'{Q}/16, /27',
  'Supply and apply, wall and ceiling. LS SAR 850 per bathroom.',
  'Paint type, sheen, colour, number of coats, and whether a bathroom-grade '
  '(anti-mould, moisture-resistant) product is intended. Nothing is given.',
  'Off-white matt, roughness 0.62.'),
 ('CEM_Board', 'Cement board cladding + base paint',
  f'{Q}/5',
  'Wall cladding in cement board with base paint and ceiling paint, '
  'G.F. Guests Bathroom only. LS SAR 2,000.',
  'No porcelain at all in this room - it is a painted bathroom. Confirm '
  'intended. Board thickness, fixing, jointing, finish coat.',
  'Not modelled - room not located (C-03).'),
 ('INS_Tanking', 'Waterproofing / "new insulation"',
  f'{Q}/10, /22',
  'Included within the strip-out lines: "included the making new insulation".',
  'Membrane type, upstand height, falls to gully, junction detailing, testing. '
  'This is the single most consequential unspecified item in a wet room.',
  'Not modelled (concealed).'),
]

RISKS = [
 ('R-01', 'HIGH', f'{Q}/11 and /23 - porcelain supply may be excluded',
  'Every other line in this BOQ reads "Supply and installation". Items 11 and '
  '23 read "Installation of porcelain for flooring and wall @ shower area" - '
  'installation only, no supply. On a plain reading the tile itself is not in '
  'the SAR 3,250, and the cost is open until a tile is selected.',
  'Get this confirmed in writing before signing. At Jeddah rates a mid-range '
  'porcelain over two bathrooms is a four-figure sum in its own right.'),
 ('R-02', 'HIGH', f'{Q}/10 vs /22 - possible double count of SAR 2,500',
  'Item 10 prices strip-out "in tow bathroom" (two bathrooms) at SAR 2,500 '
  'under Mrs Aziza. Item 22 prices the same strip-out again, singular, under '
  'Mr Mohammed, at SAR 2,500. Either item 10 already covers both rooms and '
  'item 22 is a duplicate, or item 10\'s "two bathrooms" means something else '
  '(e.g. bathroom plus powder room).',
  'Ask the contractor which rooms item 10 covers. If it covers both bathrooms, '
  'SAR 2,500 comes out.'),
 ('R-03', 'HIGH', 'Walls stripped throughout, re-tiled only at the shower',
  'Item 10 removes "the porcelain floors and walls" across the bathroom. Item '
  '11 reinstates porcelain "for flooring and wall @ shower area" only. The '
  'remaining wall area is covered by SAR 850 of paint (item 16 / 27).',
  'Confirm this is the design intent: painted plaster rather than tile on the '
  'non-shower walls of a wet room. If tiling is wanted wall-to-wall, both the '
  'tile quantity and the SAR 3,250 installation figure need re-quoting.'),
 ('R-04', 'MEDIUM', f'{Q}/15 and /25 - shower screen height 1500 mm',
  'The screen is specified W1600 x H1500. A shower enclosure is normally '
  '1800-2000 mm high. At 1500 mm the screen finishes around chest height and '
  'water will carry over the top.',
  'Confirm whether 1500 is a typo for 1900/2000, or whether this is '
  'deliberately a half-height partition to an open wet area.'),
 ('R-05', 'MEDIUM', 'Sanitary ware is entirely unpriced',
  'BOQ note: "The Sink and Mixer and other Sanitary will be priced after '
  'checking what kind of required". So WC, basin, all mixers, the shower valve '
  'and head, wastes, traps and accessories are outside the SAR 39,370 the two '
  'bathrooms currently carry.',
  'Specify these before the tiling is set out - basin and WC positions drive '
  'the tile setting-out and the vanity cut-out.'),
 ('R-06', 'LOW', 'The two bathrooms are specified asymmetrically',
  'Mrs Aziza gets a 3-leaf beech cabinet W1700 x H2800 (item 12, SAR 4,760); '
  'Mr Mohammed has no equivalent. Her marble is SAR 5,650 with a dimensioned '
  'skirting; his is SAR 5,260 with the skirting undimensioned.',
  'Confirm the asymmetry is intended rather than an omission.'),
 ('R-07', 'LOW', 'Carcass may not be moisture-resistant',
  'Bathroom cabinets (items 12, 13, 26) are specified "Made of MDF with Beech '
  'veneer". Joinery elsewhere in the same BOQ is specified "MDF W/R" '
  '(water-resistant). The bathrooms are where W/R matters most.',
  'Confirm W/R carcass for anything in a wet room.'),
 ('R-09', 'MEDIUM', 'Only one first-floor bathroom can take Mrs Aziza\'s package',
  'Testing the specified fittings against the measured spaces: the 3-leaf '
  'cabinet (1700 mm) plus a shower only fits FF-BATH-W (2195 x 1755) on the '
  'first floor, and only with the cabinet turned onto an end wall, leaving '
  'about 855 mm of circulation. FF-BATH-N and FF-BATH-C cannot take the 1700 '
  'mm cabinet at all alongside a shower; FF-BATH-S cannot take the package in '
  'any arrangement. Three of the four are under 1600 mm on their short '
  'dimension.',
  'Either Mrs Aziza\'s bathroom is FF-BATH-W, or the cabinet and shower tray '
  'need re-sizing. Worth settling at the same time as the space-key mark-up.'),
 ('R-10', 'MEDIUM', 'Shower tray size is not specified anywhere',
  'The BOQ gives the glass screen (1600 x 1500) but never the tray or the '
  'shower footprint. A 900 mm tray depth has been ASSUMED for the fit testing '
  'above. Nothing in the BOQ supplies a tray at all - it falls under the '
  'unpriced sanitary ware (R-05).',
  'Specify the tray (or a formed, tanked floor gully) before the fit above can '
  'be relied on. A shallower tray changes every verdict in that table.'),
 ('R-08', 'LOW', 'Terminology to correct on the order',
  '"Rossi Levanto" should read Rosso Levanto. "Forsted Galss" should read '
  'frosted glass. "tow bathroom" should read two bathrooms.',
  'Cosmetic, but worth fixing so the order matches the quarry name.'),
]

MIN_CIRC = 700          # mm - minimum clear circulation in front of fittings
SHOWER = (1600, 900)    # BOQ screen width x assumed tray depth
CABINET = (1700, 500)   # BOQ item 12
VANITY = (1100, 500)    # BOQ items 13 / 26

def _fit(along, across, cabinet):
    """Best circulation achievable in a room `along` x `across`.

    Two arrangements are tried:
      OPPOSITE - shower on one long wall, the cabinet/vanity facing it. Needs
                 one wall to take both widths; circulation is what is left
                 across the room once both depths are taken.
      ADJACENT - shower on one wall, the cabinet turned onto an end wall. Uses
                 the room far better, so this is usually the real arrangement.
    Returns (circulation_mm, arrangement) or None if neither can be built.
    """
    other = CABINET if cabinet else VANITY
    best = None
    # opposite walls
    if SHOWER[0] <= along and other[0] <= along:
        c = across - SHOWER[1] - other[1]
        best = max(best or (-1e9, ''), (c, 'facing'))
    # adjacent: the cabinet turns onto an end wall
    if SHOWER[0] + other[1] <= along and other[0] <= across:
        c = across - SHOWER[1]
        best = max(best or (-1e9, ''), (c, 'cabinet on an end wall'))
    return best

def fit_verdict(w, d, cabinet):
    opts = [_fit(w, d, cabinet), _fit(d, w, cabinet)]
    opts = [o for o in opts if o is not None]
    if not opts:
        return '**No** - no wall long enough'
    circ, how = max(opts)
    if circ < MIN_CIRC - 100:
        return f'**No** - {circ:.0f} mm circulation at best'
    if circ < MIN_CIRC:
        return f'Very tight - {circ:.0f} mm ({how})'
    if circ < MIN_CIRC + 300:
        return f'Tight - {circ:.0f} mm ({how})'
    return f'Yes - {circ:.0f} mm ({how})'

def items_for(room):
    return [i for i in BOQ['items'] if i['room'] == room]

def main():
    az = items_for('bathroom_aziza')
    mo = items_for('bathroom_mohammed')
    gf = [i for i in BOQ['items'] if i['boq_item'] == f'{Q}/5']
    o = []; A = o.append
    A('# Bathroom material schedule')
    A('')
    A(f'Quotation {Q} - generated {TODAY}')
    A('')
    A('## BLUF')
    A('')
    A('**Almost nothing about the bathroom finishes is actually specified.** The '
      'BOQ names a marble and a veneer and says "porcelain" - no size, no '
      'colour, no finish, no manufacturer for any tile, and no paint type. '
      'Three things need answering before anyone orders:')
    A('')
    A('1. **The porcelain may not be in the price.** Items 11 and 23 say '
      '*"Installation of"*, not *"Supply and installation"* like every other '
      'line (R-01).')
    A('2. **SAR 2,500 may be double-counted** on strip-out between items 10 and '
      '22 (R-02).')
    A('3. **The walls are stripped but only the shower area is re-tiled** - the '
      'rest gets SAR 850 of paint (R-03).')
    A('')
    A('And one that affects where the rooms go: **on the first floor only '
      'FF-BATH-W is big enough for Mrs Aziza\'s specified package**, and only '
      'just. Three of the four first-floor bathrooms are under 1600 mm on '
      'their short dimension (R-09).')
    A('')
    A(f'Priced value: Mrs Aziza SAR {sum(i["total"] or 0 for i in az):,.0f}, '
      f'Mr Mohammed SAR {sum(i["total"] or 0 for i in mo):,.0f}, '
      'G.F. Guests Bathroom SAR 2,000 (cladding and paint only). '
      'All sanitary ware is unpriced (R-05).')
    A('')
    A('## Materials as specified')
    A('')
    A('| Material | BOQ ref | Specified | Not specified | How it is modelled |')
    A('|---|---|---|---|---|')
    for key, name, ref, spec, missing, modelled in MATERIALS:
        A(f'| **{name}**<br>`{key}` | {ref} | {spec} | {missing} | {modelled} |')
    A('')
    A('## Bathroom by bathroom')
    A('')
    for title, items, note in (
        ('Mrs Aziza', az, 'The only bathroom with the 3-leaf cabinet (item 12).'),
        ('Mr Mohammed', mo, 'No 3-leaf cabinet; otherwise the same package.'),
        ('G.F. Guests Bathroom', gf,
         'Priced inside the Entrance Salon section, and absent from the '
         'nine-room register (conflict C-08). Cement board and paint only - '
         'no porcelain, no marble, no joinery, no glass.')):
        A(f'### {title}')
        A('')
        A(f'{note}')
        A('')
        A('| Ref | Item | Unit | Qty | SAR |')
        A('|---|---|---|---|---|')
        for i in items:
            d = i['description']
            d = d[:130] + ('...' if len(d) > 130 else '')
            A(f'| {i["boq_item"]} | {d} | {i["unit"]} | {i["qty"]} | '
              f'{i["total"]:,.0f} |')
        A(f'| | **Total** | | | **{sum(i["total"] or 0 for i in items):,.0f}** |')
        A('')
    A('## Risks and questions')
    A('')
    A('| Ref | Severity | Issue | Detail | What to do |')
    A('|---|---|---|---|---|')
    for rid, sev, issue, detail, action in RISKS:
        A(f'| {rid} | {sev} | {issue} | {detail} | {action} |')
    A('')
    A('## Which space is which')
    A('')
    A('The bathrooms are still unlocated (conflict C-03, decision D-01). The '
      'BOQ joinery does narrow it down, because the full package has to fit:')
    A('')
    A('| Space | Clear (mm) | Area | Mrs Aziza package | Mr Mohammed package |')
    A('|---|---|---|---|---|')
    for r in sorted((r for r in ROOMS if r['kind'] in ('bathroom', 'wc')),
                    key=lambda r: -r['area_m2']):
        w, d = r['size_mm']
        A(f'| {r["id"]} | {w} x {d} | {r["area_m2"]:.2f} m2 | '
          f'{fit_verdict(w, d, cabinet=True)} | '
          f'{fit_verdict(w, d, cabinet=False)} |')
    A('')
    A('Test applied: the shower is taken as 1600 wide x 900 deep (the BOQ gives '
      'the screen width; the tray depth is ASSUMED). Two arrangements are tried '
      '- the cabinet facing the shower, and the cabinet turned onto an end wall '
      f'- and the better one is reported. {MIN_CIRC} mm is treated as the '
      'minimum usable circulation. The WC is not placed, and it needs room '
      'again, so these figures are optimistic.')
    A('')
    A('The pattern to notice: **three of the four first-floor bathrooms are '
      'under 1600 mm on their short dimension**, so a 900 mm shower tray plus '
      'circulation only works if the cabinet is turned onto an end wall. If the '
      'design has the cabinet facing the shower, none of them works and the '
      'shower tray has to get shallower.')
    A('')
    A('This is an aid to the mark-up, not a conclusion. Confirm on the space '
      'keys.')
    A('')
    p = os.path.join(L, 'bathroom_material_schedule.md')
    open(p, 'w').write('\n'.join(o))

    c = os.path.join(L, 'bathroom_material_schedule.csv')
    with open(c, 'w', newline='') as f:
        w = csv.writer(f)
        w.writerow(['material_key', 'material', 'boq_ref', 'specified',
                    'not_specified', 'modelled_as'])
        for row in MATERIALS:
            w.writerow(row)
    print('wrote', p)
    print('wrote', c)

if __name__ == '__main__':
    main()
