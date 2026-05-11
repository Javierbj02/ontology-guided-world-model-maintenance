# Candidate-generation qualitative summary (run_1)

## Top-1 hypothesis frequencies by condition

### PC1
- Accidental Displacement During Transport: 6

### PC2
- Accidental Displacement During Transport: 5
- Accidental Displacement: 1

### PC3
- Accidental Displacement During Transport: 5
- Accidental Displacement: 1

## Top-1 hypothesis frequencies by family and condition

### co-located
- PC1:
  - Accidental Displacement During Transport: 3
- PC2:
  - Accidental Displacement During Transport: 2
  - Accidental Displacement: 1
- PC3:
  - Accidental Displacement During Transport: 2
  - Accidental Displacement: 1

### nurse-separated
- PC1:
  - Accidental Displacement During Transport: 3
- PC2:
  - Accidental Displacement During Transport: 3
- PC3:
  - Accidental Displacement During Transport: 3

## Per-case summaries

### CG1_base_loss_clean — PC1 (co-located)
Source: `outputs\generation_suite\CG1_base_loss_clean\PC1\run_1\CG1_base_loss_clean__PC1__run1__raw_output.txt`

- Rank 1: Accidental Displacement During Transport
  - event_type: `EventType_AccidentalDisplacement`
  - participants: Agent_Shadow
  - location: `None`
  - rationale: Medicine may have been dislodged due to sudden movement or vibration during transport.
  - flags: shadow=True, medicine=False, tray=False, explicit_location=False
- Rank 2: Tray Malfunction
  - event_type: `EventType_TrayMalfunction`
  - participants: Agent_Shadow, PhysicalObject_ShadowTray
  - location: `None`
  - rationale: A malfunction in the tray mechanism could have caused the medicine to fall off unnoticed.
  - flags: shadow=True, medicine=False, tray=True, explicit_location=False
- Rank 3: Unobserved Third-Party Interference
  - event_type: `EventType_ThirdPartyInterference`
  - participants: UnknownAgent
  - location: `None`
  - rationale: An unidentified individual or object may have interfered with the medicine while the robot was in transit.
  - flags: shadow=False, medicine=False, tray=False, explicit_location=False
  - novel_symbols: UnknownAgent

### CG1_base_loss_clean — PC2 (co-located)
Source: `outputs\generation_suite\CG1_base_loss_clean\PC2\run_1\CG1_base_loss_clean__PC2__run1__raw_output.txt`

- Rank 1: Accidental Displacement
  - event_type: `EventType_AccidentalDisplacement`
  - participants: Agent_Shadow
  - location: `None`
  - rationale: Medicine may have been accidentally displaced during transport due to robot movement or environmental factors.
  - flags: shadow=True, medicine=False, tray=False, explicit_location=False
- Rank 2: Tray Malfunction
  - event_type: `EventType_TrayMalfunction`
  - participants: Agent_Shadow, PhysicalObject_ShadowTray
  - location: `None`
  - rationale: A malfunction in the tray mechanism could have caused the medicine to fall off during transport.
  - flags: shadow=True, medicine=False, tray=True, explicit_location=False
- Rank 3: Unobserved Third-Party Interaction
  - event_type: `EventType_ThirdPartyInteraction`
  - participants: Unknown_Agent
  - location: `None`
  - rationale: An unobserved third party may have interacted with the robot or tray, causing the medicine to be removed or displaced.
  - flags: shadow=False, medicine=False, tray=False, explicit_location=False
  - novel_symbols: Unknown_Agent

### CG1_base_loss_clean — PC3 (co-located)
Source: `outputs\generation_suite\CG1_base_loss_clean\PC3\run_1\CG1_base_loss_clean__PC3__run1__raw_output.txt`

- Rank 1: Accidental Displacement
  - event_type: `EventType_AccidentalDisplacement`
  - participants: Agent_Shadow, PhysicalObject_Medicine1
  - location: `PhysicalPlace_Corridor1`
  - rationale: Medicine could have been accidentally displaced from the tray due to robot movement or environmental factors.
  - flags: shadow=True, medicine=True, tray=False, explicit_location=True
