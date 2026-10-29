-- Generated from projectbase.rules
local settings = { ["casual"] = { ["counts"] = { ["kRPBLow"] = 2, ["kREnergyLow"] = 1, ["kREnergyMed"] = 3, ["kREnergyHigh"] = 5, ["kREnergyHeatLow"] = 5, ["kREnergyHeatHigh"] = 8 }, ["tricks"] = { ["kRGravityHeat"] = true } },
  ["normal"] = { ["counts"] = { ["kRPBLow"] = 2, ["kREnergyLow"] = 1, ["kREnergyMed"] = 2, ["kREnergyHigh"] = 3, ["kREnergyHeatLow"] = 5, ["kREnergyHeatHigh"] = 8 }, ["tricks"] = { ["kRCanIBJ"] = true, ["kRCanMochball"] = true, ["kRCanWallJump"] = true } },
  ["speedrunner"] = { ["counts"] = { ["kRPBLow"] = 2, ["kREnergyLow"] = 0, ["kREnergyMed"] = 1, ["kREnergyHigh"] = 2, ["kREnergyHeatLow"] = 5, ["kREnergyHeatHigh"] = 8 }, ["tricks"] = { ["kRCanIBJ"] = true, ["kRCanWallJump"] = true, ["kRCanBackflip"] = true, ["kRCanMochball"] = true, ["kRCanSuperJump"] = true } },
  ["hard"] = { ["counts"] = { ["kRPBLow"] = 2, ["kREnergyLow"] = 0, ["kREnergyMed"] = 0, ["kREnergyHigh"] = 0, ["kREnergyHeatLow"] = 5, ["kREnergyHeatHigh"] = 8 }, ["tricks"] = { ["kRCanWaterWJ"] = true, ["kRCanIBJ"] = true, ["kRCanWallJump"] = true, ["kRCanBackflip"] = true, ["kRCanMochball"] = true, ["kRCanSuperJump"] = true } },
  ["very_hard"] = { ["counts"] = { ["kRPBLow"] = 2, ["kREnergyLow"] = 0, ["kREnergyMed"] = 0, ["kREnergyHigh"] = 0, ["kREnergyHeatLow"] = 5, ["kREnergyHeatHigh"] = 8 }, ["tricks"] = { ["kRCanWaterWJ"] = true, ["kRCanIBJ"] = true, ["kRCanWallJump"] = true, ["kRCanBackflip"] = true, ["kRCanMochball"] = true, ["kRCanHeatRun"] = true, ["kRCanSuperJump"] = true } } }
local difficulties = { "casual", "normal", "speedrunner", "hard", "very_hard" }
local function has(code, count) return Tracker:ProviderCountForCode(code) >= count end
local helpers = {}
local slot_settings, slot_stage
function pb_set_slot_settings(value)
  slot_settings, slot_stage = value, Tracker:FindObjectForCode('difficulty').CurrentStage
  local item = Tracker:FindObjectForCode('difficulty')
  item.CurrentStage = (slot_stage + 1) % #difficulties
  item.CurrentStage = slot_stage -- invalidate cached access even with an empty inventory
end

