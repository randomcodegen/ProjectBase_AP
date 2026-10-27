; PB 0.8.4.2 QoL. New-game detection and warp guards follow VARIA's
; new_game / fast_reload approach (data/VARIA-LICENSE.txt). PB has its own
; elevator movement and SRAM checksums: do not apply vanilla IPS patches.

org $F19000
ap_start_at_ship:
    lda $0998 : cmp #$001F : bne .done
    lda.l $7ED914 : bne .done ; new file only, never a saved game
    stz $079F : stz $078B
    lda #$0005 : sta.l $7ED914
.done:
    lda.l $7ED914 ; replaced load in the native game-data loader
    rtl

ap_ship_warp:
    ; Entered before PB processes Start/pause. Its caller used JSR in bank 82.
    php : rep #$30 : pha : phx : phy : phb
    pea $7E7E : plb : plb
    lda $8B : and #$3030 : cmp #$3030 : bne .normal
    lda $8F : and #$3030 : beq .normal ; no repeat while holding the chord
    lda $0998 : cmp #$0008 : bne .normal
    lda $079F : cmp #$0006 : bcs .normal ; never Ceres/debug areas
    lda $09C2 : beq .normal
    lda $0617 : bne .normal ; APU upload
    lda $0943 : bne .normal ; escape timer
    lda #$000E : jsl $808233 : bcs .normal ; Zebes escape event
    lda.l $70318E : bne .normal ; completed game
    ; Flush the departing area's explored map before changing area. Both calls
    ; use PB's checksum-aware save routine, including collection flags/cursor.
    lda $0952 : jsl $818000
    stz $079F : stz $078B
    jsl $80858C ; load Crateria's explored map before saving the ship checkpoint
    lda $D8F8 : ora #$0001 : sta $D8F8 ; ship is a used save station
    lda #$0005 : sta.l $7ED914
    lda $0952 : jsl $818000
    jsl $82BE17 ; stop sounds
    lda $0952 : jsl $818085
    jsl $80858C
    lda #$0006 : sta $0998 ; native room/game loader, not a synthetic door
    plb : ply : plx : pla : plp
    jml $82FE6C ; PB main-game RTS (existing bank-82 return address)
.normal:
    plb : ply : plx : pla : plp
    php : rep #$30 : jsl $A08EB6 ; overwritten PB main-game entry
    jml $82FE18
assert pc() <= $F1A000

org $82801D
    jsl ap_start_at_ship
org $82EEDA
    db $1F ; bypass intro cinematic, then the loader selects the ship
org $82FE11
    jml ap_ship_warp

; Restore the permanent speeds from PB_faster_elevators.asm (DSO/Quote58).
; 0.8.4.2 reduced these to 1, no Run check exists in these movement routines.
; Keep PB's downward transition fix, including its existing extra INC.
org $A39591
    dw $0003
org $A395B0
    dw $0003
org $A395D2
    dw $0003
org $A395EC
    dw $0003

; AimAnyButton behavior (VARIA-LICENSE.txt), adapted to PB's mapper.
; Keep each action's own input read, remove only the L/R-only rejection.
org $918247 ; newly pressed Aim Down
    nop #2
org $91825D ; newly pressed Aim Up
    nop #2
org $9182B2 ; held Aim Down
    nop #2
org $9182C8 ; held Aim Up
    nop #2
org $82F5CA ; file-menu labels: do not replace non-L/R aim bindings with OFF
    rts
org $87F0A4 ; PB pause menu: use the other actions' seven-button validation
    jmp $F07F
org $87E1B4 ; PB pause-menu sprites: keep the selected button instead of OFF
    nop #3