- Rank 2: Tray Malfunction
  - event_type: `EventType_TrayMalfunction`
  - participants: Agent_Shadow, PhysicalObject_ShadowTray
  - location: `PhysicalPlace_Corridor1`
  - rationale: A malfunction in the tray mechanism could have caused the medicine to fall off without detection.
  - flags: shadow=True, medicine=False, tray=True, explicit_location=True
- Rank 3: Unobserved Third-Party Interaction
  - event_type: `EventType_ThirdPartyInteraction`
  - participants: Agent_Unknown, PhysicalObject_Medicine1, Agent_Shadow
  - location: `PhysicalPlace_Corridor1`
  - rationale: An unobserved third party might have interacted with the robot or tray, causing the medicine to be removed.
  - flags: shadow=True, medicine=True, tray=False, explicit_location=True
  - novel_symbols: Agent_Unknown

### CG2_wrong_location_decoy — PC1 (co-located)
Source: `outputs\generation_suite\CG2_wrong_location_decoy\PC1\run_1\CG2_wrong_location_decoy__PC1__run1__raw_output.txt`

- Rank 1: Accidental Displacement During Transport
  - event_type: `EventType_AccidentalDisplacement`
  - participants: Agent_Shadow
  - location: `None`
  - rationale: Medicine may have been dislodged from the tray due to sudden movement or vibration during transport.
  - flags: shadow=True, medicine=False, tray=False, explicit_location=False
- Rank 2: Tray Malfunction or Instability
  - event_type: `EventType_TrayMalfunction`
  - participants: Agent_Shadow
  - location: `None`
  - rationale: A malfunction or instability in the tray mechanism could have caused the medicine to fall off unnoticed.
  - flags: shadow=True, medicine=False, tray=False, explicit_location=False
- Rank 3: Unintended Interaction with Environmental Obstacle
  - event_type: `EventType_EnvironmentalInteraction`
  - participants: Agent_Shadow
  - location: `None`
  - rationale: The robot may have brushed against an obstacle, causing the medicine to be knocked off the tray.
  - flags: shadow=True, medicine=False, tray=False, explicit_location=False

### CG2_wrong_location_decoy — PC2 (co-located)
Source: `outputs\generation_suite\CG2_wrong_location_decoy\PC2\run_1\CG2_wrong_location_decoy__PC2__run1__raw_output.txt`

- Rank 1: Accidental Displacement During Transport
  - event_type: `EventType_AccidentalDisplacement`
  - participants: Agent_Shadow
  - location: `None`
  - rationale: Medicine may have been accidentally displaced from the tray during robot movement due to vibrations, bumps, or uneven surfaces.
  - flags: shadow=True, medicine=False, tray=False, explicit_location=False
- Rank 2: Interference by Another Object
  - event_type: `EventType_ObjectInterference`
  - participants: Agent_Shadow, PhysicalObject_Decoy
  - location: `None`
  - rationale: The decoy object may have interfered with the medicine, causing it to fall or shift off the tray during transport.
  - flags: shadow=True, medicine=False, tray=False, explicit_location=False
  - novel_symbols: PhysicalObject_Decoy
- Rank 3: Tray Malfunction
  - event_type: `EventType_TrayMalfunction`
  - participants: Agent_Shadow, PhysicalObject_ShadowTray
  - location: `None`
  - rationale: A malfunction in the tray, such as a loose surface or faulty securing mechanism, could have caused the medicine to fall off during transport.
  - flags: shadow=True, medicine=False, tray=True, explicit_location=False

### CG2_wrong_location_decoy — PC3 (co-located)
Source: `outputs\generation_suite\CG2_wrong_location_decoy\PC3\run_1\CG2_wrong_location_decoy__PC3__run1__raw_output.txt`

- Rank 1: Accidental Displacement During Transport
  - event_type: `EventType_AccidentalDisplacement`
  - participants: Agent_Shadow
  - location: `PhysicalPlace_Corridor1`
  - rationale: Medicine may have been accidentally displaced from the tray due to movement or vibration during transport.
  - flags: shadow=True, medicine=False, tray=False, explicit_location=True
