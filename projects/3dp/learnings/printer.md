---
about: Printer and AMS hardware learnings: faults, fixes, maintenance
read-when: before troubleshooting the printer or the AMS
readonly: no
---
# **learnings/printer**

Slicing learnings are in learnings/walls, seams, speed-and-cooling and slicing-checks.

## **AMS slot not detecting filament, or reading empty after loading (researched 2026-10-03, original AMS)**

> * Each slot has two filament sensors, one in its feeder and one in the hub. The feeder pulls filament in only after its own sensor sees it; with both sensors off, the AMS treats the slot as empty.  
> * Feeder lights: all four flashing white in turn = every slot empty; solid white = filament in, idle; pulsing white = busy (feeding, reading the tag); off = empty while other slots hold filament (normal). Faults: solid white with the slot empty = sensor fault or a broken piece inside; one light staying off with all four slots empty = that feeder has no power; slow red pulse = a print called for the slot and the AMS read it as empty; red single flash = the feeder sees filament but the hub doesn't (a feed failed); solid red = the hub sees filament but the feeder doesn't; red double flash = both see it (a load or unload failed); all four flashing red = the printer can't reach the AMS.  
> * A slot that reads empty right after a pre-load (the AMS pulling in newly inserted filament) has lost both sensors. Check whether the filament still runs down into the feeder. If it does, wiggle it at the inlet: the light coming back means the feeder's sensor is losing it. If it's been pulled back out, the load itself is failing (inference).  
> * Bambu's fix order for the feeder's sensor: blow compressed air at it, then push a short piece of filament in and out several times and watch the light. Next, take the feeder out (steps 1–3 of Bambu's feeder replacement guide), check that its cable is firmly plugged in, and brush away debris near the sensor, which mostly comes from filaments that grind easily. A sensor that never recovers means replacing the feeding funnel unit. If the light responds but the gears don't turn, reseat the feeder's motor cable, then replace the whole feeder.  
> * Filament not coming out of the tube at the AMS's back when loading: Bambu's test for the hub's sensor is to remove that tube, unscrew the AMS main frame's two fixing screws, turn the frame over without pulling its cable, and push filament into the hub; that slot's light turning red means the sensor works.  
> * From forum users, not Bambu: a slot 1 feeder missed loaded filament until the filament was wiggled; swap the suspect feeder with a neighbor to see whether the fault follows it; check the tube under the feeder for a broken piece of filament; check that the spool turns freely and its rollers sit straight (a roller knocked about 1 mm out of place stalled one load); fluff in the hub was blamed (unconfirmed) for a slot going dark mid-print; a spool that runs out mid-print (reported with Bambu Matte) can leave the feeder latched as if loaded until it's taken out and refitted; Bambu support has sent users replacement feeders, though in one case the cause turned out to be the hub motor.  
> * No material or color shown after loading points to the RFID tag, not the sensor: only Bambu spools come with tags, so third-party filament is set by hand.  
> * Find Bambu wiki pages by search: the original AMS's troubleshooting pages sit under wiki.bambulab.com/en/x1/troubleshooting/ and /en/ams/troubleshooting/, and a guessed /en/ams/manual/ address failed.  
> * Mine (2026-10-03): slot 1 takes inserted filament in, blinks red once mid-load, then its light goes out and Orca shows it empty. Nothing tried yet (open item in the 3dp todo).

Sources: Bambu wiki: AMS first stage feeder fault ([https://wiki.bambulab.com/en/x1/troubleshooting/AMS-first-stage-feeder-fault](https://wiki.bambulab.com/en/x1/troubleshooting/AMS-first-stage-feeder-fault)); AMS LED status ([https://wiki.bambulab.com/en/x1/troubleshooting/ams-led-status](https://wiki.bambulab.com/en/x1/troubleshooting/ams-led-status)); AMS slot 1 is empty, HMS 0700-2000-0002-0002 ([https://wiki.bambulab.com/en/x1/troubleshooting/hmscode/0700_2000_0002_0002](https://wiki.bambulab.com/en/x1/troubleshooting/hmscode/0700_2000_0002_0002)); AMS loading and unloading failure ([https://wiki.bambulab.com/en/ams/troubleshooting/ams-loading-unloading-failure](https://wiki.bambulab.com/en/ams/troubleshooting/ams-loading-unloading-failure)). Bambu forum: wiggling and swapping feeders ([https://forum.bambulab.com/t/ams-fails-to-detect-loaded-filament-at-power-on/44301](https://forum.bambulab.com/t/ams-fails-to-detect-loaded-filament-at-power-on/44301)); broken piece under the feeder ([https://forum.bambulab.com/t/ams-unload-failure-slot-1-no-break-or-clog/32667](https://forum.bambulab.com/t/ams-unload-failure-slot-1-no-break-or-clog/32667)); displaced roller ([https://forum.bambulab.com/t/solved-ams-preload-failed-with-noisy-motor/98546/1](https://forum.bambulab.com/t/solved-ams-preload-failed-with-noisy-motor/98546/1)); slot going dark, fluff in the hub ([https://forum.bambulab.com/t/ams-issue-with-one-bay/217756](https://forum.bambulab.com/t/ams-issue-with-one-bay/217756)); feeder latched after a spool ran out ([https://forum.bambulab.com/t/stage-1-feeder-issues/22700](https://forum.bambulab.com/t/stage-1-feeder-issues/22700)); replacement parts from Bambu ([https://forum.bambulab.com/t/1st-stage-feeder-issue/67561](https://forum.bambulab.com/t/1st-stage-feeder-issue/67561), [https://forum.bambulab.com/t/ams-lite-issue-failing-to-feed-into-the-tube/118119](https://forum.bambulab.com/t/ams-lite-issue-failing-to-feed-into-the-tube/118119)). BambuHub: RFID on Bambu spools only, spool tension ([https://bambuhub.net/ams-detection-issues](https://bambuhub.net/ams-detection-issues)).

## P1S vs X1C: similarities, differences and interchangeability (researched 2026-09-26)

**What's the same (what drives print quality)**
- Both have the same CoreXY motion system, a 256 × 256 × 256 mm build volume, a 500 mm/s top speed and 20,000 mm/s² acceleration.
- The hotend reaches 300 °C on both, and both have the same part cooling, including the auxiliary side fan.
- Both are enclosed and have an activated-carbon exhaust filter.
- With the same filament and the same slicer profile, reviewers can't tell prints from the two apart.

**What's different on the X1C**
- A lidar on the toolhead does first-layer inspection, spaghetti-failure detection and automatic lidar flow-rate calibration. The P1S has none of these; it levels the bed with a strain sensor.
- A hardened-steel nozzle is standard. The stock P1S nozzle is stainless steel (mine has been upgraded to hardened steel). Sources disagree on whether the P1S's extruder gears are hardened steel; check them before printing abrasive filaments a lot.
- The X1C has an aluminum-and-glass body and runs a warmer chamber (about 50–55 °C). The P1S body is plastic and glass. This matters for ABS/ASA and barely matters for PETG.
- The X1C has a color touchscreen and a 1080p/30 fps camera. The P1S has a basic screen and a 720p camera at 0.5 fps.
- The X1C costs roughly $500 more.

**Interchangeability in OrcaSlicer**
- **Process profiles** (e.g. "0.30mm Standard @BBL X1C 0.6 nozzle"): interchangeable. Bambu shares them between the X1C and the P1S, so an X1C-named process profile is fine on my P1S.
- **Filament profiles** ("@BBL X1C"): mostly interchangeable, since the values are nearly identical. Use the P1S-specific version when one exists, because it sometimes adjusts fans or temperatures for the P1S's cooler chamber.
- **Printer profiles**: NOT interchangeable. The X1C start G-code calls lidar routines. Always slice with the "Bambu Lab P1S 0.6 nozzle" printer profile.
- **3MF project files** made for an X1C open fine. Set the printer to the P1S and re-slice.
- A filament profile's compatible-printer list matters more than its name. Which Bambu profile Orca 2.4.2 lists for the "Bambu Lab P1S 0.6 nozzle" varies by filament: usually the plain "@BBL X1C" one (37 profiles, e.g. PLA Matte, PLA Basic, PETG-CF); the "@BBL X1C 0.8 nozzle" one, which covers the P1S 0.6 and 0.8 nozzles, for PETG Basic, PETG HF, PETG Translucent, PLA Translucent and PLA-CF ("Bambu PETG HF @BBL X1C 0.8 nozzle" is the only PETG HF profile listed, so it's the right one for my setup); a "0.6 nozzle" one only for ASA-CF, PC and PC FR. Look up a profile's compatible printers in Orca's profile files before naming one or calling it wrong (checked 2026-10-01 and 2026-10-03).

Sources: 3dsearch.app/blog/bambu-x1c-vs-p1s (2026), 3dpros.com P1S vs X1 Carbon comparison, additive-x.com Bambu comparison blog, forum.bambulab.com flow dynamics / lidar thread.
