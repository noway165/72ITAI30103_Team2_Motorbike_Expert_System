# Diagnosis assistant: results

Knowledge base: 79 symptoms, 9 intermediates, 40 faults, 88 rules. 30 scenarios, 10 held-out descriptions, 9 bike-model scenarios. Produced by `python src/evaluate_assistant.py --write`.

## 1. Understanding the rider's description

| Descriptions | Language | Precision | Recall | F1 |
|---|---|---|---|---|
| SE + ET (development) | vi | 0.89 | 0.93 | 0.91 |
| SE + ET (development) | en | 0.89 | 0.95 | 0.92 |
| BT (used for error analysis on 12/11) | vi | 0.87 | 0.93 | 0.90 |
| BT (used for error analysis on 12/11) | en | 0.85 | 0.93 | 0.89 |
| HO (held-out: never used to change nlu.py) | vi | 0.88 | 0.39 | 0.54 |
| HO (held-out: never used to change nlu.py) | en | 0.86 | 0.33 | 0.48 |

## 2. Questions asked and accuracy

| Method | Average questions | Top-1 correct |
|---|---|---|
| Backward chaining, every fault | 39.7 | 30/30 |
| Backward chaining, right subsystem chosen by the rider | 9.0 | – |
| Assistant, no description (information gain only) | 10.9 | 20/30 |
| Assistant, Vietnamese description + information gain | 5.5 | 30/30 |
| Assistant, English description + information gain | 5.5 | 30/30 |

Questions asked by the assistant do not count what was read from the description. All 30 scenario descriptions have now been used while writing nlu.py, so the held-out set below is the fair estimate.

## 3. Per scenario

| Id | Expected fault | Backward (all / right part) | No text | VI text | EN text |
|---|---|---|---|---|---|
| BT01 | worn_brake_pads | 38 / 8 | 15 ✕ | 4 ✓ | 4 ✓ |
| BT02 | worn_brake_pads | 40 / 6 | 15 ✕ | 15 ✓ | 15 ✓ |
| BT03 | brake_fluid_leak | 43 / 9 | 6 ✓ | 0 ✓ | 0 ✓ |
| BT04 | old_brake_fluid | 39 / 9 | 13 ✓ | 9 ✓ | 9 ✓ |
| BT05 | warped_brake_disc | 36 / 6 | 15 ✓ | 15 ✓ | 15 ✓ |
| BT06 | sticking_brake_caliper | 38 / 6 | 15 ✕ | 15 ✓ | 15 ✓ |
| BT07 | underinflated_tyre | 38 / 10 | 7 ✓ | 4 ✓ | 4 ✓ |
| BT08 | tyre_puncture | 38 / 10 | 15 ✓ | 5 ✓ | 7 ✓ |
| BT09 | fork_seal_leak | 40 / 8 | 15 ✕ | 15 ✓ | 15 ✓ |
| BT10 | worn_rear_shock | 41 / 11 | 5 ✓ | 0 ✓ | 0 ✓ |
| ET01 | clogged_air_filter | 42 / 13 | 9 ✓ | 0 ✓ | 0 ✓ |
| ET02 | engine_burning_oil | 37 / 10 | 10 ✓ | 5 ✓ | 5 ✓ |
| ET03 | low_engine_oil | 39 / 10 | 15 ✕ | 0 ✓ | 0 ✓ |
| ET04 | low_coolant | 37 / 10 | 15 ✓ | 7 ✓ | 7 ✓ |
| ET05 | cooling_fan_problem | 37 / 10 | 15 ✓ | 13 ✓ | 13 ✓ |
| ET06 | dirty_throttle_body | 38 / 11 | 15 ✕ | 15 ✓ | 15 ✓ |
| ET07 | worn_cvt_belt | 38 / 7 | 8 ✓ | 1 ✓ | 1 ✓ |
| ET08 | clutch_cable_needs_adjustment | 40 / 9 | 15 ✕ | 15 ✓ | 15 ✓ |
| ET09 | clutch_slipping | 40 / 9 | 15 ✓ | 15 ✓ | 15 ✓ |
| ET10 | chain_needs_lubrication | 38 / 7 | 12 ✓ | 1 ✓ | 1 ✓ |
| SE01 | weak_battery | 41 / 10 | 4 ✓ | 0 ✓ | 0 ✓ |
| SE02 | start_procedure_error | 40 / 9 | 5 ✓ | 0 ✓ | 0 ✓ |
| SE03 | out_of_fuel | 41 / 8 | 4 ✓ | 0 ✓ | 0 ✓ |
| SE04 | flooded_engine | 45 / 11 | 6 ✓ | 1 ✓ | 1 ✓ |
| SE05 | fuel_pump_problem | 43 / 11 | 6 ✓ | 0 ✓ | 0 ✓ |
| SE06 | blown_main_fuse | 41 / 8 | 15 ✕ | 0 ✓ | 0 ✓ |
| SE07 | blown_headlight_bulb | 41 / 7 | 15 ✕ | 8 ✓ | 8 ✓ |
| SE08 | charging_system_problem | 42 / 8 | 4 ✓ | 1 ✓ | 0 ✓ |
| SE09 | spark_plug_problem | 40 / 8 | 15 ✕ | 1 ✓ | 0 ✓ |
| SE10 | weak_battery | 41 / 10 | 4 ✓ | 1 ✓ | 1 ✓ |

## 4. Held-out descriptions (HO)

| Language | Average questions | Top-1 correct |
|---|---|---|
| Vietnamese | 10.8 | 8/10 |
| English | 11.5 | 7/10 |

## 5. Bike-model scenarios (MS, tests/data/model_scenarios.json)

One scenario per model rule MD01-MD09, written by the author of the rules.

| Method | Top-1 correct | Average questions |
|---|---|---|
| Forward chaining, bike model given | 9/9 | – |
| Forward chaining, bike model left out | 4/9 | – |
| Backward chaining | 9/9 | – |
| Wang's algorithm proves the expected fault | 9/9 | – |
| Assistant, Vietnamese description | 9/9 | 13.3 |
| Assistant, English description | 9/9 | 13.3 |
