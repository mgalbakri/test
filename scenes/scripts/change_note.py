#!/usr/bin/env python3
"""Master bedroom joinery re-measure change note (owner decision D-02).

The owner instructed that the joinery be re-measured to the room rather than
the room re-assigned. This issues the note the contractor re-quotes against.
Idempotent.
"""
import json, os, datetime

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
L = os.path.join(ROOT, 'logs')
BOQ = json.load(open(os.path.join(L, 'boq_parsed.json')))
Q = BOQ['quotation']
TODAY = datetime.date.today().isoformat()

# ref, label, quoted_mm, installable_mm, quoted_value_SAR, why
REMEASURE = [
 (f'{Q}/31', 'Wardrobe run, master bedroom', 4260, 2630, 13300,
  'Quoted W=4260 mm. The wardrobe recess measures 2630 x 480 mm clear, so a '
  '4260 mm run cannot be installed.'),
 (f'{Q}/33', 'TV-area run, master bedroom', 4260, 3140, 14580,
  'Quoted W=4260 mm. The facing wall is 4260 mm long but carries a 1000 mm '
  'window, leaving 3260 mm in two pieces. 120 mm is held clear of the '
  'headboard, so 3140 mm is installable, as 1450 + 1690 mm.'),
]

def main():
    o = []
    A = o.append
    A('# Change note - master bedroom joinery re-measure')
    A('')
    A(f'Quotation {Q} - issued {TODAY}')
    A('')
    A('**For the contractor to re-quote.** Owner instruction D-02.')
    A('')
    A('## Why')
    A('')
    A('Items 31 and 33 are both quoted at W=4260 mm. Measured against the '
      'as-built drawing, neither can be installed at that length. The BOQ '
      'already anticipates re-measurement: *"The project is re-measured for '
      'all items Excepet some of the items mentioned above the B.O.Q."*')
    A('')
    A('The room itself is an ASSUMED identification (conflict C-03, decision '
      'D-01). If the owner\'s mark-up places the master bedroom in a different '
      'space, this note is void and the quantities must be re-taken.')
    A('')
    A('## Re-measured quantities')
    A('')
    A('| BOQ ref | Item | Quoted | Installable | Variance | Quoted (SAR) | '
      'Indicative pro-rata (SAR) | Indicative delta (SAR) |')
    A('|---|---|---|---|---|---|---|---|')
    tq = ti = 0.0
    for ref, label, quoted, inst, val, _ in REMEASURE:
        pro = val * inst / float(quoted)
        tq += val; ti += pro
        A(f'| {ref} | {label} | {quoted} mm | {inst} mm | '
          f'{(inst-quoted)/quoted*100:+.1f}% | {val:,.0f} | {pro:,.0f} | '
          f'{pro-val:+,.0f} |')
    A(f'| | **Total** | | | | **{tq:,.0f}** | **{ti:,.0f}** | **{ti-tq:+,.0f}** |')
    A('')
    A(f'At 15% VAT the indicative delta is **SAR {(ti-tq)*1.15:+,.0f}**.')
    A('')
    A('The pro-rata column is **indicative only**. Joinery does not price '
      'linearly - carcass, ironmongery, mouldings and fitting carry fixed '
      'cost - so the contractor\'s re-quote will not match it. It is given so '
      'the order of magnitude is visible before the re-quote arrives.')
    A('')
    A('## Detail')
    A('')
    for ref, label, quoted, inst, val, why in REMEASURE:
        A(f'**{ref} - {label}**')
        A('')
        A(f'- Quoted {quoted} mm; installable {inst} mm.')
        A(f'- {why}')
        A('')
    A('## What this note does not change')
    A('')
    A(f'- Item {Q}/32 (headboard, L=2600 mm) fits the measured wall exactly. '
      'No variance, no change.')
    A('- Door-leaf panels on items 31 and 33 stay unpriced and Phase 2 - *"the '
      'panel for door leaf will be wall paper or fabric the price will be '
      'separate"*. They are modelled as PH2 placeholders.')
    A('- Depth and height are unchanged: D=500 mm (the recess measures 480 mm, '
      'so the run sits 20 mm proud) and H=3000 mm floor-to-ceiling.')
    A('')
    p = os.path.join(L, 'change_note_master_bedroom_joinery.md')
    open(p, 'w').write('\n'.join(o))
    print('wrote', p)
    print(f'indicative delta excl. VAT: SAR {ti-tq:+,.0f}')

if __name__ == '__main__':
    main()
