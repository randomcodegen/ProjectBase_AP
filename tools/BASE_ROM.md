# Rebuilding the base ROM with ALttP enemy graphics

The apworld's builder replaces the Bubble/Anti-Fairy and Spike Trap graphics
embedded in the original PB patch with graphics reconstructed from your own
ALttP ROM.  
It preserves PB's exact appearance, enemies and gameplay.  
Its output is the normal, clean Project Base 0.8.4.2 ROM.  
This happens automatically when applying an `.appb`.

The graphics-stripped PB IPS and sprite differences are bundled in the apworld.

## Standalone developer commands

Use Python 3.10 or newer from the repository directory.  
No extra packages are needed.  
Supply these files yourself:

- `project_base_0.8.4.2.zip`, the original release ZIP
- A clean Super Metroid (JU) ROM
- A clean **Zelda no Densetsu: Kamigami no Triforce (Japan), revision 1.0** ROM

Both ROMs may have an optional 512-byte copier header.  

Create the output folder if it does not exist. In PowerShell:

```powershell
New-Item -ItemType Directory -Path dist -Force | Out-Null
```

First remove the two embedded graphics ranges from the original PB IPS:

```text
python -m tools.build_base_rom prepare "PATH/project_base_0.8.4.2.zip" "dist/project_base_0.8.4.2-zelda-stripped.ips"
```

Then rebuild the base with both source ROMs and that stripped patch:

```text
python -m tools.build_base_rom build "PATH/Super Metroid (JU).sfc" "PATH/Zelda no Densetsu - Kamigami no Triforce (Japan).sfc" "dist/project_base_0.8.4.2-zelda-stripped.ips" "dist/project_base_0.8.4.2-rebuilt.sfc"
```

The builder checks all input versions and the final ROM SHA-256:
`98e42d15792724e712c1519852b6a0c79020da91a1e42d36335a4b24df2ea0b4`.  
Successful output is byte-for-byte identical to the supported PB release.

## Reconstruction

`prepare` removes writes to these PC offsets, splitting overlapping IPS records:

| Enemy | PC offset | SNES address | Size |
| --- | --- | --- | --- |
| Spike Trap | `0x17F600` | `$AF:F600` | 128 bytes |
| Bubble / Anti-Fairy | `0x186F20` | `$B0:EF20` | 1024 bytes |

`build` decompresses ALttP sprite sheet 82, converts its 3bpp tiles to SNES 4bpp,
and maps colors to PB's palette slots.  
The Bubble combines the skull and flame tiles into PB's eight frame slots.  
The Spike Trap starts from ALttP's small Spike Block.  
It then applies the PB-specific XOR differences recorded in `projectbase/data/pb-zelda-delta.json`.  
That file holds differences from the conversion, not complete enemy graphics.

`projectbase/data/pb-base-stripped.ips`is the bundled stripped patch.  
Run the ROM-free checks with:

```text
python -m unittest discover -s tests -p "test_base_rom_builder.py" -v
```
