; Project Base 0.8.4.2 AP bridge. MIT-derived PLMs: SMBasepatch-LICENSE.txt.
; The patcher copies the user's PB bank $85 to $F0 before assembly. Keeping
; PB's engine at identical low addresses preserves its local JSR/data pointers.
; DB stays $85, retaining WRAM mirrors and PB data/font access. F0:FF00 holds adapters.
lorom

!recv = $702000
!wcount = $702602
!completed = $7ED8AE ; inside PB's existing $D7C0..D91F save block
!tags = $703600     ; 384 16-bit absolute indices, prevents stale ring receipts
!active = $703180
!message_item = $703182
!message_player = $703184
!send_read = $702680
!send_write = $702682
!send = $702700

org $F18000
config_player_id: dw $0001
item_name_count: dw 22
player_count: dw 2
protocol_version: dw $0002

org $F18100
ap_boot:
    php : rep #$30 : pha : phx : phy
    ldx #$0013
.compare:
    lda.l $80FFC0,x
    cmp.l $703015,x
    bne .reset
    dex : dex
    bpl .compare
    bra .done
.reset:
    lda #$0000
    ldx #$3FFE
.clear:
    sta.l $700000,x ; a different seed/bridge invalidates vanilla save slots too
    dex : dex
    bpl .clear
    lda #$FFFF
    ldx #$02FE
.tags:
    sta.l !tags,x
    dex : dex
    bpl .tags
    ldx #$0013
.title:
    lda.l $80FFC0,x
    sta.l $703015,x
    dex : dex
    bpl .title
.done:
    lda #$0000 : sta.l !active
    ply : plx : pla : plp
    sep #$30 : lda #$8F ; overwritten Nintendo-logo init instructions
    rtl

ap_frame:
    jsl $A09169 ; original last main-game routine
    php : rep #$30 : pha : phx : phy : phb
    pea $7E7E : plb : plb
    lda $0998 : cmp #$0008 : beq + : brl .done : +
    lda $079B : cmp #$DF45 : bne + : brl .done : + ; Ceres Mode 7
    lda.l !completed
    cmp #$FFFF : bne + : brl .done : + ; refuse counter rollover
    cmp.l !wcount : bcc + : brl .done : +
    pha
    jsr recv_index
    tax
    lda.l !tags,x
    cmp $01,s
    beq + : brl .stale : +
    txa : asl : tax
    lda.l !recv+2,x : and #$00FF
    cmp #$0016 : bcc + : brl .stale : +
    lda.l !recv,x
    cmp.l config_player_id : bne .receive
    lda.l !recv+2,x : xba : and #$00FF
    cmp #$00FF : beq .receive
    phx
    jsl $80818E
    lda.l $7ED870,x : and.l $7E05E7
    beq .collect
    plx
    bra .advance ; local reward already granted, suppress own-world echo
.collect:
    lda.l $7ED870,x : ora.l $7E05E7 : sta.l $7ED870,x
    lda.l $7ED86E : inc : sta.l $7ED86E
    plx
.receive:
    lda.l !recv,x
    jsr player_index
    sta.l !message_player
    lda.l !recv+2,x : and #$00FF : asl : tax
    lda.l ap_to_native,x
    sta.l !message_item
    asl : tax
    lda #$0002 : sta.l !active
    jsl perform_item_pickup
    jsr clamp_capacity
    lda #$0000 : sta.l !active
.advance:
    pla : inc : sta.l !completed
    bra .done
.stale:
    pla ; await SNI replenishing the requested absolute entry
.done:
    plb : ply : plx : pla : plp
    rtl

; A = absolute index, result = byte offset in the 384-entry tag array
recv_index:
.loop:
    cmp #$0180 : bcc .end
    sec : sbc #$0180 : bra .loop
.end:
    asl : rts

; A = AP player id, returns ROM name index, last entry means unknown sender
player_index:
    phx : phy
    pha
    ldx #$0000 : ldy #$0000
.loop:
    lda $01,s
    cmp.l player_ids,x : beq .found
    inx : inx : iny
    tya : cmp.l player_count : bcc .loop
    dey
.found:
    pla : tya : ply : plx : rts

clamp_capacity:
    ; Vanilla pickup routines supply HUD/menu updates. Clamp afterwards so
    ; repeat ammo and tank grants cannot accumulate into 16-bit overflow.
    ldx #$0000
.next:
    lda.l max_addresses,x : tay
    lda $0000,y
    cmp.l max_values,x : bcc .current
    lda.l max_values,x : sta $0000,y
.current:
    lda.l current_addresses,x : tay
    lda $0000,y
    cmp.l max_values,x : bcc .continue
    lda.l max_values,x : sta $0000,y
.continue:
    inx : inx : cpx #$000A : bcc .next
    rts
max_addresses: dw $09C4,$09C8,$09CC,$09D0,$09D4
current_addresses: dw $09C2,$09C6,$09CA,$09CE,$09D6
max_values: dw 1499,999,99,99,400

i_live_pickup_multiworld:
    php : rep #$30 : pha : phx : phy
    lda.l $7E1DC7,x : and #$00FF : asl #3 : tax
    ; The vanilla collected flag is always authoritative, including when offline
    ; or the bounded send queue is full. SNI reconciles the whole flag bitmap.
    lda.l !send_write : cmp #$0080 : bcs .display
    asl #3 : tay
    phx : tyx
    pla
    sta.l !send+4,x
    tax
    lda.l !send_write : inc : sta.l !send_write