- Rank 2: Interference by Another Object
  - event_type: `EventType_ObjectInterference`
  - participants: Agent_Shadow, PhysicalObject_Decoy
  - location: `PhysicalPlace_Corridor1`
  - rationale: A decoy object or another item on the tray may have shifted, causing the medicine to fall off.
  - flags: shadow=True, medicine=False, tray=False, explicit_location=True
  - novel_symbols: PhysicalObject_Decoy
- Rank 3: Unobserved Third-Party Interaction
  - event_type: `EventType_ThirdPartyInteraction`
  - participants: Agent_Shadow, Agent_Unknown
  - location: `PhysicalPlace_Corridor1`
  - rationale: An unobserved third party may have interacted with the tray, causing the medicine to be displaced or removed.
  - flags: shadow=True, medicine=False, tray=False, explicit_location=True
  - novel_symbols: Agent_Unknown

### CG3_old_decoy — PC1 (co-located)
Source: `outputs\generation_suite\CG3_old_decoy\PC1\run_1\CG3_old_decoy__PC1__run1__raw_output.txt`

- Rank 1: Accidental Displacement During Transport
  - event_type: `EventType_AccidentalDisplacement`
  - participants: Agent_Shadow
  - location: `None`
  - rationale: Medicine may have been dislodged from the tray due to sudden movement or vibration during transport.
  - flags: shadow=True, medicine=False, tray=False, explicit_location=False
- Rank 2: Tray Malfunction
  - event_type: `EventType_TrayMalfunction`
  - participants: Agent_Shadow
  - location: `None`
  - rationale: A malfunction in the tray mechanism could have caused the medicine to fall off without detection.
  - flags: shadow=True, medicine=False, tray=False, explicit_location=False
- Rank 3: Unobserved Third-Party Interference
  - event_type: `EventType_ThirdPartyInterference`
  - participants: Unknown_Agent
  - location: `None`
  - rationale: An unobserved individual may have interfered with the tray, removing the medicine without triggering standard detection mechanisms.
  - flags: shadow=False, medicine=False, tray=False, explicit_location=False
  - novel_symbols: Unknown_Agent

### CG3_old_decoy — PC2 (co-located)
Source: `outputs\generation_suite\CG3_old_decoy\PC2\run_1\CG3_old_decoy__PC2__run1__raw_output.txt`

- Rank 1: Accidental Displacement During Transport
  - event_type: `EventType_AccidentalDisplacement`
  - participants: Agent_Shadow
  - location: `None`
  - rationale: The medicine may have been accidentally displaced during transport due to movement or vibration, especially if the tray was not secured properly.
  - flags: shadow=True, medicine=False, tray=False, explicit_location=False
- Rank 2: Unintended Decoy Interaction
  - event_type: `EventType_UnintendedInteraction`
  - participants: Agent_Shadow, PhysicalObject_Medicine1
  - location: `None`
  - rationale: The old decoy event in the history might have caused confusion, leading to the medicine being placed incorrectly or removed unintentionally during a routine check.
  - flags: shadow=True, medicine=True, tray=False, explicit_location=False
- Rank 3: Tray Malfunction
  - event_type: `EventType_TrayMalfunction`
  - participants: Agent_Shadow, PhysicalObject_ShadowTray
  - location: `None`
  - rationale: A malfunction in the tray mechanism could have caused the medicine to fall off without detection, especially if the tray has a history of issues.
  - flags: shadow=True, medicine=False, tray=True, explicit_location=False

### CG3_old_decoy — PC3 (co-located)
Source: `outputs\generation_suite\CG3_old_decoy\PC3\run_1\CG3_old_decoy__PC3__run1__raw_output.txt`

- Rank 1: Accidental Displacement During Transport
  - event_type: `EventType_AccidentalDisplacement`
  - participants: Agent_Shadow
  - location: `PhysicalPlace_Corridor1`
  - rationale: Medicine could have been accidentally displaced from the tray due to movement or vibration during transport.
  - flags: shadow=True, medicine=False, tray=False, explicit_location=True
- Rank 2: Unobserved Third-Party Interference
  - event_type: `EventType_ThirdPartyInterference`
  - participants: Agent_Unknown
  - location: `PhysicalPlace_Corridor1`
  - rationale: An unobserved third party might have interfered with the tray, causing the medicine to be removed or displaced.
  - flags: shadow=False, medicine=False, tray=False, explicit_location=True
  - novel_symbols: Agent_Unknown
