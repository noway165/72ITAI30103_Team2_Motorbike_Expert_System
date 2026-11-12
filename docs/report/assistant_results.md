# Diagnosis assistant: results

Knowledge base: 73 symptoms, 9 intermediates, 40 faults, 79 rules. 30 scenarios, 10 held-out descriptions. Produced by `python src/evaluate_assistant.py --write`.

## 1. Understanding the rider's description

| Descriptions | Language | Precision | Recall | F1 |
|---|---|---|---|---|
| SE + ET (development) | vi | 1.00 | 0.93 | 0.96 |
| SE + ET (development) | en | 1.00 | 0.95 | 0.97 |
| BT (used for error analysis on 12/11) | vi | 1.00 | 0.93 | 0.96 |
| BT (used for error analysis on 12/11) | en | 1.00 | 0.95 | 0.98 |
| HO (held-out: never used to change nlu.py) | vi | 0.88 | 0.39 | 0.54 |
| HO (held-out: never used to change nlu.py) | en | 0.86 | 0.33 | 0.48 |

## 2. Questions asked and accuracy

| Method | Average questions | Top-1 correct |
|---|---|---|
| Backward chaining, every fault | 39.7 | 30/30 |
| Backward chaining, right subsystem chosen by the rider | 9.0 | – |
| Assistant, no description (information gain only) | 11.0 | 19/30 |
| Assistant, Vietnamese description + information gain | 5.3 | 30/30 |
| Assistant, English description + information gain | 5.3 | 30/30 |

Questions asked by the assistant do not count what was read from the description. All 30 scenario descriptions have now been used while writing nlu.py, so the held-out set below is the fair estimate.

## 3. Per scenario

| Id | Expected fault | Backward (all / right part) | No text | VI text | EN text |
|---|---|---|---|---|---|
| BT01 | worn_brake_pads | 38 / 8 | 15 ✕ | 3 ✓ | 3 ✓ |
| BT02 | worn_brake_pads | 40 / 6 | 15 ✕ | 15 ✓ | 15 ✓ |
| BT03 | brake_fluid_leak | 43 / 9 | 6 ✓ | 0 ✓ | 0 ✓ |
| BT04 | old_brake_fluid | 39 / 9 | 12 ✓ | 9 ✓ | 9 ✓ |
| BT05 | warped_brake_disc | 36 / 6 | 15 ✓ | 15 ✓ | 15 ✓ |
| BT06 | sticking_brake_caliper | 38 / 6 | 15 ✕ | 15 ✓ | 15 ✓ |
| BT07 | underinflated_tyre | 38 / 10 | 7 ✓ | 3 ✓ | 3 ✓ |
| BT08 | tyre_puncture | 38 / 10 | 15 ✓ | 4 ✓ | 6 ✓ |
| BT09 | fork_seal_leak | 40 / 8 | 15 ✕ | 15 ✓ | 15 ✓ |
| BT10 | worn_rear_shock | 41 / 11 | 5 ✓ | 0 ✓ | 0 ✓ |
| ET01 | clogged_air_filter | 42 / 13 | 9 ✓ | 0 ✓ | 0 ✓ |
| ET02 | engine_burning_oil | 37 / 10 | 11 ✓ | 4 ✓ | 4 ✓ |
| ET03 | low_engine_oil | 39 / 10 | 15 ✕ | 0 ✓ | 0 ✓ |
| ET04 | low_coolant | 37 / 10 | 15 ✓ | 6 ✓ | 6 ✓ |
| ET05 | cooling_fan_problem | 37 / 10 | 15 ✕ | 12 ✓ | 12 ✓ |
| ET06 | dirty_throttle_body | 38 / 11 | 15 ✕ | 15 ✓ | 15 ✓ |
| ET07 | worn_cvt_belt | 38 / 7 | 8 ✓ | 1 ✓ | 1 ✓ |
| ET08 | clutch_cable_needs_adjustment | 40 / 9 | 15 ✕ | 15 ✓ | 15 ✓ |
| ET09 | clutch_slipping | 40 / 9 | 15 ✓ | 15 ✓ | 15 ✓ |
| ET10 | chain_needs_lubrication | 38 / 7 | 13 ✓ | 1 ✓ | 1 ✓ |
| SE01 | weak_battery | 41 / 10 | 4 ✓ | 0 ✓ | 0 ✓ |
| SE02 | start_procedure_error | 40 / 9 | 5 ✓ | 0 ✓ | 0 ✓ |
| SE03 | out_of_fuel | 41 / 8 | 4 ✓ | 0 ✓ | 0 ✓ |
| SE04 | flooded_engine | 45 / 11 | 6 ✓ | 1 ✓ | 1 ✓ |
| SE05 | fuel_pump_problem | 43 / 11 | 6 ✓ | 0 ✓ | 0 ✓ |
| SE06 | blown_main_fuse | 41 / 8 | 15 ✕ | 0 ✓ | 0 ✓ |
| SE07 | blown_headlight_bulb | 41 / 7 | 15 ✕ | 7 ✓ | 7 ✓ |
| SE08 | charging_system_problem | 42 / 8 | 4 ✓ | 1 ✓ | 0 ✓ |
| SE09 | spark_plug_problem | 40 / 8 | 15 ✕ | 1 ✓ | 0 ✓ |
| SE10 | weak_battery | 41 / 10 | 4 ✓ | 1 ✓ | 1 ✓ |

## 4. Held-out descriptions (HO)

| Language | Average questions | Top-1 correct |
|---|---|---|
| Vietnamese | 10.5 | 8/10 |
| English | 11.4 | 7/10 |
