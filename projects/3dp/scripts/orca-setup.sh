#!/bin/bash
# Installs OrcaSlicer's command-line slicer at /opt/orca (run: /opt/orca/slice FILE.3mf OUTDIR).
set -e
V=2.4.2; D=/opt/orca
[ -x $D/slice ] && exit 0
mkdir -p $D && cd $D
curl -sSL -o orca.AppImage "https://github.com/SoftFever/OrcaSlicer/releases/download/v$V/OrcaSlicer_Linux_AppImage_Ubuntu2404_V$V.AppImage"
chmod +x orca.AppImage && ./orca.AppImage --appimage-extract >/dev/null && rm orca.AppImage
B=squashfs-root/bin/orca-slicer; mkdir -p stubs
# empty stand-ins for display libraries the container lacks; slicing never calls them
nm -D --undefined-only $B | awk '{print $2}' | sed 's/@.*//' | sort -u > und.txt
ldd $B | awk '/=> \//{print $3}' | xargs -I{} nm -D --defined-only {} 2>/dev/null | awk '{print $3}' | sed 's/@.*//' | sort -u > def.txt
comm -23 und.txt def.txt | grep -v '^_' | awk '{print "void "$1"(void){}"}' > stubs.c
for l in $(ldd $B | awk '/not found/{print $1}'); do gcc -shared -fPIC -w -o stubs/$l stubs.c; done
cat > slice <<'SH'
#!/bin/bash
# slice FILE.3mf [OUTDIR]: slices every plate with the 3mf's own settings; prints result.json's status and warnings
D=/opt/orca; O=${2:-out}; mkdir -p "$O" $D/dd
LD_LIBRARY_PATH=$D/stubs:$D/squashfs-root/bin $D/squashfs-root/bin/orca-slicer --datadir $D/dd --slice 0 --outputdir "$O" "$1" >"$O/orca.log" 2>&1
grep -E '"(error_string|return_code|warning_message)"' "$O/result.json" | grep -v '"warning_message": ""' || echo "no result.json; see $O/orca.log"
# each plate's time, layers, height and filament, from its G-code header
for g in "$O"/plate_*.gcode; do [ -f "$g" ] && echo "$(basename "$g"): $(grep -m6 -E '^; (model printing time|total layer number|max_z_height|filament used \[g\])' "$g" | sed 's/^; //' | paste -sd';' -)"; done
SH
chmod +x slice; rm -f und.txt def.txt