- Rank 3: Tray Malfunction or Instability
  - event_type: `EventType_TrayMalfunction`
  - participants: Agent_Shadow
  - location: `PhysicalPlace_Corridor1`
  - rationale: The tray might have malfunctioned or become unstable, leading to the medicine falling off during transport.
  - flags: shadow=True, medicine=False, tray=False, explicit_location=True

### CG4_nurse_separated_clean — PC1 (nurse-separated)
Source: `outputs\generation_suite\CG4_nurse_separated_clean\PC1\run_1\CG4_nurse_separated_clean__PC1__run1__raw_output.txt`

- Rank 1: Accidental Displacement During Transport
  - event_type: `EventType_AccidentalDisplacement`
  - participants: Agent_Shadow
  - location: `None`
  - rationale: Medicine may have fallen off the tray due to movement or vibration during transport.
  - flags: shadow=True, medicine=False, tray=False, explicit_location=False
- Rank 2: Tray Malfunction
  - event_type: `EventType_TrayMalfunction`
  - participants: Agent_Shadow
  - location: `None`
  - rationale: A malfunction in the tray mechanism could have caused the medicine to slip or fall.
  - flags: shadow=True, medicine=False, tray=False, explicit_location=False
- Rank 3: Unobserved Third-Party Interference
  - event_type: `EventType_ThirdPartyInterference`
  - participants: Unknown_Agent
  - location: `None`
  - rationale: An unobserved individual or object may have inadvertently knocked the medicine off the tray.
  - flags: shadow=False, medicine=False, tray=False, explicit_location=False
  - novel_symbols: Unknown_Agent

### CG4_nurse_separated_clean — PC2 (nurse-separated)
Source: `outputs\generation_suite\CG4_nurse_separated_clean\PC2\run_1\CG4_nurse_separated_clean__PC2__run1__raw_output.txt`

- Rank 1: Accidental Displacement During Transport
  - event_type: `EventType_AccidentalDisplacement`
  - participants: Agent_Shadow
  - location: `None`
  - rationale: Medicine may have slipped off the tray due to movement or vibration during transport.
  - flags: shadow=True, medicine=False, tray=False, explicit_location=False
- Rank 2: Unintended Removal by Another Agent
  - event_type: `EventType_UnintendedRemoval`
  - participants: Agent_Unknown
  - location: `None`
  - rationale: Another person or agent may have unintentionally removed the medicine while the nurse was away.
  - flags: shadow=False, medicine=False, tray=False, explicit_location=False
  - novel_symbols: Agent_Unknown
- Rank 3: Tray Malfunction or Defect
  - event_type: `EventType_TrayMalfunction`
  - participants: Agent_Shadow
  - location: `None`
  - rationale: A defect in the tray mechanism could have caused the medicine to fall off without external intervention.
  - flags: shadow=True, medicine=False, tray=False, explicit_location=False

### CG4_nurse_separated_clean — PC3 (nurse-separated)
Source: `outputs\generation_suite\CG4_nurse_separated_clean\PC3\run_1\CG4_nurse_separated_clean__PC3__run1__raw_output.txt`

- Rank 1: Accidental Displacement During Transport
  - event_type: `EventType_AccidentalDisplacement`
  - participants: Agent_Shadow
  - location: `PhysicalPlace_Corridor1`
  - rationale: Medicine may have fallen off the tray due to movement or vibration while the robot was in motion.
  - flags: shadow=True, medicine=False, tray=False, explicit_location=True
- Rank 2: Unintended Interaction with Environment
  - event_type: `EventType_EnvironmentalInteraction`
  - participants: Agent_Shadow
  - location: `PhysicalPlace_Corridor1`
  - rationale: The medicine could have been dislodged by contact with a fixed object or obstacle in the corridor.
  - flags: shadow=True, medicine=False, tray=False, explicit_location=True
- Rank 3: Tray Malfunction
  - event_type: `EventType_EquipmentMalfunction`
  - participants: Agent_Shadow
  - location: `PhysicalPlace_Corridor1`
  - rationale: A mechanical failure or defect in the tray could have caused the medicine to fall off.
  - flags: shadow=True, medicine=False, tray=False, explicit_location=True

