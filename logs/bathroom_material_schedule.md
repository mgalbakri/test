# Bathroom material schedule

Quotation R1-M.A.740-26 - generated 2026-09-19

## BLUF

**Almost nothing about the bathroom finishes is actually specified.** The BOQ names a marble and a veneer and says "porcelain" - no size, no colour, no finish, no manufacturer for any tile, and no paint type. Three things need answering before anyone orders:

1. **The porcelain may not be in the price.** Items 11 and 23 say *"Installation of"*, not *"Supply and installation"* like every other line (R-01).
2. **SAR 2,500 may be double-counted** on strip-out between items 10 and 22 (R-02).
3. **The walls are stripped but only the shower area is re-tiled** - the rest gets SAR 850 of paint (R-03).

And one that affects where the rooms go: **on the first floor only FF-BATH-W is big enough for Mrs Aziza's specified package**, and only just. Three of the four first-floor bathrooms are under 1600 mm on their short dimension (R-09).

Priced value: Mrs Aziza SAR 22,260, Mr Mohammed SAR 17,110, G.F. Guests Bathroom SAR 2,000 (cladding and paint only). All sanitary ware is unpriced (R-05).

## Materials as specified

| Material | BOQ ref | Specified | Not specified | How it is modelled |
|---|---|---|---|---|
| **Porcelain floor tile**<br>`POR_Floor` | R1-M.A.740-26/11, /23 | Porcelain, floor. "Installation of porcelain for flooring and wall @ shower area." | Size, colour, finish, slip rating, manufacturer, grout colour. Nothing is given. | Modelled 600 x 1200 mm ASSUMED, light warm grey, satin. Real-world UV. |
| **Porcelain wall tile, shower area**<br>`POR_Wall_Shower` | R1-M.A.740-26/11, /23 | Porcelain, walls, shower area only. | Size, colour, finish, extent (height, wrap), trim/edge detail. | Modelled 600 x 1200 mm ASSUMED, matching floor, full height in shower zone. |
| **Marble vanity top + skirting**<br>`MRB_RossoLevanto` | R1-M.A.740-26/14, /24 | Rosso Levanto marble (BOQ: "Rossi Levanto"), top W1100 x D500 x 20 mm thk, with marble skirting. Mrs Aziza skirting L1100 x H150 x 20 mm thk. | Mr Mohammed skirting is undimensioned. Edge profile, finish (polished/honed), basin cut-out type (undermount / vessel / countertop), tap-hole drilling. | Dark oxblood ground with white veining, polished, coat 0.6. Vein scale set to the 1100 mm slab so figure reads at real size. |
| **MDF with beech veneer, stain finish**<br>`WD_Beech_Veneer` | R1-M.A.740-26/12, /13, /26 | 3-leaf cabinet W1700 x H2800 x D500 (Mrs Aziza only). Vanity cabinet W1100 x H850 x D500 (both bathrooms). | Stain colour/reference, sheen, whether carcass is moisture-resistant (W/R) - the bathroom cabinets say "MDF", the joinery elsewhere says "MDF W/R". Ironmongery, soft-close, internal fit-out. | Quiet low-contrast beech figure, roughness 0.32, light coat. Deliberately subtle: grain direction is object-space, so a strong figure runs wrong on vertical parts. |
| **Frosted glass shower door and partition**<br>`GLS_Frosted_10mm` | R1-M.A.740-26/15, /25 | Frosted glass (BOQ: "Forsted Galss"), 10 mm thk, W1600 x H1500. | H1500 is low for a shower screen - see risk R-04. Hinge/track type, hardware finish, edge polish, toughening/safety marking. | Transmission 1.0, roughness 0.38, IOR 1.52. |
| **Wall and ceiling paint**<br>`PNT_Wall_Ceiling` | R1-M.A.740-26/16, /27 | Supply and apply, wall and ceiling. LS SAR 850 per bathroom. | Paint type, sheen, colour, number of coats, and whether a bathroom-grade (anti-mould, moisture-resistant) product is intended. Nothing is given. | Off-white matt, roughness 0.62. |
| **Cement board cladding + base paint**<br>`CEM_Board` | R1-M.A.740-26/5 | Wall cladding in cement board with base paint and ceiling paint, G.F. Guests Bathroom only. LS SAR 2,000. | No porcelain at all in this room - it is a painted bathroom. Confirm intended. Board thickness, fixing, jointing, finish coat. | Not modelled - room not located (C-03). |
| **Waterproofing / "new insulation"**<br>`INS_Tanking` | R1-M.A.740-26/10, /22 | Included within the strip-out lines: "included the making new insulation". | Membrane type, upstand height, falls to gully, junction detailing, testing. This is the single most consequential unspecified item in a wet room. | Not modelled (concealed). |

## Bathroom by bathroom

### Mrs Aziza

