# Project Base Archipelago

Archipelago integration source for **Project Base 0.8.4.2**.

This source checkout includes the apworld and the standalone base-ROM reconstruction utility.

## Installation
See the [setup guide](projectbase/docs/setup_en.md)

### Applying a generated player patch

Applying an `.appb` reconstructs Project Base automatically from your clean
**Super Metroid (Japan, USA)** and **A Link to the Past Japan 1.0** ROMs.  

## Alpha limits

The final-goal predicate is conservative.  
Experimental FX, Flood and Party modes change physical behavior beyond what the route logic models.

DeathLink, entrance randomization, alternate goals and the source randomizer's alternate Vanilla Map are not implemented.

## Repository contents

| Path | Purpose |
| --- | --- |
| `projectbase/` | Apworld source, logic, SNI integration, ASM and bundled patch data |
| `tools/` | Published IPS graphics-stripping and base-ROM reconstruction utility and guide |
| `tests/` | Regression tests |
| `maps/` | CSV worksheets for reviewing checks and routes |

## Credits

- Project Base logic and visual resources: [Quote58/Project-Base-0.8-Randomizer, revision 911273c](https://github.com/Quote58/Project-Base-0.8-Randomizer/tree/911273cafd7d5cabec2ea4e8458a52a91b95081a).
  See [visual resource provenance](projectbase/data/visuals/UPSTREAM.txt) and
  [stripped PB patch provenance](projectbase/data/pb-base-UPSTREAM.txt).
- PLM adaptations: [SMBasepatch](https://github.com/beauxq/SMBasepatch/tree/047d7725d08cf298d191c9f7c6ea4de987135242),
  with its [license notice](projectbase/asm/SMBasepatch-LICENSE.txt).
- AP icons and reused components: [Archipelago notice](projectbase/data/Archipelago-LICENSE.txt).
- QoL and input-mapping adaptations: [VARIA notice](projectbase/data/VARIA-LICENSE.txt).
  PB elevator behavior follows [Quote58's public faster-elevator source](https://github.com/Quote58/ACID-engine/blob/main/Code/extra/Project%20Base/PB_faster_elevators.asm).