### CG5_nurse_separated_wrong_location_decoy — PC1 (nurse-separated)
Source: `outputs\generation_suite\CG5_nurse_separated_wrong_location_decoy\PC1\run_1\CG5_nurse_separated_wrong_location_decoy__PC1__run1__raw_output.txt`

- Rank 1: Accidental Displacement During Transport
  - event_type: `EventType_AccidentalDisplacement`
  - participants: Agent_Shadow
  - location: `None`
  - rationale: Medicine may have fallen off the tray during movement due to uneven surfaces or sudden stops.
  - flags: shadow=True, medicine=False, tray=False, explicit_location=False
- Rank 2: Decoy Confusion Leading to Misplacement
  - event_type: `EventType_MisplacementDueToDecoy`
  - participants: Agent_Shadow, Agent_Nurse
  - location: `None`
  - rationale: The wrong-location decoy may have caused confusion, leading to the medicine being placed incorrectly.
  - flags: shadow=True, medicine=False, tray=False, explicit_location=False
- Rank 3: Interference by Unobserved Third Party
  - event_type: `EventType_ThirdPartyInterference`
  - participants: Agent_Unknown
  - location: `None`
  - rationale: An unobserved third party may have interfered with the tray, removing the medicine without detection.
  - flags: shadow=False, medicine=False, tray=False, explicit_location=False
  - novel_symbols: Agent_Unknown

### CG5_nurse_separated_wrong_location_decoy — PC2 (nurse-separated)
Source: `outputs\generation_suite\CG5_nurse_separated_wrong_location_decoy\PC2\run_1\CG5_nurse_separated_wrong_location_decoy__PC2__run1__raw_output.txt`

- Rank 1: Accidental Displacement During Transport
  - event_type: `EventType_AccidentalDisplacement`
  - participants: Agent_Shadow
  - location: `None`
  - rationale: Medicine may have been dislodged from the tray due to movement or vibration during transport.
  - flags: shadow=True, medicine=False, tray=False, explicit_location=False
- Rank 2: Interference by Another Object
  - event_type: `EventType_ObjectInterference`
  - participants: Agent_Shadow, PhysicalObject_Decoy
  - location: `None`
  - rationale: The decoy object may have interfered with the medicine, causing it to fall off the tray.
  - flags: shadow=True, medicine=False, tray=False, explicit_location=False
  - novel_symbols: PhysicalObject_Decoy
- Rank 3: Unintended Removal by a Third Party
  - event_type: `EventType_UnintendedRemoval`
  - participants: Agent_Unknown
  - location: `None`
  - rationale: An unidentified individual may have unintentionally removed the medicine, mistaking it for the decoy.
  - flags: shadow=False, medicine=False, tray=False, explicit_location=False
  - novel_symbols: Agent_Unknown

### CG5_nurse_separated_wrong_location_decoy — PC3 (nurse-separated)
Source: `outputs\generation_suite\CG5_nurse_separated_wrong_location_decoy\PC3\run_1\CG5_nurse_separated_wrong_location_decoy__PC3__run1__raw_output.txt`

- Rank 1: Accidental Displacement During Transport
  - event_type: `EventType_AccidentalDisplacement`
  - participants: Agent_Shadow
  - location: `PhysicalPlace_Corridor1`
  - rationale: Medicine could have fallen off the tray due to movement or vibration while the robot was in motion.
  - flags: shadow=True, medicine=False, tray=False, explicit_location=True
- Rank 2: Interference by Another Agent
  - event_type: `EventType_Interference`
  - participants: Agent_Unknown
  - location: `PhysicalPlace_Corridor1`
  - rationale: An unknown agent might have interfered with the robot or tray, causing the medicine to be displaced.
  - flags: shadow=False, medicine=False, tray=False, explicit_location=True
  - novel_symbols: Agent_Unknown
- Rank 3: Tray Malfunction
  - event_type: `EventType_TrayMalfunction`
  - participants: Agent_Shadow
  - location: `PhysicalPlace_Corridor1`
  - rationale: A malfunction in the tray mechanism could have caused the medicine to fall or be ejected.
  - flags: shadow=True, medicine=False, tray=False, explicit_location=True