.display:
    lda.l rando_item_table,x : bne .foreign
    lda.l rando_item_table+2,x : cmp #$0016 : bcs .end
    asl : tax
    lda #$0000 : sta.l !active
    jsl perform_item_pickup
    jsr clamp_capacity
    bra .end
.foreign:
    lda.l rando_item_table+2,x : sta.l !message_item
    lda.l rando_item_table+4,x : sta.l !message_player
    lda #$0001 : sta.l !active
    lda #$0019 : jsl $858080
    lda #$0000 : sta.l !active
.end:
    ply : plx : pla : plp
    rtl

; Called in the copied PB message engine. Build its vanilla four-line tilemap.
ap_draw_message:
    php : rep #$30 : pha : phx : phy
    lda #$0070 : sta $05A6
    lda #$007C : sta $05A4
    stz $05A2
    ldx #$00E0 : lda #$0000
.blank:
    sta.l $7E3000,x : dex : dex : bpl .blank
    lda.l !active : cmp #$0001 : beq .sent
    ldx #$00FE
.received:
    lda.l received_template,x : sta.l $7E3200,x
    dex : dex : bpl .received
    bra .names
.sent:
    ldx #$00FE
.sent_copy:
    lda.l sent_template,x : sta.l $7E3200,x
    dex : dex : bpl .sent_copy
.names:
    lda.l !message_item : cmp.l item_name_count : bcc .item_ok
    lda #$0000
.item_ok:
    asl #6 : tax
    ldy #$0000
.item:
    lda.l item_names,x
    phx : tyx : sta.l $7E3240,x : plx
    inx : inx : iny : iny : cpy #$0040 : bcc .item
    lda.l !message_player : cmp.l player_count : bcc .player_ok
    lda.l player_count : dec
.player_ok:
    asl #6 : tax
    ldy #$0000
.player:
    lda.l player_names,x
    phx : tyx : sta.l $7E32C0,x : plx
    inx : inx : iny : iny : cpy #$0040 : bcc .player
    stz $0A
    lda #$0100 : sta $02
    lda #$0080 : sta $0E
    ply : plx : pla : plp
    rtl

ap_message_entry:
    ; The copied engine must not PHK/PLB to bank F0: C0+ lacks WRAM mirrors.
    ; Reproduce PB's entry stack with its original data bank before continuing.
    php : phb : rep #$30 : pha : sep #$20
    lda #$85 : pha : plb
    rep #$30 : pla : pha
    lda.l !active : beq .native
    pla : lda #$0019 ; valid PB large-box definition for every custom receipt
    bra .ready
.native:
    pla
.ready:
    phx : phy
    jml $F08088
assert pc() <= $F1A000

; Seed data is filled by rom.py, no ROM-derived graphics are bundled.
org $F1A000
item_names: fillbyte $00 : fill $2400 ; 144 centered 32-word rows
org $F28000
player_names: fill $4000 ; 256 centered 32-word rows, no LoROM bank crossing
org $F2C000
player_ids: fill $0200
org $F2C800
rando_item_table: fill $0800 ; indexed by vanilla collection flag * 8
org $F2D000
ap_to_native:
    dw 19,4,5,10,12,7,8,9,16,13,17,11,15,6,18,14,21,20,0,1,2,3
sm_item_graphics:
    dw $0008,$000A,$000C,$000E,$E12F,$E15D,$E18B,$E1B9,$E1E7,$E215,$E243
    dw $E271,$E2A3,$E2D8,$E30D,$E33A,$E368,$E395,$E3C3,$E3F1,$E41F,$EFE2
    dw plm_graphics_entry_offworld_progression_item,plm_graphics_entry_offworld_item
sm_item_plm_pickup_sequence_pointers:
    dw $E0B6,$E0DB,$E100,$E125,$E152,$E180,$E1AE,$E1DC,$E20A,$E238,$E266
    dw $E294,$E2C8,$E2FD,$E330,$E35D,$E38B,$E3B8,$E3E6,$E414,$E442,$F005
org $F2D200
sent_template: fill $0100
received_template: fill $0100

; PB PLM bank has verified FF space from $F94F. Keep original Dash Ball intact.
org $84F950
incsrc "items.asm"
assert pc() <= $850000

; The source randomizer fixes Zebes waking after shuffled pickups. PB's two
; state selectors still use $E652, here either a check or AP receipt wakes it.
org $8FFC92
ap_zebes_awake:
    lda.l $7ED86E : ora.l !completed : beq .no
    lda $0000,x : tax : jmp $E5E6
.no:
    inx : inx : rts
assert pc() <= $8FFCB0
org $8F9767
    dw ap_zebes_awake
org $8F97C0
    dw ap_zebes_awake

; Adapt PB's message engine without borrowing any vanilla/Subversion addresses.
org $F0FF00
ap_body_adapter:
    lda.l !active : beq .normal
    jsr $80F7 : jsl $808F0C : jsl $8289EF
    jsl ap_draw_message
    rts
.normal:
    jsr $80F7 : jmp $8478
ap_keys_adapter:
    lda.l !active : beq .normal
    rts
.normal:
    ldx $1C1F : jmp $8583
org $F08475
    jmp ap_body_adapter
org $F08580
    jmp ap_keys_adapter
org $858080
    jml ap_message_entry
; PB inherits SM's 8 KiB SRAM mirror test, which rejects expanded AP SRAM.
; Keep the region check, skip only its destructive SRAM mapping test.
org $808693
    jmp $86E1
org $8B914A
    jsl ap_boot
; PB redirects $82:8B44 to its replacement main-game routine at $82:FE11.
org $82FE67
    jsl ap_frame

incsrc "qol.asm"
