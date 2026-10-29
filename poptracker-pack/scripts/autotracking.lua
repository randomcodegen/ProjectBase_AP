-- track the AP slot
local items = { [1346502656] = "morph_ball", [1346502657] = "bombs", [1346502658] = "charge_beam", [1346502659] =
"spazer", [1346502660] = "varia_suit", [1346502661] = "hijump_boots", [1346502662] = "speed_booster", [1346502663] =
"wave_beam", [1346502664] = "grapple_beam", [1346502665] = "gravity_suit", [1346502666] = "space_jump", [1346502667] =
"spring_ball", [1346502668] = "plasma_beam", [1346502669] = "ice_beam", [1346502670] = "screw_attack", [1346502671] =
"xray_scope", [1346502672] = "dash_ball", [1346502673] = "reserve_tank", [1346502674] = "energy_tank", [1346502675] =
"missile", [1346502676] = "super_missile", [1346502677] = "power_bomb" }
local locations = { [1346506756] = "@AP Checks/Power Bomb (Crateria surface)/Room $8F:93AA", [1346506757] =
"@AP Checks/Missile (Crateria moat)/Room $8F:95FF", [1346506758] =
"@AP Checks/Missile (Crateria 1st gauntlet missiles)/Room $8F:965B", [1346506759] = "@AP Checks/Bomb/Room $8F:9804",
  [1346506760] = "@AP Checks/Energy Tank (Crateria terminator)/Room $8F:990D", [1346506761] =
"@AP Checks/Missile (Crateria Map Station Missiles)/Room $8F:9994", [1346506762] =
"@AP Checks/Missile (Crateria 2st gauntlet missiles)/Room $8F:99BD", [1346506763] =
"@AP Checks/Energy Tank (Crateria gauntlet)/Room $8F:99BD", [1346506764] =
"@AP Checks/Super Missile (Crateria supers)/Room $8F:89D0", [1346506765] =
"@AP Checks/Missile (Crateria Final Missiles)/Room $8F:9A90", [1346506825] =
"@AP Checks/Missile (Underwater outside Wrecked Ship)/Room $8F:93FE", [1346506826] =
"@AP Checks/Missile (outside Wrecked Ship top)/Room $8F:93FE", [1346506827] =
"@AP Checks/Missile (outside WS under super block)/Room $8F:93FE", [1346506836] =
"@AP Checks/Missile (Crateria old MB missiles)/Room $8F:975C", [1346506858] =
"@AP Checks/Power Bomb (Crateria-Maridia Connector)/Room $8F:95A8", [1346506766] =
"@AP Checks/Power Bomb (Brinstar Etecoons)/Room $8F:9AD9", [1346506767] =
"@AP Checks/Missile (Brinstar below Early Supers)/Room $8F:9BC8", [1346506768] =
"@AP Checks/Super Missile (Brinstar Early Supers)/Room $8F:9BC8", [1346506769] =
"@AP Checks/Reserve Tank (Brinstar Reserve)/Room $8F:9C07", [1346506770] =
"@AP Checks/Missile (Brinstar Reserve Ron Popeil Missiles)/Room $8F:9C07", [1346506771] =
"@AP Checks/Missile (Brinstar Reserve Missiles)/Room $8F:9C07", [1346506772] =
"@AP Checks/Missile (Big Pink Brinstar top)/Room $8F:9D19", [1346506773] =
"@AP Checks/Missile (Big Pink Brinstar Charge Missiles)/Room $8F:9D19", [1346506774] =
"@AP Checks/Charge Beam/Room $8F:A0D2", [1346506775] = "@AP Checks/Missile (Brinstar Pipe Missiles)/Room $8F:9E52",
  [1346506776] = "@AP Checks/Morphing Ball/Room $8F:9E9F", [1346506777] =
"@AP Checks/Power Bomb (Blue Brinstar)/Room $8F:9E9F", [1346506778] =
"@AP Checks/Energy Tank (Pink Brinstar under Charge Beam)/Room $8F:9D19", [1346506779] =
"@AP Checks/Energy Tank (Pink Brinstar Hoppers Room)/Room $8F:A15B", [1346506780] =
"@AP Checks/Power Bomb (Beta Power Bomb Room)/Room $8F:A37C", [1346506781] =
"@AP Checks/Power Bomb (Alpha Power Bomb Room)/Room $8F:A3AE", [1346506782] =
"@AP Checks/Missile (Alpha Power Bomb Room)/Room $8F:A3AE", [1346506783] = "@AP Checks/Spazer/Room $8F:A447",
[1346506819] = "@AP Checks/Missile (Blue Brinstar First Missiles)/Room $8F:A107", [1346506820] =
"@AP Checks/Missile (Blue Brinstar middle)/Room $8F:9F64", [1346506821] =
"@AP Checks/Energy Tank (Blue Brinstar)/Room $8F:9F64", [1346506822] =
"@AP Checks/Dash Ball (Blue Brinstar upper Billy Mays)/Room $8F:9F64", [1346506823] =
"@AP Checks/Missile (Blue Brinstar lower Billy Mays)/Room $8F:9F64", [1346506824] =
"@AP Checks/Missile (Blue Brinstar Ceiling tile)/Room $8F:9F64", [1346506830] = "@AP Checks/Varia Suit/Room $8F:A6E2",
  [1346506834] = "@AP Checks/Power Bomb (Pink Brinstar Power Bombs)/Room $8F:9D19", [1346506835] =
"@AP Checks/Super Missile (Spospo Supers)/Room $8F:9B5B", [1346506837] =
"@AP Checks/Energy Tank (Brinstar near Etecoons E-tank)/Room $8F:A011", [1346506843] =
"@AP Checks/Missile (Brinstar Map Station Missiles)/Room $8F:9C35", [1346506844] =
"@AP Checks/Super Missile (Brinstar near Etecoons)/Room $8F:9C35", [1346506845] =
"@AP Checks/Missile (Kraid)/Room $8F:A471", [1346506846] = "@AP Checks/Energy Tank (Kraid)/Room $8F:A471", [1346506856] =
"@AP Checks/X-Ray Visor/Room $8F:A2CE", [1346506857] = "@AP Checks/Missile (western Green Bullshaft)/Room $8F:9C5E",
  [1346506860] = "@AP Checks/Missile (Southwest Brinstar Connector)/Room $8F:9E11", [1346506753] =
"@AP Checks/Missile (Bubble Mountain)/Room $8F:AD5E", [1346506754] =
"@AP Checks/Missile (Wave/LN Escape Missiles)/Room $8F:AD5E", [1346506755] = "@AP Checks/Wave Beam/Room $8F:AD5E",
  [1346506787] = "@AP Checks/Ice Beam/Room $8F:A890", [1346506788] = "@AP Checks/Missile (Crocomire)/Room $8F:A98D",
  [1346506789] = "@AP Checks/Hi-Jump Boots/Room $8F:A9E5", [1346506790] =
"@AP Checks/Missile (Hi-Jump Boots)/Room $8F:AA41", [1346506791] = "@AP Checks/Energy Tank (Hi-Jump Boots)/Room $8F:AA41",
  [1346506792] = "@AP Checks/Missile (Speed Booster)/Room $8F:ACF0", [1346506793] =
"@AP Checks/Speed Booster/Room $8F:AD1B", [1346506794] = "@AP Checks/Missile (Gold Torizo)/Room $8F:B283", [1346506795] =
"@AP Checks/Super Missile (Gold Torizo)/Room $8F:B283", [1346506796] = "@AP Checks/Missile (Mickey Mouse)/Room $8F:B40A",
  [1346506797] = "@AP Checks/Missile (Spring Ball Maze)/Room $8F:B510", [1346506798] =
"@AP Checks/Power Bomb (Spring Ball Maze)/Room $8F:B55A", [1346506799] =
"@AP Checks/Power Bomb (Power Bombs of Shame)/Room $8F:B5D5", [1346506800] =
"@AP Checks/Missile (FrankerZ)/Room $8F:B656", [1346506801] = "@AP Checks/Screw Attack/Room $8F:B6C1", [1346506802] =
"@AP Checks/Energy Tank (Lower Norfair Fire Flea E-tank)/Room $8F:B6EE", [1346506818] =
"@AP Checks/Energy Tank (Ridley)/Room $8F:B698", [1346506828] = "@AP Checks/Grapple Beam/Room $8F:AC2B", [1346506829] =
"@AP Checks/Missile (Left Grapple Missiles)/Room $8F:AC2B", [1346506838] =
"@AP Checks/Energy Tank (Crocomire)/Room $8F:AA82", [1346506839] =
"@AP Checks/Missile (Cathedral Missiles)/Room $8F:A788", [1346506840] =
"@AP Checks/Missile (Norfair Reserves 1st Missiles)/Room $8F:A788", [1346506841] =
"@AP Checks/Missile (Norfair Reserves 2nd Missiles)/Room $8F:A788", [1346506842] =
"@AP Checks/Reserve Tank (Norfair Reserves)/Room $8F:A788", [1346506847] =
"@AP Checks/Missile (Right Grapple Missiles)/Room $8F:AB64", [1346506848] =
"@AP Checks/Power Bomb (Grapple Power Bombs)/Room $8F:AB64", [1346506849] =
"@AP Checks/Missile (Crocomire Escape)/Room $8F:AF72", [1346506784] = "@AP Checks/Gravity Suit/Room $8F:C98E",
  [1346506785] = "@AP Checks/Reserve Tank (Wrecked Ship Reserves)/Room $8F:C98E", [1346506786] =
"@AP Checks/Missile (Wrecked Ship Reserves)/Room $8F:C98E", [1346506803] =
"@AP Checks/Missile (Wrecked Ship Attic)/Room $8F:CA52", [1346506804] =
"@AP Checks/Missile (Wrecked Ship Spike Room)/Room $8F:CA08", [1346506805] =
"@AP Checks/Energy Tank (Wrecked Ship)/Room $8F:CC27", [1346506806] =
"@AP Checks/Missile (Wrecked Ship Map Station Missiles)/Room $8F:CCCB", [1346506807] =
"@AP Checks/Super Missile (Wrecked Ship left)/Room $8F:CDA8", [1346506808] =
"@AP Checks/Super Missile (Wrecked Ship right)/Room $8F:CDF1", [1346506859] =
"@AP Checks/Super Missile (Wrecked Ship-Maridia Connector)/Room $8F:CAAE", [1346506752] =
"@AP Checks/Missile (Draygon)/Room $8F:D72A", [1346506809] = "@AP Checks/Missile (Maridia Main Street)/Room $8F:CFC9",
  [1346506810] = "@AP Checks/Super Missile (Maridia Crab Supers)/Room $8F:CFC9", [1346506811] =
"@AP Checks/Energy Tank (Maridia Turtles)/Room $8F:D055", [1346506812] =
"@AP Checks/Missile (Maridia Turtles)/Room $8F:D055", [1346506813] =
"@AP Checks/Missile (Maridia Map Station Missiles Corridor)/Room $8F:D3B6", [1346506814] =
"@AP Checks/Missile (Maridia Beach Missiles)/Room $8F:D1DD", [1346506815] = "@AP Checks/Plasma Beam/Room $8F:D2AA",
  [1346506816] = "@AP Checks/Spring Ball/Room $8F:D6D0", [1346506817] = "@AP Checks/Space Jump/Room $8F:D913",
  [1346506831] = "@AP Checks/Super Missile (Maridia Watering Hole Supers)/Room $8F:D13B", [1346506832] =
"@AP Checks/Missile (Maridia Watering Hole Missiles)/Room $8F:D13B", [1346506833] =
"@AP Checks/Energy Tank (Botwoon)/Room $8F:D7E4", [1346506850] = "@AP Checks/Missile (Aqueduct Missiles)/Room $8F:D5A7",
  [1346506851] = "@AP Checks/Super Missile (Aqueduct Supers)/Room $8F:D5A7", [1346506852] =
"@AP Checks/Reserve Tank (Maridia Reserves)/Room $8F:D5A7", [1346506853] =
"@AP Checks/Missile (Maridia left sand pit room)/Room $8F:D5A7", [1346506854] =
"@AP Checks/Missile (Maridia right sand pit room)/Room $8F:D5A7", [1346506855] =
"@AP Checks/Power Bomb (Maridia right sand pit room)/Room $8F:D5A7" }
local difficulties = { ["casual"] = 0, ["normal"] = 1, ["speedrunner"] = 2, ["hard"] = 3, ["very_hard"] = 4 }
local tricks = { ["kRCanWallJump"] = 16777216, ["kRCanIBJ"] = 33554432, ["kRCanHeatRun"] = 67108864, ["kRCanMochball"] = 134217728,
  ["kRCanSuperJump"] = 268435456, ["kRCanWaterWJ"] = 536870912, ["kRCanBackflip"] = 1073741824, ["kRGravityHeat"] = 2147483648 }