helpers.kRCanUsePB = function(s) return (has("morph_ball", 1) and has("power_bomb", 1)) end
helpers.kRCanAccessRB = function(s) return helpers.kRCanUsePB(s) end
helpers.kRCanUseBomb = function(s) return (has("morph_ball", 1) and has("bombs", 1)) end
helpers.kRCanSpeedball = function(s) return (has("morph_ball", 1) and has("speed_booster", 1)) end
helpers.kRCanUse2PB = function(s) return (has("morph_ball", 1) and has("power_bomb", s.counts.kRPBLow)) end
helpers.kRCanOpenMissile = function(s) return (has("missile", 1) or has("super_missile", 1)) end
helpers.kRCanAccessWS = function(s) return (((has("super_missile", 1) and helpers.kRCanUsePB(s)) and has("energy_tank", s.counts.kREnergyMed)) and ((has("space_jump", 1) or has("grapple_beam", 1)) or has("speed_booster", 1))) end
helpers.kRGauntlet = function(s) return ((has("hijump_boots", 1) or (s.tricks.kRCanWallJump == true)) and (((has("speed_booster", 1) or helpers.kRCanUseBomb(s)) or helpers.kRCanUse2PB(s)) or has("screw_attack", 1))) end
helpers.kRCanOpenPassages = function(s) return ((helpers.kRCanUseBomb(s) or helpers.kRCanUsePB(s)) or has("screw_attack", 1)) end
helpers.kRCanEnterPassages = function(s) return (helpers.kRCanUseBomb(s) or helpers.kRCanUsePB(s)) end
helpers.kRCanDestroyBomb = function(s) return ((helpers.kRCanEnterPassages(s) or has("screw_attack", 1)) or has("speed_booster", 1)) end
helpers.kRCanAccessGB = function(s) return ((helpers.kRCanEnterPassages(s) or (helpers.kRCanUsePB(s) and has("super_missile", 1))) or (helpers.kRCanOpenMissile(s) and helpers.kRCanUsePB(s))) end
helpers.kRCanAccessPB = function(s) return (((helpers.kRCanEnterPassages(s) and has("super_missile", 1)) or (helpers.kRCanAccessGB(s) and helpers.kRCanOpenMissile(s))) or helpers.kRCanAccessRB(s)) end
helpers.kRCanDefeatKraid = function(s) return (((helpers.kRCanAccessRB(s) and helpers.kRCanEnterPassages(s)) and helpers.kRCanOpenMissile(s)) and has("energy_tank", s.counts.kREnergyLow)) end
helpers.kRCanAccessNorfair = function(s) return (helpers.kRCanAccessRB(s) and ((has("varia_suit", 1) or (has("gravity_suit", 1) and (s.tricks.kRGravityHeat == true))) or ((s.tricks.kRCanHeatRun == true) and has("energy_tank", s.counts.kREnergyHeatLow)))) end
helpers.kRCanAccessLN = function(s) return (((helpers.kRCanAccessNorfair(s) and has("energy_tank", s.counts.kREnergyHigh)) and ((has("varia_suit", 1) or (has("gravity_suit", 1) and (s.tricks.kRGravityHeat == true))) or ((s.tricks.kRCanHeatRun == true) and has("energy_tank", s.counts.kREnergyHeatHigh)))) and (((has("gravity_suit", 1) and has("space_jump", 1)) and has("power_bomb", 1)) or (s.tricks.kRCanBackflip == true))) end
helpers.kRCanAccessIce = function(s) return (helpers.kRCanAccessNorfair(s) and helpers.kRCanUsePB(s)) end
helpers.kRCanAccessCroc = function(s) return (helpers.kRCanAccessNorfair(s) and has("super_missile", 1)) end
helpers.kRCanAccessMaridia = function(s) return (((helpers.kRCanAccessRB(s) and (has("gravity_suit", 1) or (s.tricks.kRCanWaterWJ == true))) and helpers.kRCanUsePB(s)) and has("energy_tank", s.counts.kREnergyHigh)) end
helpers.kRCanAccessAquaduct = function(s) return (helpers.kRCanAccessMaridia(s) and ((has("speed_booster", 1) or has("space_jump", 1)) or has("grapple_beam", 1))) end
helpers.kRCanMeetEtecoons = function(s) return (helpers.kRCanAccessGB(s) and helpers.kRCanUsePB(s)) end
helpers.kRCanDefeatPhantoon = function(s) return ((helpers.kRCanAccessWS(s) and has("charge_beam", 1)) and ((has("gravity_suit", 1) or has("varia_suit", 1)) or has("energy_tank", s.counts.kREnergyLow))) end
helpers.kRCanAccessOuterM = function(s) return (((helpers.kRCanAccessRB(s) and has("power_bomb", 1)) and has("gravity_suit", 1)) and (has("space_jump", 1) or has("hijump_boots", 1))) end
helpers.kRCanAccessInnerM = function(s) return (helpers.kRCanAccessOuterM(s) and ((has("space_jump", 1) or has("grapple_beam", 1)) or has("speed_booster", 1))) end
helpers.kRCanDefeatBotwoon = function(s) return (helpers.kRCanAccessInnerM(s) and (has("ice_beam", 1) or has("speed_booster", 1))) end
helpers.kRCanDefeatDraygon = function(s) return ((helpers.kRCanDefeatBotwoon(s) and has("space_jump", 1)) and has("energy_tank", s.counts.kREnergyLow)) end
helpers.kRCanAccessRBV = function(s) return (has("super_missile", 1) and ((helpers.kRCanDestroyBomb(s) and has("morph_ball", 1)) or helpers.kRCanUsePB(s))) end
helpers.kRCanAccessNorfairV = function(s) return ((helpers.kRCanAccessRBV(s) and (has("space_jump", 1) or has("hijump_boots", 1))) and ((has("varia_suit", 1) or (has("gravity_suit", 1) and (s.tricks.kRGravityHeat == true))) or ((s.tricks.kRCanHeatRun == true) and has("energy_tank", s.counts.kREnergyHeatLow)))) end
helpers.kRCanAccessCrocV = function(s) return (helpers.kRCanAccessNorfairV(s) and ((has("speed_booster", 1) and helpers.kRCanUsePB(s)) or has("wave_beam", 1))) end
local locations = {
  function(s) return (helpers.kRCanAccessAquaduct(s) and ((has("grapple_beam", 1) or has("space_jump", 1)) or (s.tricks.kRCanWallJump == true))) end,
  function(s) return helpers.kRCanAccessNorfair(s) end,
  function(s) return (helpers.kRCanAccessNorfair(s) and (has("hijump_boots", 1) or (s.tricks.kRCanWallJump == true))) end,
  function(s) return ((helpers.kRCanAccessNorfair(s) and helpers.kRCanOpenMissile(s)) and (((has("speed_booster", 1) or has("grapple_beam", 1)) or has("space_jump", 1)) or (helpers.kRCanUseBomb(s) and (s.tricks.kRCanIBJ == true)))) end,
  function(s) return (helpers.kRCanUsePB(s) and ((has("speed_booster", 1) or has("space_jump", 1)) or (helpers.kRCanUseBomb(s) and (s.tricks.kRCanIBJ == true)))) end,
  function(s) return helpers.kRCanAccessWS(s) end,
  function(s) return helpers.kRGauntlet(s) end,
  function(s) return (helpers.kRCanOpenMissile(s) and has("morph_ball", 1)) end,
  function(s) return helpers.kRCanEnterPassages(s) end,
  function(s) return (helpers.kRCanOpenMissile(s) and has("morph_ball", 1)) end,
  function(s) return helpers.kRGauntlet(s) end,
  function(s) return helpers.kRGauntlet(s) end,
  function(s) return (helpers.kRCanUsePB(s) and has("speed_booster", 1)) end,
  function(s) return helpers.kRCanEnterPassages(s) end,
  function(s) return helpers.kRCanMeetEtecoons(s) end,
  function(s) return ((helpers.kRCanAccessGB(s) and helpers.kRCanOpenMissile(s)) and has("morph_ball", 1)) end,
  function(s) return ((helpers.kRCanAccessGB(s) and helpers.kRCanOpenMissile(s)) and ((helpers.kRCanSpeedball(s) or (has("morph_ball", 1) and (s.tricks.kRCanMochball == true))) or (has("morph_ball", 1) and has("dash_ball", 1)))) end,
  function(s) return ((helpers.kRCanAccessGB(s) and helpers.kRCanOpenMissile(s)) and ((helpers.kRCanSpeedball(s) or (has("morph_ball", 1) and (s.tricks.kRCanMochball == true))) or (has("morph_ball", 1) and has("dash_ball", 1)))) end,
  function(s) return (((helpers.kRCanAccessGB(s) and helpers.kRCanOpenMissile(s)) and helpers.kRCanEnterPassages(s)) and ((helpers.kRCanSpeedball(s) or (has("morph_ball", 1) and (s.tricks.kRCanMochball == true))) or (has("morph_ball", 1) and has("dash_ball", 1)))) end,
  function(s) return ((helpers.kRCanAccessGB(s) and helpers.kRCanOpenMissile(s)) and ((helpers.kRCanSpeedball(s) or (has("morph_ball", 1) and (s.tricks.kRCanMochball == true))) or (has("morph_ball", 1) and has("dash_ball", 1)))) end,
  function(s) return (helpers.kRCanAccessPB(s) and (((has("grapple_beam", 1) or has("space_jump", 1)) or has("speed_booster", 1)) or (s.tricks.kRCanWallJump == true))) end,
  function(s) return helpers.kRCanAccessPB(s) end,
  function(s) return helpers.kRCanAccessPB(s) end,
  function(s) return (helpers.kRCanAccessPB(s) or helpers.kRCanEnterPassages(s)) end,
  function(s) return true end,
  function(s) return helpers.kRCanUsePB(s) end,
  function(s) return ((helpers.kRCanAccessPB(s) and helpers.kRCanUsePB(s)) and has("speed_booster", 1)) end,
  function(s) return (helpers.kRCanAccessPB(s) and helpers.kRCanUsePB(s)) end,
  function(s) return ((helpers.kRCanAccessRB(s) and has("super_missile", 1)) and helpers.kRCanUsePB(s)) end,
  function(s) return (helpers.kRCanAccessRB(s) and has("super_missile", 1)) end,
  function(s) return (helpers.kRCanAccessRB(s) and helpers.kRCanDestroyBomb(s)) end,
  function(s) return (helpers.kRCanAccessRB(s) and has("super_missile", 1)) end,
  function(s) return (helpers.kRCanAccessWS(s) and ((has("speed_booster", 1) or has("grapple_beam", 1)) or has("space_jump", 1))) end,
  function(s) return (helpers.kRCanAccessWS(s) and ((has("speed_booster", 1) or has("grapple_beam", 1)) or has("space_jump", 1))) end,
  function(s) return (helpers.kRCanAccessWS(s) and ((has("speed_booster", 1) or has("grapple_beam", 1)) or has("space_jump", 1))) end,
  function(s) return helpers.kRCanAccessIce(s) end,
  function(s) return (helpers.kRCanAccessCroc(s) and ((has("speed_booster", 1) or has("grapple_beam", 1)) or has("space_jump", 1))) end,
  function(s) return (helpers.kRCanAccessRB(s) and helpers.kRCanEnterPassages(s)) end,
  function(s) return (helpers.kRCanAccessRB(s) and helpers.kRCanEnterPassages(s)) end,
  function(s) return (helpers.kRCanAccessRB(s) and helpers.kRCanEnterPassages(s)) end,
  function(s) return helpers.kRCanAccessNorfair(s) end,
  function(s) return ((helpers.kRCanAccessNorfair(s) and helpers.kRCanOpenMissile(s)) or (helpers.kRCanAccessNorfair(s) and helpers.kRCanUsePB(s))) end,
  function(s) return ((helpers.kRCanAccessNorfair(s) and helpers.kRCanUsePB(s)) and has("charge_beam", 1)) end,
  function(s) return ((helpers.kRCanAccessNorfair(s) and helpers.kRCanUsePB(s)) and has("charge_beam", 1)) end,
  function(s) return (helpers.kRCanAccessLN(s) and helpers.kRCanEnterPassages(s)) end,
  function(s) return (helpers.kRCanAccessLN(s) and helpers.kRCanEnterPassages(s)) end,
  function(s) return (helpers.kRCanAccessLN(s) and helpers.kRCanEnterPassages(s)) end,
  function(s) return (helpers.kRCanAccessLN(s) and helpers.kRCanEnterPassages(s)) end,
  function(s) return (helpers.kRCanAccessLN(s) and helpers.kRCanEnterPassages(s)) end,
  function(s) return (helpers.kRCanAccessLN(s) and helpers.kRCanUsePB(s)) end,
  function(s) return ((helpers.kRCanAccessLN(s) and has("super_missile", 1)) and (has("space_jump", 1) or (s.tricks.kRCanWallJump == true))) end,
  function(s) return helpers.kRCanAccessWS(s) end,
  function(s) return helpers.kRCanAccessWS(s) end,
  function(s) return (helpers.kRCanAccessWS(s) and ((has("grapple_beam", 1) or has("space_jump", 1)) or (s.tricks.kRCanWallJump == true))) end,
  function(s) return (helpers.kRCanAccessWS(s) and ((has("ice_beam", 1) or has("hijump_boots", 1)) or has("space_jump", 1))) end,
  function(s) return helpers.kRCanAccessWS(s) end,
  function(s) return helpers.kRCanAccessWS(s) end,
  function(s) return ((helpers.kRCanAccessRB(s) and has("gravity_suit", 1)) and has("speed_booster", 1)) end,
  function(s) return helpers.kRCanAccessMaridia(s) end,
  function(s) return (helpers.kRCanAccessMaridia(s) and ((has("space_jump", 1) or has("grapple_beam", 1)) or has("speed_booster", 1))) end,
  function(s) return helpers.kRCanAccessMaridia(s) end,
  function(s) return helpers.kRCanAccessRB(s) end,
  function(s) return (helpers.kRCanAccessMaridia(s) and ((((has("hijump_boots", 1) or has("space_jump", 1)) or has("gravity_suit", 1)) or ((s.tricks.kRCanIBJ == true) and helpers.kRCanUseBomb(s))) or ((s.tricks.kRCanSuperJump == true) and has("super_missile", 1)))) end,
  function(s) return helpers.kRCanAccessMaridia(s) end,
  function(s) return (helpers.kRCanAccessMaridia(s) and (has("space_jump", 1) or (s.tricks.kRCanWallJump == true))) end,
  function(s) return (helpers.kRCanAccessAquaduct(s) and ((has("grapple_beam", 1) or has("space_jump", 1)) or (s.tricks.kRCanWallJump == true))) end,
  function(s) return ((helpers.kRCanAccessLN(s) and helpers.kRCanUsePB(s)) and has("super_missile", 1)) end,
  function(s) return has("morph_ball", 1) end,
  function(s) return (has("morph_ball", 1) and helpers.kRCanOpenMissile(s)) end,
  function(s) return helpers.kRCanOpenMissile(s) end,
  function(s) return ((helpers.kRCanOpenMissile(s) and has("morph_ball", 1)) and ((has("space_jump", 1) or (s.tricks.kRCanWallJump == true)) or (has("bombs", 1) and (s.tricks.kRCanIBJ == true)))) end,
  function(s) return (helpers.kRCanOpenMissile(s) and has("morph_ball", 1)) end,
  function(s) return (helpers.kRCanOpenMissile(s) and (((has("hijump_boots", 1) or has("space_jump", 1)) or has("speed_booster", 1)) or (helpers.kRCanUseBomb(s) and (s.tricks.kRCanIBJ == true)))) end,
  function(s) return helpers.kRCanAccessWS(s) end,
  function(s) return helpers.kRCanAccessWS(s) end,
  function(s) return helpers.kRCanAccessWS(s) end,
  function(s) return ((helpers.kRCanAccessRB(s) and helpers.kRCanEnterPassages(s)) or helpers.kRCanAccessCroc(s)) end,
  function(s) return (helpers.kRCanAccessRB(s) or (helpers.kRCanAccessCroc(s) and helpers.kRCanEnterPassages(s))) end,
  function(s) return (helpers.kRCanAccessRB(s) and helpers.kRCanDefeatKraid(s)) end,
  function(s) return (helpers.kRCanAccessMaridia(s) and has("hijump_boots", 1)) end,
  function(s) return (helpers.kRCanAccessMaridia(s) and has("hijump_boots", 1)) end,
  function(s) return (helpers.kRCanAccessAquaduct(s) and helpers.kRCanEnterPassages(s)) end,
  function(s) return ((helpers.kRCanAccessPB(s) and helpers.kRCanUsePB(s)) and (((has("grapple_beam", 1) or has("space_jump", 1)) or has("speed_booster", 1)) or (s.tricks.kRCanWallJump == true))) end,
  function(s) return (helpers.kRCanAccessPB(s) and has("super_missile", 1)) end,
  function(s) return (has("morph_ball", 1) and ((has("bombs", 1) or has("power_bomb", 1)) or has("screw_attack", 1))) end,
  function(s) return helpers.kRCanMeetEtecoons(s) end,
  function(s) return (helpers.kRCanAccessCroc(s) or (helpers.kRCanAccessRB(s) and helpers.kRCanEnterPassages(s))) end,
  function(s) return helpers.kRCanAccessNorfair(s) end,
  function(s) return ((helpers.kRCanAccessNorfair(s) and has("super_missile", 1)) and ((has("grapple_beam", 1) or (s.tricks.kRCanWallJump == true)) or (helpers.kRCanUseBomb(s) and (s.tricks.kRCanIBJ == true)))) end,
  function(s) return ((helpers.kRCanAccessNorfair(s) and has("super_missile", 1)) and ((has("grapple_beam", 1) or (s.tricks.kRCanWallJump == true)) or (helpers.kRCanUseBomb(s) and (s.tricks.kRCanIBJ == true)))) end,
  function(s) return ((helpers.kRCanAccessNorfair(s) and has("super_missile", 1)) and ((has("grapple_beam", 1) or (s.tricks.kRCanWallJump == true)) or (helpers.kRCanUseBomb(s) and (s.tricks.kRCanIBJ == true)))) end,
  function(s) return (helpers.kRCanAccessGB(s) and helpers.kRCanOpenMissile(s)) end,
  function(s) return helpers.kRCanMeetEtecoons(s) end,
  function(s) return (helpers.kRCanAccessRB(s) and helpers.kRCanDefeatKraid(s)) end,
  function(s) return (helpers.kRCanAccessRB(s) and helpers.kRCanDefeatKraid(s)) end,
  function(s) return ((((has("speed_booster", 1) or has("grapple_beam", 1)) or has("space_jump", 1)) and (helpers.kRCanAccessIce(s) and helpers.kRCanEnterPassages(s))) or helpers.kRCanAccessCroc(s)) end,
  function(s) return ((((has("speed_booster", 1) or has("grapple_beam", 1)) or has("space_jump", 1)) and (helpers.kRCanAccessIce(s) and helpers.kRCanEnterPassages(s))) or helpers.kRCanAccessCroc(s)) end,
  function(s) return helpers.kRCanAccessRB(s) end,
  function(s) return ((helpers.kRCanAccessAquaduct(s) and has("speed_booster", 1)) and has("gravity_suit", 1)) end,
  function(s) return ((helpers.kRCanAccessAquaduct(s) and has("speed_booster", 1)) and has("gravity_suit", 1)) end,
  function(s) return helpers.kRCanAccessAquaduct(s) end,
  function(s) return helpers.kRCanAccessAquaduct(s) end,
  function(s) return helpers.kRCanAccessAquaduct(s) end,
  function(s) return helpers.kRCanAccessAquaduct(s) end,
  function(s) return ((((helpers.kRCanAccessPB(s) and has("super_missile", 1)) and has("morph_ball", 1)) and has("grapple_beam", 1)) or ((has("grapple_beam", 1) and helpers.kRCanAccessRB(s)) and helpers.kRCanUsePB(s))) end,
  function(s) return ((helpers.kRCanAccessRB(s) and helpers.kRCanUsePB(s)) and has("super_missile", 1)) end,
  function(s) return (has("super_missile", 1) and has("morph_ball", 1)) end,
  function(s) return ((helpers.kRCanAccessWS(s) and has("super_missile", 1)) and has("morph_ball", 1)) end,
  function(s) return ((helpers.kRCanAccessRB(s) and helpers.kRCanUsePB(s)) and has("super_missile", 1)) end,
}
function pb_location(index)
  local rule = locations[tonumber(index)]
  if not rule then return false end
  if slot_settings and Tracker:FindObjectForCode('difficulty').CurrentStage == slot_stage then
    return rule(slot_settings)
  end
  for _, name in ipairs(difficulties) do
    if Tracker:ProviderCountForCode("difficulty_" .. name) > 0 then
      return rule(settings[name])
    end
  end
  return rule(settings.casual)
end
