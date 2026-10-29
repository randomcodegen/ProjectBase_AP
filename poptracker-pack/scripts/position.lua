local rooms = { [35280] = { 0, 21, 9, 4, 8 }, [37368] = { 0, 23, 0, 9, 5 }, [37555] = { 0, 24, 17, 2, 8 }, [37629] = { 0, 18, 4, 5, 5 },
  [37802] = { 0, 32, 1, 2, 1 }, [37845] = { 0, 18, 6, 1, 1 }, [37886] = { 0, 37, 0, 8, 6 }, [37985] = { 0, 40, 2, 2, 1 },
  [38028] = { 0, 32, 4, 3, 3 }, [38092] = { 0, 57, 10, 1, 8 }, [38141] = { 0, 54, 0, 7, 6 }, [38226] = { 0, 58, 4, 4, 9 },
  [38269] = { 0, 26, 16, 4, 2 }, [38312] = { 0, 30, 16, 3, 1 }, [38356] = { 0, 45, 10, 12, 1 }, [38399] = { 0, 35, 4, 2, 5 },
  [38491] = { 0, 12, 2, 11, 1 }, [38543] = { 0, 33, 16, 3, 1 }, [38586] = { 0, 18, 9, 3, 9 }, [38748] = { 0, 20, 17, 3, 2 },
  [38837] = { 0, 23, 17, 1, 8 }, [38916] = { 0, 25, 6, 1, 1 }, [39033] = { 0, 22, 6, 3, 1 }, [39138] = { 0, 36, 16, 15, 1 },
  [39181] = { 0, 12, 4, 6, 3 }, [39224] = { 0, 6, 8, 1, 10 }, [39273] = { 0, 7, 8, 4, 1 }, [39316] = { 0, 20, 7, 5, 2 },
  [39357] = { 0, 11, 2, 1, 7 }, [39492] = { 0, 17, 7, 2, 1 }, [39568] = { 0, 16, 7, 1, 1 }, [39641] = { 1, 9, 0, 4, 12 },
  [39771] = { 1, 23, 1, 3, 9 }, [39837] = { 0, 51, 13, 11, 4 }, [39880] = { 1, 10, 3, 3, 2 }, [39943] = { 1, 13, 4, 2, 1 },
  [39989] = { 1, 5, 4, 4, 6 }, [40030] = { 1, 4, 4, 1, 15 }, [40073] = { 1, 5, 7, 1, 1 }, [40115] = { 1, 10, 6, 7, 7 },
  [40201] = { 1, 1, 1, 1, 1 }, [40217] = { 1, 15, 4, 5, 10 }, [40348] = { 1, 19, 4, 4, 1 }, [40391] = { 1, 22, 1, 1, 3 },
  [40465] = { 1, 20, 18, 13, 1 }, [40530] = { 1, 19, 10, 8, 4 }, [40607] = { 1, 21, 8, 8, 3 }, [40721] = { 1, 5, 18, 15, 1 },
  [40804] = { 1, 29, 8, 4, 4 }, [40890] = { 1, 27, 13, 6, 1 }, [40933] = { 1, 8, 10, 1, 1 }, [40977] = { 1, 5, 10, 6, 2 },
  [41041] = { 1, 5, 10, 1, 1 }, [41083] = { 1, 9, 12, 1, 1 }, [41124] = { 1, 20, 9, 3, 1 }, [41170] = { 1, 8, 13, 7, 1 },
  [41223] = { 1, 23, 11, 6, 1 }, [41264] = { 1, 19, 7, 2, 2 }, [41307] = { 1, 21, 8, 1, 1 }, [41348] = { 1, 15, 4, 1, 1 },
  [41389] = { 1, 55, 20, 4, 1 }, [41432] = { 1, 29, 8, 1, 1 }, [41473] = { 1, 8, 5, 1, 1 }, [41514] = { 1, 5, 11, 1, 1 },
  [41555] = { 1, 33, 9, 1, 10 }, [41619] = { 1, 25, 15, 8, 2 }, [41678] = { 1, 18, 11, 7, 5 }, [41719] = { 1, 34, 9, 3, 1 },
  [41762] = { 1, 37, 4, 3, 8 }, [41852] = { 1, 35, 7, 2, 2 }, [41902] = { 1, 34, 11, 3, 1 }, [41949] = { 1, 34, 12, 4, 7 },
  [41992] = { 1, 36, 17, 2, 2 }, [42055] = { 1, 38, 17, 1, 1 }, [42097] = { 1, 42, 18, 13, 3 }, [42161] = { 1, 43, 19, 1, 1 },
  [42202] = { 1, 45, 18, 4, 2 }, [42273] = { 1, 47, 19, 6, 1 }, [42347] = { 1, 53, 18, 2, 2 }, [42399] = { 1, 55, 18, 2, 2 },
  [42477] = { 0, 12, 8, 5, 1 }, [42520] = { 1, 32, 18, 1, 1 }, [42561] = { 1, 54, 18, 1, 1 }, [42602] = { 0, 17, 8, 1, 2 },
  [42722] = { 1, 57, 19, 1, 1 }, [42763] = { 1, 49, 18, 1, 1 }, [42804] = { 1, 38, 8, 1, 1 }, [42845] = { 2, 4, 3, 2, 1 },
  [42888] = { 2, 11, 2, 11, 3 }, [42931] = { 2, 11, 3, 3, 2 }, [42974] = { 2, 10, 0, 1, 7 }, [43029] = { 2, 3, 1, 7, 4 },
  [43109] = { 2, 4, 1, 2, 1 }, [43152] = { 2, 5, 2, 1, 1 }, [43193] = { 2, 3, 1, 2, 3 }, [43256] = { 2, 2, 4, 1, 4 },
  [43299] = { 2, 3, 7, 13, 3 }, [43405] = { 2, 12, 10, 8, 1 }, [43493] = { 2, 7, 6, 1, 1 }, [43534] = { 2, 11, 6, 4, 2 },
  [43585] = { 2, 8, 5, 2, 2 }, [43650] = { 2, 9, 10, 4, 2 }, [43701] = { 2, 12, 11, 1, 1 }, [43742] = { 2, 9, 10, 1, 1 },
  [43783] = { 2, 10, 12, 1, 5 }, [43835] = { 2, 11, 15, 4, 1 }, [43876] = { 2, 4, 12, 8, 6 }, [43919] = { 2, 4, 15, 8, 3 },
  [43986] = { 2, 6, 12, 1, 3 }, [44032] = { 2, 4, 14, 2, 1 }, [44075] = { 2, 2, 4, 2, 13 }, [44122] = { 2, 18, 2, 2, 1 },
  [44163] = { 2, 20, 2, 2, 1 }, [44211] = { 2, 22, 2, 2, 4 }, [44272] = { 2, 25, 1, 12, 2 }, [44315] = { 2, 37, 2, 1, 1 },
  [44382] = { 2, 22, 1, 8, 6 }, [44461] = { 2, 25, 4, 4, 2 }, [44510] = { 2, 29, 4, 1, 1 }, [44551] = { 2, 25, 6, 4, 1 },
  [44594] = { 2, 27, 6, 3, 3 }, [44660] = { 2, 25, 8, 2, 3 }, [44724] = { 2, 23, 8, 3, 1 }, [44767] = { 2, 22, 6, 1, 3 },
  [44820] = { 2, 22, 10, 4, 3 }, [44863] = { 2, 21, 10, 1, 1 }, [44914] = { 2, 11, 5, 12, 4 }, [44963] = { 2, 17, 4, 5, 1 },
  [45006] = { 2, 16, 9, 10, 1 }, [45051] = { 2, 21, 9, 4, 1 }, [45094] = { 2, 20, 9, 1, 1 }, [45137] = { 2, 23, 7, 1, 1 },
  [45178] = { 2, 24, 1, 1, 2 }, [45236] = { 2, 9, 4, 1, 1 }, [45277] = { 2, 21, 3, 1, 1 }, [45318] = { 2, 12, 5, 8, 1 },
  [45369] = { 2, 19, 6, 1, 3 }, [45415] = { 2, 11, 5, 1, 1 }, [45458] = { 2, 16, 8, 1, 1 }, [45499] = { 2, 20, 10, 1, 1 },
  [45541] = { 2, 15, 13, 3, 3 }, [45622] = { 2, 17, 11, 8, 3 }, [45699] = { 2, 18, 15, 2, 2 }, [45786] = { 2, 21, 14, 4, 1 },
  [45829] = { 2, 21, 15, 1, 1 }, [45870] = { 2, 23, 16, 1, 2 }, [45946] = { 2, 24, 16, 3, 1 }, [45989] = { 2, 25, 12, 1, 3 },
  [46049] = { 2, 26, 11, 1, 1 }, [46090] = { 2, 26, 9, 4, 4 }, [46167] = { 2, 26, 14, 4, 1 }, [46210] = { 2, 27, 16, 3, 1 },
  [46253] = { 2, 30, 9, 1, 6 }, [46309] = { 2, 31, 9, 4, 5 }, [46352] = { 2, 33, 5, 5, 2 }, [46426] = { 2, 37, 6, 1, 1 },
  [46469] = { 2, 35, 9, 3, 5 }, [46549] = { 2, 32, 14, 6, 3 }, [46635] = { 2, 30, 16, 3, 1 }, [46678] = { 2, 29, 3, 4, 3 },
  [46744] = { 2, 22, 17, 1, 1 }, [46785] = { 2, 20, 14, 1, 3 }, [46830] = { 2, 35, 6, 3, 6 }, [46913] = { 2, 36, 12, 1, 1 },
  [51598] = { 3, 9, 11, 6, 3 }, [51720] = { 3, 11, 14, 4, 3 }, [51794] = { 3, 11, 10, 10, 1 }, [51886] = { 3, 19, 17, 5, 3 },
  [51958] = { 3, 11, 11, 6, 8 }, [52107] = { 3, 18, 15, 2, 1 }, [52181] = { 3, 20, 13, 1, 3 }, [52263] = { 3, 17, 13, 3, 2 },
  [52335] = { 3, 11, 19, 7, 1 }, [52427] = { 3, 11, 17, 1, 2 }, [52499] = { 3, 18, 19, 1, 1 }, [52572] = { 3, 16, 15, 4, 1 },
  [52648] = { 3, 14, 17, 1, 1 }, [52721] = { 3, 17, 17, 4, 1 }, [52800] = { 3, 9, 13, 1, 1 }, [52874] = { 3, 16, 14, 1, 1 },
  [52946] = { 4, 12, 19, 1, 1 }, [52987] = { 4, 11, 17, 1, 3 }, [53076] = { 4, 10, 18, 1, 1 }, [53120] = { 4, 12, 17, 4, 2 },
  [53193] = { 4, 10, 9, 3, 8 }, [53271] = { 4, 13, 13, 4, 3 }, [53333] = { 4, 17, 12, 3, 4 }, [53386] = { 4, 12, 16, 4, 1 },
  [53433] = { 4, 12, 9, 6, 4 }, [53508] = { 4, 12, 7, 3, 2 }, [53563] = { 4, 12, 4, 2, 3 }, [53613] = { 4, 14, 4, 4, 2 },
  [53667] = { 4, 18, 7, 2, 4 }, [53725] = { 4, 18, 4, 4, 3 }, [53788] = { 4, 16, 16, 1, 2 }, [53842] = { 4, 17, 16, 1, 1 },
  [53886] = { 4, 28, 2, 6, 1 }, [53930] = { 4, 26, 0, 2, 3 }, [53977] = { 4, 26, 5, 8, 1 }, [54027] = { 4, 34, 0, 1, 6 },
  [54080] = { 4, 22, 2, 4, 6 }, [54151] = { 4, 25, 0, 1, 4 }, [54198] = { 4, 17, 17, 14, 1 }, [54239] = { 4, 35, 4, 1, 1 },
  [54280] = { 4, 22, 5, 1, 10 }, [54323] = { 4, 26, 5, 1, 1 }, [54369] = { 4, 18, 16, 4, 1 }, [54414] = { 4, 22, 15, 1, 2 },
  [54466] = { 4, 23, 16, 3, 1 }, [54511] = { 4, 20, 14, 2, 2 }, [54558] = { 4, 23, 14, 2, 2 }, [54605] = { 2, 22, 15, 1, 2 },
  [54650] = { 0, 44, 6, 1, 5 }, [54695] = { 4, 20, 9, 6, 7 }, [54764] = { 4, 26, 7, 1, 1 }, [54807] = { 4, 20, 8, 4, 1 },
  [54854] = { 4, 26, 13, 2, 4 }, [54938] = { 2, 12, 17, 10, 1 }, [54992] = { 4, 32, 15, 2, 2 }, [55037] = { 4, 26, 10, 4, 1 },
  [55082] = { 4, 33, 6, 10, 4 }, [55141] = { 4, 19, 11, 1, 1 }, [55268] = { 4, 26, 8, 7, 1 }, [55322] = { 4, 41, 6, 1, 1 },
  [55365] = { 4, 38, 8, 1, 1 }, [55406] = { 2, 20, 10, 1, 1 }, [55448] = { 1, 58, 17, 1, 3 }, [55493] = { 4, 28, 15, 4, 1 },
  [55571] = { 4, 26, 10, 13, 1 }, [55646] = { 4, 24, 8, 2, 1 }, [55722] = { 4, 30, 10, 9, 1 }, [55764] = { 4, 42, 6, 1, 1 },
  [55806] = { 4, 27, 6, 1, 2 }, [55851] = { 4, 26, 6, 7, 2 }, [55904] = { 4, 39, 9, 2, 2 }, [55982] = { 5, 28, 9, 1, 4 },
  [56033] = { 5, 13, 12, 15, 1 }, [56113] = { 5, 12, 12, 1, 2 }, [56189] = { 5, 13, 13, 15, 1 }, [56269] = { 5, 28, 13, 1, 2 },
  [56345] = { 5, 14, 15, 15, 1 }, [56421] = { 5, 12, 15, 2, 1 }, [56497] = { 5, 8, 15, 4, 1 }, [56575] = { 5, 7, 15, 1, 2 },
  [56622] = { 5, 6, 16, 1, 1 }, [56664] = { 5, 21, 18, 4, 1 }, [56772] = { 5, 8, 16, 15, 1 }, [56819] = { 5, 23, 16, 3, 3 },
  [56867] = { 5, 24, 17, 1, 1 }, [56909] = { 5, 19, 18, 2, 1 }, [56954] = { 5, 19, 19, 1, 2 }, [56999] = { 5, 20, 19, 6, 2 },
  [57054] = { 5, 26, 16, 3, 6 }, [57115] = { 5, 29, 12, 1, 1 } }