The only bathroom with the 3-leaf cabinet (item 12).

| Ref | Item | Unit | Qty | SAR |
|---|---|---|---|---|
| R1-M.A.740-26/10 | Removing the porcelain floors and walls in tow bathroom and glass of the shower and sink included the making new insulation | LS | 1.0 | 2,500 |
| R1-M.A.740-26/11 | Installation of porcelain for flooring and wall @ shower area | LS | 1.0 | 3,250 |
| R1-M.A.740-26/12 | Supply and installation 3 leaf cabinet Made of MDF with Beech veneer finish size W = 1700 x H = 2800 mmx D =500 mm @ as per design | Unit | 1.0 | 4,760 |
| R1-M.A.740-26/13 | Supply and installation Vanity cabinet Made of MDF with Beech veneer finish size W = 1100 x H = 850 mmx D =500 mm as per design | Unit | 1.0 | 2,500 |
| R1-M.A.740-26/14 | Supply and installation Marble Top for Vanity kind of Rossi Levanto size W = 1100 x D = 500 mm x Thk.20 mm with Marble skirting si... | Unit | 1.0 | 5,650 |
| R1-M.A.740-26/15 | Supply and installation Shower Forsted Galss door & Partition Thk.10mmwith size W= 1600 x H = 1500 mm | Unit | 1.0 | 2,750 |
| R1-M.A.740-26/16 | supply and Apply wall & Ceiling paint | LS | 1.0 | 850 |
| | **Total** | | | **22,260** |

### Mr Mohammed

No 3-leaf cabinet; otherwise the same package.

| Ref | Item | Unit | Qty | SAR |
|---|---|---|---|---|
| R1-M.A.740-26/22 | Removing the porcelain floors and walls and glass of the shower and sink included the making new insulation | LS | 1.0 | 2,500 |
| R1-M.A.740-26/23 | Installation of porcelain for flooring and wall @ shower area | LS | 1.0 | 3,250 |
| R1-M.A.740-26/24 | Supply and installation Marble Top for Vanity kind of Rossi Levanto size W = 1100 x D = 500 mm x Thk.20 mm with Marble skirting | Unit | 1.0 | 5,260 |
| R1-M.A.740-26/25 | Supply and installation Shower Forsted Galss door & Partition Thk.10mmwith size W= 1600 x H = 1500 mm | Unit | 1.0 | 2,750 |
| R1-M.A.740-26/26 | Supply and installation Vanity cabinet Made of MDF with Beech veneer finish size W = 1100 x H = 850 mmx D =500 mm as per design | Unit | 1.0 | 2,500 |
| R1-M.A.740-26/27 | supply and Apply wall & Ceiling paint | LS | 1.0 | 850 |
| | **Total** | | | **17,110** |

### G.F. Guests Bathroom

Priced inside the Entrance Salon section, and absent from the nine-room register (conflict C-08). Cement board and paint only - no porcelain, no marble, no joinery, no glass.

| Ref | Item | Unit | Qty | SAR |
|---|---|---|---|---|
| R1-M.A.740-26/5 | Supply and installation wall Cladding Cement board with base paint & Ceiling paint @ G.F. Guests Bathroom | LS | 1.0 | 2,000 |
| | **Total** | | | **2,000** |

## Risks and questions