local seen = {}
local function checked(id)
  local path = locations[id]
  if path then Tracker:FindObjectForCode(path).AvailableChestCount = 0 end
end
function pb_sync_checked_locations()
  local server_checks = {}
  for _, id in ipairs(Archipelago.CheckedLocations or {}) do server_checks[id] = true end
  for id, path in pairs(locations) do
    local section = Tracker:FindObjectForCode(path)
    local remaining = server_checks[id] and 0 or section.ChestCount
    if section.AvailableChestCount ~= remaining then section.AvailableChestCount = remaining end
  end
end

Archipelago:AddClearHandler("Project Base", function(slot_data)
  seen = {}
  for _, code in pairs(items) do
    local item = Tracker:FindObjectForCode(code)
    if item.Type == "consumable" then item.AcquiredCount = 0 else item.Active = false end
  end
  for _, path in pairs(locations) do
    local section = Tracker:FindObjectForCode(path)
    section.AvailableChestCount = section.ChestCount
  end
  local difficulty = slot_data and slot_data.difficulty or "casual"
  assert(difficulties[difficulty] ~= nil, "Unsupported Project Base difficulty: " .. tostring(difficulty))
  Tracker:FindObjectForCode("difficulty").CurrentStage = difficulties[difficulty]
  local custom = slot_data and slot_data.logic_settings
  if custom then
    local s = {
      counts = {
        kRPBLow = 2,
        kREnergyLow = custom.energy_low,
        kREnergyMed = custom.energy_med,
        kREnergyHigh = custom.energy_high,
        kREnergyHeatLow = 5,
        kREnergyHeatHigh = 8
      },
      tricks = {}
    }
    for name, bit in pairs(tricks) do s.tricks[name] = (custom.trick_mask & bit) ~= 0 end
    pb_set_slot_settings(s)
  else
    pb_set_slot_settings(nil)
  end
  pb_sync_checked_locations()
end)
Archipelago:AddItemHandler("Project Base", function(index, id)
  if seen[index] then return end
  seen[index] = true
  local code = items[id]
  if not code then return end
  local item = Tracker:FindObjectForCode(code)
  if item.Type == "consumable" then
    item.AcquiredCount = item.AcquiredCount + 1
  else
    item.Active = true
  end
end)
Archipelago:AddLocationHandler("Project Base", function(id) checked(id) end)
local check_sync_time = 0
ScriptHost:AddOnFrameHandler('Project Base AP check snapshot', function(elapsed)
  check_sync_time = check_sync_time + elapsed
  if check_sync_time < 1 then return end
  check_sync_time = 0
  if AutoTracker:GetConnectionState('AP') == 3 and Archipelago.PlayerNumber and Archipelago.PlayerNumber > 0 then
    pb_sync_checked_locations()
  end
end)