local geometry = { ["cell"] = 48, ["origin"] = { 450, 160 }, ["areas"] = { { ["x"] = { { 0, 0 }, { 64, 64 } }, ["y"] = { { 0, 0 }, { 64, 64 } }, ["source_min"] = { 6, 0 } }, { ["x"] = { { 0, -3 }, { 64, 61 } }, ["y"] = { { 0, 18 }, { 1, 19 }, { 8, 25 }, { 21, 39 } }, ["source_min"] = { 1, 0 } }, { ["x"] = { { 0, 28 }, { 64, 92 } }, ["y"] = { { 0, 38 }, { 64, 102 } }, ["source_min"] = { 2, 0 } }, { ["x"] = { { 9, 43 }, { 11, 45 }, { 21, 54 }, { 23.5, 57.5 }, { 24, 58 } }, ["y"] = { { 0, -10 }, { 64, 54 } }, ["source_min"] = { 9, 10 } }, { ["x"] = { { 10, 35 }, { 12, 37 }, { 31, 55 }, { 34.5, 57.5 } }, ["y"] = { { 0, 18 }, { 7.5, 24.57142857142857 }, { 17.5, 35.230769230769226 }, { 18.5, 36.30769230769231 } }, ["source_min"] = { 9, 0 } }, { ["x"] = { { 0, -11 }, { 64, 53 } }, ["y"] = { { 9, 10 }, { 17.5, 17.5 } }, ["source_min"] = { 6, 9 } } } }
local areas = { "Crateria", "Brinstar", "Norfair", "Wrecked Ship", "Maridia", "Tourian" }

