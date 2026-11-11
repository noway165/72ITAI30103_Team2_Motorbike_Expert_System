# Evaluation results

Written by `python src/evaluate.py --markdown`; do not edit by hand.

Knowledge base: 73 symptoms, 9 intermediates, 40 faults, 79 rules. Fallback rules: BR13, EN18, SF14, TS15.

## Summary by scenario group

| Group | Scenarios | Top-1 | Top-3 | Top-1, correct part only | Top-1 without fallback rules | Mean CF of expected fault | Questions, all parts | Questions, correct part |
|---|---|---|---|---|---|---|---|---|
| Starting, fuel, electrics (SE) | 10 | 10 (100.0%) | 10 (100.0%) | 10 | 9 | 0.76 | 41.5 | 9.0 |
| Engine, transmission (ET) | 10 | 10 (100.0%) | 10 (100.0%) | 10 | 10 | 0.79 | 38.6 | 9.6 |
| Brakes, tyres, suspension (BT) | 10 | 10 (100.0%) | 10 (100.0%) | 10 | 9 | 0.81 | 39.1 | 8.3 |
| **All** | 30 | 30 (100.0%) | 30 (100.0%) | 30 | 28 | 0.79 | 39.7 | 9.0 |

- Backward chaining gives the same faults and CF as forward chaining on 30/30 scenarios.
- Checking only the correct part needs 4.4 times fewer questions (9.0 instead of 39.7; the knowledge base has 73 symptoms).
- Without the fallback rules, top-1 is 28/30; with them, 30/30.

## Every scenario

| Scenario | Expected fault | Rank | CF | Questions, all parts | Questions, correct part | Rank without fallback rules |
|---|---|---|---|---|---|---|
| BT01 | `worn_brake_pads` | 1 | 0.90 | 38 | 8 | 1 |
| BT02 | `worn_brake_pads` | 1 | 0.85 | 40 | 6 | 1 |
| BT03 | `brake_fluid_leak` | 1 | 0.96 | 43 | 9 | 1 |
| BT04 | `old_brake_fluid` | 1 | 0.70 | 39 | 9 | 1 |
| BT05 | `warped_brake_disc` | 1 | 0.80 | 36 | 6 | 1 |
| BT06 | `sticking_brake_caliper` | 1 | 0.75 | 38 | 6 | 1 |
| BT07 | `underinflated_tyre` | 1 | 0.85 | 38 | 10 | 1 |
| BT08 | `tyre_puncture` | 1 | 0.95 | 38 | 10 | 1 |
| BT09 | `fork_seal_leak` | 1 | 0.85 | 40 | 8 | 1 |
| BT10 | `worn_rear_shock` | 1 | 0.49 | 41 | 11 | not found |
| ET01 | `clogged_air_filter` | 1 | 0.68 | 42 | 13 | 1 |
| ET02 | `engine_burning_oil` | 1 | 0.80 | 37 | 10 | 1 |
| ET03 | `low_engine_oil` | 1 | 0.88 | 39 | 10 | 1 |
| ET04 | `low_coolant` | 1 | 0.96 | 37 | 10 | 1 |
| ET05 | `cooling_fan_problem` | 1 | 0.63 | 37 | 10 | 1 |
| ET06 | `dirty_throttle_body` | 1 | 0.55 | 38 | 11 | 1 |
| ET07 | `worn_cvt_belt` | 1 | 0.86 | 38 | 7 | 1 |
| ET08 | `clutch_cable_needs_adjustment` | 1 | 0.94 | 40 | 9 | 1 |
| ET09 | `clutch_slipping` | 1 | 0.68 | 40 | 9 | 1 |
| ET10 | `chain_needs_lubrication` | 1 | 0.94 | 38 | 7 | 1 |
| SE01 | `weak_battery` | 1 | 0.89 | 41 | 10 | 1 |
| SE02 | `start_procedure_error` | 1 | 0.90 | 40 | 9 | 1 |
| SE03 | `out_of_fuel` | 1 | 0.95 | 41 | 8 | 1 |
| SE04 | `flooded_engine` | 1 | 0.70 | 45 | 11 | 1 |
| SE05 | `fuel_pump_problem` | 1 | 0.75 | 43 | 11 | 1 |
| SE06 | `blown_main_fuse` | 1 | 0.58 | 41 | 8 | 1 |
| SE07 | `blown_headlight_bulb` | 1 | 0.80 | 41 | 7 | 1 |
| SE08 | `charging_system_problem` | 1 | 0.89 | 42 | 8 | 1 |
| SE09 | `spark_plug_problem` | 1 | 0.64 | 40 | 8 | 1 |
| SE10 | `weak_battery` | 1 | 0.54 | 41 | 10 | not found |
