---
about: Fans and mounts for the UNICOLY cabinet
readonly: no
---
cabinet-fans  
Short name: cabinet-fans  
Status: concept, nothing built. Updated 2026-09-30.

Scope  
- Fans and their mounts for the UNICOLY cabinet.

Fan  
- be quiet! Pure Wings 3 140mm PWM high-speed, black, part BL109, GTIN 04260052190814.  
- 140 × 140 × 25 mm; 1800 rpm; 72.2 cfm (122.6 m³/h); 2.44 mm H₂O; 30.5 dB(A); 5–13.2 V DC; 0.5 A; 4-pin PWM; rifle bearing; fan screws included. Source: be quiet! datasheet.  
- Mounting holes: 124.5 mm square (standard 140 mm pattern; assumption, not measured on this fan).  
- Runs at full speed with the PWM wire unconnected (inference: standard PWM fan behavior; confirm on the fan).

Requirements (from me)  
- Full speed, 24/7.  
- Compact: no large plenum or expansion diffuser.  
- More than one fan; how many is open.  
- No changes to the cabinet itself.

Temperatures (measured by me, 2026-09-28)  
- Room about 77 °F; cabinet 82–85 °F. Goal: 70–80 °F.

Estimates (inference)  
- Each fan adds at most about 6 W (12 V × 0.5 A): about 0.2–0.3 °C average rise per fan in the closed cabinet, assuming the cabinet sheds about 20–25 W per °C.  
- Circulation fans can't cool; they even out top-to-bottom differences. Exhaust fans pull the cabinet toward room temperature: about 20 W per °C per fan through real openings.  
- With the room at 77 °F: 1 exhaust fan → about 79.5–81 °F; 2 → about 79–80 °F; 3 → about 78–79 °F. The low 70s need a cooler room.  
- Exhaust brings cabinet humidity toward room humidity.  
- Raw fan outlet speed about 2.5–3 m/s.

Decisions  
1. Circulation fans get no diffuser: each fan blows into a cabinet surface at a set, adjustable gap (about 35–70 mm, a quarter to half the fan's width; inference), with a guard over the intake. Chosen over a perforated face plate, a deflector cap and a short expansion; a full expansion slot was rejected as too big.

Open questions (in order)  
1. Design direction: exhaust plus circulation (recommended: two exhaust fans in the cabinet's existing top holes, an inlet down low, circulation fans inside), exhaust only, or circulation only.  
2. Number of fans.  
3. Which surface circulation fans blow into: cabinet top (recommended), side glass or back wall.  
4. How the mount attaches to the cabinet, without altering it.  
5. How the fan attaches to the mount.  
6. The gap to the surface, and how it adjusts.  
7. Intake guard design.  
8. Exhaust: size and position of the cabinet's pre-existing fan holes (mentioned by reviewers, not measured), and where the inlet goes.  
9. Whether to move power supplies and drivers outside the cabinet.

Agreed changes not yet built: none.  
Build script: none yet.  