| Ref | Severity | Issue | Detail | What to do |
|---|---|---|---|---|
| R-01 | HIGH | R1-M.A.740-26/11 and /23 - porcelain supply may be excluded | Every other line in this BOQ reads "Supply and installation". Items 11 and 23 read "Installation of porcelain for flooring and wall @ shower area" - installation only, no supply. On a plain reading the tile itself is not in the SAR 3,250, and the cost is open until a tile is selected. | Get this confirmed in writing before signing. At Jeddah rates a mid-range porcelain over two bathrooms is a four-figure sum in its own right. |
| R-02 | HIGH | R1-M.A.740-26/10 vs /22 - possible double count of SAR 2,500 | Item 10 prices strip-out "in tow bathroom" (two bathrooms) at SAR 2,500 under Mrs Aziza. Item 22 prices the same strip-out again, singular, under Mr Mohammed, at SAR 2,500. Either item 10 already covers both rooms and item 22 is a duplicate, or item 10's "two bathrooms" means something else (e.g. bathroom plus powder room). | Ask the contractor which rooms item 10 covers. If it covers both bathrooms, SAR 2,500 comes out. |
| R-03 | HIGH | Walls stripped throughout, re-tiled only at the shower | Item 10 removes "the porcelain floors and walls" across the bathroom. Item 11 reinstates porcelain "for flooring and wall @ shower area" only. The remaining wall area is covered by SAR 850 of paint (item 16 / 27). | Confirm this is the design intent: painted plaster rather than tile on the non-shower walls of a wet room. If tiling is wanted wall-to-wall, both the tile quantity and the SAR 3,250 installation figure need re-quoting. |
| R-04 | MEDIUM | R1-M.A.740-26/15 and /25 - shower screen height 1500 mm | The screen is specified W1600 x H1500. A shower enclosure is normally 1800-2000 mm high. At 1500 mm the screen finishes around chest height and water will carry over the top. | Confirm whether 1500 is a typo for 1900/2000, or whether this is deliberately a half-height partition to an open wet area. |
| R-05 | MEDIUM | Sanitary ware is entirely unpriced | BOQ note: "The Sink and Mixer and other Sanitary will be priced after checking what kind of required". So WC, basin, all mixers, the shower valve and head, wastes, traps and accessories are outside the SAR 39,370 the two bathrooms currently carry. | Specify these before the tiling is set out - basin and WC positions drive the tile setting-out and the vanity cut-out. |
| R-06 | LOW | The two bathrooms are specified asymmetrically | Mrs Aziza gets a 3-leaf beech cabinet W1700 x H2800 (item 12, SAR 4,760); Mr Mohammed has no equivalent. Her marble is SAR 5,650 with a dimensioned skirting; his is SAR 5,260 with the skirting undimensioned. | Confirm the asymmetry is intended rather than an omission. |
| R-07 | LOW | Carcass may not be moisture-resistant | Bathroom cabinets (items 12, 13, 26) are specified "Made of MDF with Beech veneer". Joinery elsewhere in the same BOQ is specified "MDF W/R" (water-resistant). The bathrooms are where W/R matters most. | Confirm W/R carcass for anything in a wet room. |
| R-09 | MEDIUM | Only one first-floor bathroom can take Mrs Aziza's package | Testing the specified fittings against the measured spaces: the 3-leaf cabinet (1700 mm) plus a shower only fits FF-BATH-W (2195 x 1755) on the first floor, and only with the cabinet turned onto an end wall, leaving about 855 mm of circulation. FF-BATH-N and FF-BATH-C cannot take the 1700 mm cabinet at all alongside a shower; FF-BATH-S cannot take the package in any arrangement. Three of the four are under 1600 mm on their short dimension. | Either Mrs Aziza's bathroom is FF-BATH-W, or the cabinet and shower tray need re-sizing. Worth settling at the same time as the space-key mark-up. |
| R-10 | MEDIUM | Shower tray size is not specified anywhere | The BOQ gives the glass screen (1600 x 1500) but never the tray or the shower footprint. A 900 mm tray depth has been ASSUMED for the fit testing above. Nothing in the BOQ supplies a tray at all - it falls under the unpriced sanitary ware (R-05). | Specify the tray (or a formed, tanked floor gully) before the fit above can be relied on. A shallower tray changes every verdict in that table. |
| R-08 | LOW | Terminology to correct on the order | "Rossi Levanto" should read Rosso Levanto. "Forsted Galss" should read frosted glass. "tow bathroom" should read two bathrooms. | Cosmetic, but worth fixing so the order matches the quarry name. |

## Which space is which

The bathrooms are still unlocated (conflict C-03, decision D-01). The BOQ joinery does narrow it down, because the full package has to fit:

| Space | Clear (mm) | Area | Mrs Aziza package | Mr Mohammed package |
|---|---|---|---|---|
| GF-WC | 2230 x 3895 | 8.69 m2 | Yes - 2995 mm (cabinet on an end wall) | Yes - 2995 mm (cabinet on an end wall) |
| FF-BATH-N | 1560 x 2955 | 4.61 m2 | **No** - 160 mm circulation at best | Very tight - 660 mm (cabinet on an end wall) |
| FF-BATH-C | 2805 x 1590 | 4.46 m2 | **No** - 190 mm circulation at best | Very tight - 690 mm (cabinet on an end wall) |
| FF-BATH-W | 2195 x 1755 | 3.85 m2 | Tight - 855 mm (cabinet on an end wall) | Tight - 855 mm (cabinet on an end wall) |
| FF-BATH-S | 1350 x 2430 | 3.28 m2 | **No** - -50 mm circulation at best | **No** - 450 mm circulation at best |

Test applied: the shower is taken as 1600 wide x 900 deep (the BOQ gives the screen width; the tray depth is ASSUMED). Two arrangements are tried - the cabinet facing the shower, and the cabinet turned onto an end wall - and the better one is reported. 700 mm is treated as the minimum usable circulation. The WC is not placed, and it needs room again, so these figures are optimistic.

The pattern to notice: **three of the four first-floor bathrooms are under 1600 mm on their short dimension**, so a 900 mm shower tray plus circulation only works if the cabinet is turned onto an end wall. If the design has the cabinet facing the shower, none of them works and the shower tray has to get shallower.

This is an aid to the mark-up, not a conclusion. Confirm on the space keys.