local last_area, last_screen, selected_pin
local zoom_levels = { false, '0.5', '1.0', '1.5', '2.0', '3.0', '4.0' }
local function interpolate(points, value)
  local left, right = points[1], points[2]
  for i = 2, #points do
    left, right = points[i - 1], points[i]
    if value <= right[1] then break end
  end
  return left[2] + (value - left[1]) * (right[2] - left[2]) / (right[1] - left[1])
end

local function set_pin(value)
  if selected_pin == value then return end
  selected_pin = value
  local tick = Tracker:FindObjectForCode('position_tick')
  tick.CurrentStage = (tick.CurrentStage + 1) % 2 -- invalidate cached map visibility
end
local function invalidate()
  last_area, last_screen = nil, nil
  set_pin(nil)
end
function pb_samus_here(room, x, y)
  return selected_pin ~= nil and selected_pin == room .. ':' .. x .. ':' .. y
end

function pb_position_update()
  local follow = Tracker:FindObjectForCode('follow_samus').Active
  local area_tabs = Tracker:FindObjectForCode('auto_area').Active
  local marker = Tracker:FindObjectForCode('show_samus').Active
  if not marker then set_pin(nil) end
  if not follow and not area_tabs and not marker then return true end
  if AutoTracker:GetConnectionState('SNES') ~= 3 then
    invalidate()
    return false
  end
  -- bus addresses are translated by PopTracker's lorom backend
  local title = ''
  for i = 0, 5 do title = title .. string.char(AutoTracker:ReadU8(0x80FFC0 + i)) end
  if title ~= 'PBAP02' then
    invalidate(); return false
  end
  local mode = AutoTracker:ReadU16(0x7E0998)
  if mode ~= 8 and mode ~= 0x0F then
    if mode < 0x0C or mode > 0x12 then invalidate() end -- keep the last pin while paused
    return false
  end
  local id = AutoTracker:ReadU16(0x7E079B)
  local area = AutoTracker:ReadU16(0x7E079F)
  local room = rooms[id]
  if not room or room[1] ~= area then
    invalidate(); return false
  end
  local x, y = AutoTracker:ReadU16(0x7E0AF6), AutoTracker:ReadU16(0x7E0AFA)
  if x >= room[4] * 256 or y >= room[5] * 256 then
    invalidate(); return false
  end
  local sx, sy = math.floor(x / 256), math.floor(y / 256)
  local screen = tostring(id) .. ':' .. sx .. ':' .. sy
  if marker then
    local section = Tracker:FindObjectForCode('@Samus position/Samus - ' .. areas[area + 1]
      .. ' room ' .. string.format('%04X', id) .. '/Position indicator (not an AP check)')
    section.Highlight = Highlight.Priority
    set_pin(screen)
  end
  if follow then
    if screen ~= last_screen then
      local axes = geometry.areas[area + 1]
      local px = geometry.origin[1] + geometry.cell * interpolate(axes.x, room[2] + sx + 0.5)
      local py = geometry.origin[2] + geometry.cell * interpolate(axes.y, room[3] + sy + 0.5)
      Tracker:UiHint('ActivateTab', 'Full Map')
      local zoom = zoom_levels[Tracker:FindObjectForCode('follow_zoom').CurrentStage + 1]
      if zoom then Tracker:UiHint('Zoom full-map', zoom) end
      Tracker:UiHint('Pan full-map', tostring(px) .. ',' .. tostring(py))
      last_screen = screen
    end
  elseif area_tabs and area ~= last_area then
    Tracker:UiHint('ActivateTab', areas[area + 1])
    last_area = area
  end
  return true
end

local function changed_setting()
  last_area, last_screen = nil, nil
  pb_position_update()
end
function autotracker_started() changed_setting() end

function autotracker_stopped() invalidate() end

local anchor = Tracker:FindObjectForCode('position_anchor')
anchor.IgnoreUserInput = true -- block clicks
anchor.Active = false
Tracker:FindObjectForCode('position_tick').IgnoreUserInput = true
for _, code in ipairs({ 'auto_area', 'follow_samus', 'show_samus', 'follow_zoom' }) do
  ScriptHost:AddWatchForCode('pb_' .. code, code, changed_setting)
end
ScriptHost:AddMemoryWatch('PB ROM identity', 0x80FFC0, 21, pb_position_update, 250)
ScriptHost:AddMemoryWatch('PB room and game state', 0x7E079B, 0x200, pb_position_update, 250)
ScriptHost:AddMemoryWatch('PB Samus position', 0x7E0AF6, 6, pb_position_update, 250)
local elapsed = 0
ScriptHost:AddOnFrameHandler('PB position refresh', function(dt)
  elapsed = elapsed + dt
  if elapsed < 0.25 then return end
  elapsed = 0
  pb_position_update()
end)
