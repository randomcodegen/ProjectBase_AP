-- Inventory Screen Updating
function pb_inventory_update()
  local suit = Tracker:FindObjectForCode('inventory_samus')
  local stage = Tracker:FindObjectForCode('gravity_suit').Active and 2
      or Tracker:FindObjectForCode('varia_suit').Active and 1 or 0
  if suit.CurrentStage ~= stage then suit.CurrentStage = stage end
  do
    local item = Tracker:FindObjectForCode('energy_tank'); item:SetOverlay(tostring(0 + item.AcquiredCount * 1))
  end
  do
    local item = Tracker:FindObjectForCode('missile'); item:SetOverlay(tostring(0 + item.AcquiredCount * 5))
  end
  do
    local item = Tracker:FindObjectForCode('super_missile'); item:SetOverlay(tostring(0 + item.AcquiredCount * 5))
  end
  do
    local item = Tracker:FindObjectForCode('power_bomb'); item:SetOverlay(tostring(0 + item.AcquiredCount * 5))
  end
  do
    local item = Tracker:FindObjectForCode('reserve_tank'); item:SetOverlay(tostring(0 + item.AcquiredCount * 100))
  end
end

ScriptHost:AddWatchForCode('inventory_varia_suit', 'varia_suit', pb_inventory_update)
ScriptHost:AddWatchForCode('inventory_gravity_suit', 'gravity_suit', pb_inventory_update)
ScriptHost:AddWatchForCode('inventory_energy_tank', 'energy_tank', pb_inventory_update)
ScriptHost:AddWatchForCode('inventory_missile', 'missile', pb_inventory_update)
ScriptHost:AddWatchForCode('inventory_super_missile', 'super_missile', pb_inventory_update)
ScriptHost:AddWatchForCode('inventory_power_bomb', 'power_bomb', pb_inventory_update)
ScriptHost:AddWatchForCode('inventory_reserve_tank', 'reserve_tank', pb_inventory_update)
Tracker:FindObjectForCode('inventory_samus').IgnoreUserInput = true
pb_inventory_update()
