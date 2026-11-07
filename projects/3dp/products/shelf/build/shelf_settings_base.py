# Makes shelf_settings_base.json: barrinaClip's base (my printer and process settings, PLA Matte in slot 1)
# with slot 1 replaced by Orca 2.4.2's resolved "Bambu PETG-CF @BBL X1C" profile (the shelf preset, user 2026-10-08).
# Run: python3 shelf_settings_base.py ../../barrina-clips/build/barrinaClip_settings_base.json shelf_settings_base.json [profile]
# (profile defaults to the PETG-CF one; petgBasic_settings_base.json uses "Bambu PETG Basic @BBL X1C 0.8 nozzle").
import json, os, sys
PROF="/opt/orca/squashfs-root/resources/profiles/BBL/filament"
def resolve(name):
    d=json.load(open(os.path.join(PROF,name+".json")))
    if d.get("inherits"):
        b=resolve(d["inherits"]); b.update(d); d=b
    return d
NAME=sys.argv[3] if len(sys.argv)>3 else "Bambu PETG-CF @BBL X1C"
p=resolve(NAME)
s=json.load(open(sys.argv[1]))
n=len(s["filament_settings_id"]); changed=[]
for k,v in p.items():
    if k in s and isinstance(s[k],list) and isinstance(v,list):
        if len(s[k])==2*n and len(v)==2:      # per filament x extruder variant
            if s[k][0:2]!=v: changed.append((k,s[k][0:2],v))
            s[k][0:2]=v
        elif len(s[k])==n:
            if s[k][0]!=v[0]: changed.append((k,s[k][0],v[0]))
            s[k][0]=v[0]
if "filament_id" in p and "filament_ids" in s: s["filament_ids"][0]=p["filament_id"]
s["filament_settings_id"][0]=NAME
json.dump(s,open(sys.argv[2],"w"),indent=1)
print(len(changed),"slot-1 values changed; e.g.")
for c in changed:
    if c[0] in ("filament_type","nozzle_temperature","hot_plate_temp","filament_max_volumetric_speed","filament_ids","filament_flow_ratio","nozzle_temperature","filament_max_volumetric_speed","compatible_printers","filament_vendor","textured_plate_temp","fan_max_speed"): print(" ",c)
print("nozzle temps now", s["nozzle_temperature"], "hot plate", s["hot_plate_temp"])
