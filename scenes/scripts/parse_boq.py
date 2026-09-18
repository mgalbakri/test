#!/usr/bin/env python3
"""Parse the governing BOQ sheet into a structured CSV + JSON.

Governing source: sheet 'nabati rest. (3)' = Quotation R1-M.A. 740-26, 20/07/2026,
PROJECT "Mr. Mohammed & Mrs. Aziza Villa - Jeddah".
The other two sheets in the workbook belong to DIFFERENT projects and are ignored
(see logs/SUMMARY.md, conflict C-01).

Idempotent: rewrites outputs from scratch on every run.
"""
import openpyxl, csv, json, os, re, sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
XLSX = os.path.join(ROOT, 'inputs', 'boq', 'BOQ_R1-MA-740-26.xlsx')
SHEET = 'nabati rest. (3)'
QUOTE = 'R1-M.A.740-26'

# BOQ section header -> canonical room key used across the project
ROOM_MAP = {
    'GROUND FLOOR - Entance Salon':        'entrance_salon',
    'FRIST FLOOR - Powder Room Mrs. Aziza':'powder_room_aziza',
    'Bath Room Mrs. Aziza':                'bathroom_aziza',
    'OFFICE':                              'office',
    'POWDER ROOM Mr. Mohammed':            'powder_room_mohammed',
    'BATH ROOM Mr. Mohammed':              'bathroom_mohammed',
    'HALLWAYS':                            'hallways',
    'KITCHENETTE':                         'kitchenette',
    'MASTER BEDROOM':                      'master_bedroom',
}

def clean(v):
    if v is None: return ''
    return re.sub(r'\s+', ' ', str(v)).strip()

def parse():
    wb = openpyxl.load_workbook(XLSX, data_only=True)
    ws = wb[SHEET]
    rows, room, notes = [], None, []
    in_notes = False
    sub_seq = 0
    last_no = None
    for r in ws.iter_rows(min_row=1, values_only=True):
        c = [clean(x) for x in r]
        no, desc, unit, qty, up, tot = c[0], c[1], c[2], c[3], c[4], c[5]
        if desc.startswith('NOTES'):
            in_notes = True; continue
        if in_notes:
            if desc.startswith('*'): notes.append(desc.lstrip('* ').strip())
            continue
        if desc in ROOM_MAP:
            room = ROOM_MAP[desc]; sub_seq = 0; continue
        if not desc.startswith('**'):
            continue
        if no:
            last_no = no.strip(); sub_seq = 0; ref_no = last_no
        else:
            sub_seq += 1
            ref_no = f'{last_no}{chr(96+sub_seq)}'   # 1 -> 1a, 1b ...
        def num(x):
            try: return float(x)
            except: return None
        rows.append({
            'boq_item':   f'{QUOTE}/{ref_no}',
            'room':       room,
            'description':desc.lstrip('* ').strip(),
            'unit':       unit,
            'qty':        num(qty),
            'unit_price': num(up),
            'total':      num(tot),
        })
    return rows, notes

def main():
    rows, notes = parse()
    outdir = os.path.join(ROOT, 'logs'); os.makedirs(outdir, exist_ok=True)
    with open(os.path.join(outdir, 'boq_parsed.csv'), 'w', newline='') as f:
        w = csv.DictWriter(f, fieldnames=['boq_item','room','description','unit','qty','unit_price','total'])
        w.writeheader(); w.writerows(rows)
    with open(os.path.join(outdir, 'boq_parsed.json'), 'w') as f:
        json.dump({'quotation': QUOTE, 'sheet': SHEET, 'items': rows, 'notes': notes}, f, indent=2)
    # arithmetic audit
    bad = [r for r in rows if None not in (r['qty'], r['unit_price'], r['total'])
           and abs(r['qty']*r['unit_price'] - r['total']) > 0.5]
    print(f'items={len(rows)}  rooms={len(set(r["room"] for r in rows))}')
    print(f'sum(total)={sum(r["total"] or 0 for r in rows):,.2f}')
    for b in bad:
        print(f'  ARITHMETIC {b["boq_item"]}: {b["qty"]} x {b["unit_price"]} = '
              f'{b["qty"]*b["unit_price"]:,.0f} but sheet says {b["total"]:,.0f}')
    for r in rows:
        if r['room'] is None: print('  ORPHAN (no room section):', r['boq_item'])

if __name__ == '__main__':
    main()