### CG6_nurse_separated_old_decoy — PC1 (nurse-separated)
Source: `outputs\generation_suite\CG6_nurse_separated_old_decoy\PC1\run_1\CG6_nurse_separated_old_decoy__PC1__run1__raw_output.txt`

- Rank 1: Accidental Displacement During Transport
  - event_type: `EventType_AccidentalDisplacement`
  - participants: Agent_Shadow
  - location: `None`
  - rationale: Medicine may have been dislodged from the tray due to movement or vibration during transport.
  - flags: shadow=True, medicine=False, tray=False, explicit_location=False
- Rank 2: Interference by Unobserved Third Party
  - event_type: `EventType_ThirdPartyInterference`
  - participants: UnknownAgent
  - location: `None`
  - rationale: An unobserved individual may have interacted with the robot or tray, causing the medicine to be removed or displaced.
  - flags: shadow=False, medicine=False, tray=False, explicit_location=False
  - novel_symbols: UnknownAgent
- Rank 3: Tray Malfunction or Defect
  - event_type: `EventType_EquipmentMalfunction`
  - participants: Agent_Shadow
  - location: `None`
  - rationale: A defect in the tray mechanism could have caused the medicine to fall or become dislodged without external intervention.
  - flags: shadow=True, medicine=False, tray=False, explicit_location=False

### CG6_nurse_separated_old_decoy — PC2 (nurse-separated)
Source: `outputs\generation_suite\CG6_nurse_separated_old_decoy\PC2\run_1\CG6_nurse_separated_old_decoy__PC2__run1__raw_output.txt`

- Rank 1: Accidental Displacement During Transport
  - event_type: `EventType_AccidentalDisplacement`
  - participants: Agent_Shadow
  - location: `None`
  - rationale: Medicine may have been accidentally displaced from the tray during robot movement due to vibrations or uneven surfaces.
  - flags: shadow=True, medicine=False, tray=False, explicit_location=False
- Rank 2: Interference by Unobserved Third Party
  - event_type: `EventType_ThirdPartyInterference`
  - participants: Agent_Unknown
  - location: `None`
  - rationale: An unobserved third party may have interfered with the robot or tray, causing the medicine to be removed or displaced.
  - flags: shadow=False, medicine=False, tray=False, explicit_location=False
  - novel_symbols: Agent_Unknown
- Rank 3: Tray Malfunction or Defect
  - event_type: `EventType_TrayMalfunction`
  - participants: Agent_Shadow
  - location: `None`
  - rationale: A malfunction or defect in the tray mechanism could have caused the medicine to fall off during transport.
  - flags: shadow=True, medicine=False, tray=False, explicit_location=False

### CG6_nurse_separated_old_decoy — PC3 (nurse-separated)
Source: `outputs\generation_suite\CG6_nurse_separated_old_decoy\PC3\run_1\CG6_nurse_separated_old_decoy__PC3__run1__raw_output.txt`

- Rank 1: Accidental Displacement During Transport
  - event_type: `EventType_AccidentalDisplacement`
  - participants: Agent_Shadow
  - location: `PhysicalPlace_Corridor1`
  - rationale: Medicine could have fallen off the tray due to robot movement or environmental factors like bumps or vibrations.
  - flags: shadow=True, medicine=False, tray=False, explicit_location=True
- Rank 2: Interference by Unobserved Third Party
  - event_type: `EventType_ThirdPartyInterference`
  - participants: Agent_Unknown
  - location: `PhysicalPlace_Corridor1`
  - rationale: An unobserved person or object might have interfered with the tray, causing the medicine to be displaced.
  - flags: shadow=False, medicine=False, tray=False, explicit_location=True
  - novel_symbols: Agent_Unknown
- Rank 3: Decoy Confusion Leading to Misplacement
  - event_type: `EventType_DecoyConfusion`
  - participants: Agent_Shadow
  - location: `None`
  - rationale: The presence of an old decoy might have caused confusion, leading to the medicine being misplaced during transport.
  - flags: shadow=True, medicine=False, tray=False, explicit_location=False


