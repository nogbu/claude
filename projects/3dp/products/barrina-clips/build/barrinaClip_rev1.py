"""barrinaClip rev1: geometry and 3mf writer. Needs barrinaClip_settings_base.json beside it. Run: python3 barrinaClip_rev1.py OUTDIR. Profile in X-Y (X: front(-) to back(+), Y: up), extruded along Z (along the bar = print Z)."""
import numpy as np
from shapely.geometry import Polygon as SP, box, Point
from shapely import affinity
from shapely.ops import unary_union
import trimesh
# ---- values (mm). Z on 0.3 layers, bead thicknesses on 0.62 lines
LAYER=0.3; BEAD=0.62
TH=30.0                 # tilt back from straight down
L=32.4                  # 108 layers
NECK_Z=(9.3,23.1)       # 46 layers
NOTCHES=[(1.2,6.3),(26.1,31.2)]  # 17 layers each
WD=2.9                  # crosswire diameter (Measured)
UT=-1.5                 # clip top, below wire undersides (wire bottom = 0)
NOTCH_D=1.24
LIP_T=5*BEAD            # 3.10
LIP_W=30*BEAD           # 18.60
NECK_W=22*BEAD          # 13.64
WALL=3*BEAD             # 1.86 (your clip)
OVER=4*BEAD             # 2.48 above the bar's top corner
HINGE_BRIDGE=4*BEAD     # 2.48 (was 2.4)
TAB_LEN=6.0; TAB_ANG=45.0
R_STYLE=0.85; R_RELIEF=0.8
# your clip's profile values (read from the file)
HALF_OUT=12.36; HALF_IN=10.5; BACK_Y=6.3; TOP_Y=13.7; OPEN_Y=-13.7; SLOT_W=1.0
BUMP=[(10.5,4.3),(8.5,2.3),(10.5,0.3)]
def profile():
    outer=box(-HALF_OUT,OPEN_Y,HALF_OUT,TOP_Y)
    cav=box(-HALF_IN,OPEN_Y-0.1,HALF_IN,BACK_Y)
    slot=box(-HALF_IN,BACK_Y-0.1,-HALF_IN+SLOT_W,TOP_Y-HINGE_BRIDGE)   # front hinge slot only
    bumps=unary_union([SP(BUMP),SP([(-x,y) for x,y in BUMP])])
    U=outer.difference(cav).difference(slot).union(bumps)
    barcav=cav.difference(bumps)
    # tab: continues the front wall, 45 deg outward, 6 mm past the wall end
    c=np.array([-(HALF_IN+HALF_OUT)/2,OPEN_Y]); d=np.array([-np.sin(np.radians(TAB_ANG)),-np.cos(np.radians(TAB_ANG))])
    n=np.array([-d[1],d[0]])*WALL/2
    tab=SP([c+n,c+n+d*TAB_LEN,c-n+d*TAB_LEN,c-n]).union(Point(c+d*TAB_LEN).buffer(WALL/2,16)).union(box(-HALF_OUT,OPEN_Y,-HALF_IN,OPEN_Y+1))
    rot=lambda g: affinity.rotate(g,TH,origin=(0,0))
    U,barcav,slot,tab=map(rot,(U,barcav,slot,tab))
    bar=rot(box(-10,OPEN_Y,10,BACK_Y))
    lit=rot(box(-10,OPEN_Y,10,OPEN_Y+0.8))
    dy=UT-(bar.bounds[3]+OVER)
    U,barcav,slot,tab,bar,lit=[affinity.translate(g,0,dy) for g in (U,barcav,slot,tab,bar,lit)]
    cx=bar.centroid.x
    top=box(-99,-99,99,UT)
    hull=unary_union([U,box(cx-LIP_W/2-2,UT-1,cx+LIP_W/2+2,UT)]).convex_hull.intersection(top)
    opening=affinity.translate(rot(box(-HALF_IN,OPEN_Y-30,HALF_IN,OPEN_Y)),0,dy)
    body=hull.difference(barcav).union(U.intersection(top)).difference(opening).difference(slot)
    body=body.buffer(-R_STYLE,join_style=1).buffer(R_STYLE,join_style=1).buffer(R_STYLE*0.6,join_style=1).buffer(-R_STYLE*0.6,join_style=1)
    body=body.difference(slot).difference(barcav)
    body=body.union(tab.buffer(-0.3,join_style=1).buffer(0.3,join_style=1))
    for s in (-1,1):  # rounded relief into the shoulder beside the neck
        body=body.difference(Point(cx+s*(NECK_W/2+R_RELIEF),UT).buffer(R_RELIEF,32))
    if body.geom_type!='Polygon': body=max(body.geoms,key=lambda g:g.area)
    neck=box(cx-NECK_W/2,UT-0.2,cx+NECK_W/2,WD-NOTCH_D+0.01)
    lip_low=box(cx-LIP_W/2,WD-NOTCH_D,cx+LIP_W/2,WD+0.01)
    lip_up=box(cx-LIP_W/2,WD,cx+LIP_W/2,WD-NOTCH_D+LIP_T)
    lip_up=lip_up.buffer(-0.8,join_style=1).buffer(0.8,join_style=1).union(box(cx-LIP_W/2,WD,cx+LIP_W/2,WD+1))
    return dict(body=body,neck=neck,lip_low=lip_low,lip_up=lip_up,bar=bar,lit=lit,cx=cx)
def ext(poly,z0,z1):
    m=trimesh.creation.extrude_polygon(poly,z1-z0); m.apply_translation([0,0,z0]); return m
def mesh():
    p=profile()
    parts=[ext(p['body'],0,L),ext(p['neck'],NECK_Z[0],NECK_Z[1]),ext(p['lip_up'],0,L)]
    zs=[0]+[v for n in NOTCHES for v in n]+[L]
    for a,b in zip(zs[0::2],zs[1::2]): parts.append(ext(p['lip_low'],a,b))
    m=trimesh.boolean.union(parts,engine='manifold')
    return m,p

# ---------------- 3mf writer ----------------
import zipfile, uuid, os, sys
HERE=os.path.dirname(os.path.abspath(__file__))
NAME='barrinaClip_rev1'
COPIES=[(128-25.0,128.0),(128+25.0,128.0)]   # two clips, 50 mm apart on the plate
def _u(i): return str(uuid.UUID(int=0x5bc1_0000_0000_0000_0000_0000_0000_0000+i))
def write_3mf(path,m):
    m=m.copy(); c=(m.bounds[0]+m.bounds[1])/2; m.apply_translation(-c); hz=(m.bounds[1][2]-m.bounds[0][2])/2
    verts='\n'.join(f'<vertex x="{x:.6f}" y="{y:.6f}" z="{z:.6f}"/>' for x,y,z in m.vertices)
    tris='\n'.join(f'<triangle v1="{a}" v2="{b}" v3="{c_}"/>' for a,b,c_ in m.faces)
    NS='xmlns="http://schemas.microsoft.com/3dmanufacturing/core/2015/02" xmlns:BambuStudio="http://schemas.bambulab.com/package/2021" xmlns:p="http://schemas.microsoft.com/3dmanufacturing/production/2015/06" requiredextensions="p"'
    obj=f'<?xml version="1.0" encoding="UTF-8"?>\n<model unit="millimeter" xml:lang="en-US" {NS}>\n<metadata name="BambuStudio:3mfVersion">1</metadata>\n<resources>\n<object id="1" p:UUID="{_u(1)}" type="model">\n<mesh>\n<vertices>\n{verts}\n</vertices>\n<triangles>\n{tris}\n</triangles>\n</mesh>\n</object>\n</resources>\n<build/>\n</model>\n'
    res=''; items=''; cfg_objs=''; inst=''; asm=''
    for i,(x,y) in enumerate(COPIES):
        oid=2+i
        res+=f'<object id="{oid}" p:UUID="{_u(10+i)}" type="model">\n<components>\n<component p:path="/3D/Objects/{NAME}.model" objectid="1" p:UUID="{_u(20+i)}" transform="1 0 0 0 1 0 0 0 1 0 0 0"/>\n</components>\n</object>\n'
        items+=f'<item objectid="{oid}" p:UUID="{_u(30+i)}" transform="1 0 0 0 1 0 0 0 1 {x} {y} {hz:.6f}" printable="1"/>\n'
        cfg_objs+=f'<object id="{oid}">\n<metadata key="name" value="{NAME}"/>\n<metadata key="extruder" value="1"/>\n<part id="1" subtype="normal_part">\n<metadata key="name" value="{NAME}"/>\n<metadata key="matrix" value="1 0 0 0 0 1 0 0 0 0 1 0 0 0 0 1"/>\n</part>\n</object>\n'
        inst+=f'<model_instance>\n<metadata key="object_id" value="{oid}"/>\n<metadata key="instance_id" value="0"/>\n<metadata key="identify_id" value="{100+i}"/>\n</model_instance>\n'
        asm+=f'<assemble_item object_id="{oid}" instance_id="0" transform="1 0 0 0 1 0 0 0 1 {x} {y} {hz:.6f}" offset="0 0 0"/>\n'
    top=f'<?xml version="1.0" encoding="UTF-8"?>\n<model unit="millimeter" xml:lang="en-US" {NS}>\n<metadata name="Application">BambuStudio-02.06.00.51</metadata>\n<metadata name="OrcaSlicer">2.4.2</metadata>\n<metadata name="BambuStudio:3mfVersion">1</metadata>\n<metadata name="Title">{NAME}</metadata>\n<resources>\n{res}</resources>\n<build p:UUID="{_u(40)}">\n{items}</build>\n</model>\n'
    cfg=f'<?xml version="1.0" encoding="UTF-8"?>\n<config>\n{cfg_objs}<plate>\n<metadata key="plater_id" value="1"/>\n<metadata key="plater_name" value=""/>\n<metadata key="locked" value="false"/>\n{inst}</plate>\n<assemble>\n{asm}</assemble>\n</config>\n'
    ct='<?xml version="1.0" encoding="UTF-8"?>\n<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">\n<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>\n<Default Extension="model" ContentType="application/vnd.ms-package.3dmanufacturing-3dmodel+xml"/>\n<Default Extension="png" ContentType="image/png"/>\n<Default Extension="gcode" ContentType="text/x.gcode"/>\n</Types>\n'
    rels='<?xml version="1.0" encoding="UTF-8"?>\n<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">\n<Relationship Target="/3D/3dmodel.model" Id="rel-1" Type="http://schemas.microsoft.com/3dmanufacturing/2013/01/3dmodel"/>\n</Relationships>\n'
    mrels=f'<?xml version="1.0" encoding="UTF-8"?>\n<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">\n<Relationship Target="/3D/Objects/{NAME}.model" Id="rel-1" Type="http://schemas.microsoft.com/3dmanufacturing/2013/01/3dmodel"/>\n</Relationships>\n'
    settings=open(os.path.join(HERE,'barrinaClip_settings_base.json')).read()   # copied unchanged from my existing U-clip 3mf
    with zipfile.ZipFile(path,'w',zipfile.ZIP_DEFLATED) as z:
        z.writestr('[Content_Types].xml',ct); z.writestr('_rels/.rels',rels)
        z.writestr('3D/3dmodel.model',top); z.writestr('3D/_rels/3dmodel.model.rels',mrels)
        z.writestr(f'3D/Objects/{NAME}.model',obj)
        z.writestr('Metadata/project_settings.config',settings); z.writestr('Metadata/model_settings.config',cfg)
        z.writestr('Metadata/filament_sequence.json','{"plate_1":{"nozzle_sequence":[],"optimal_assignment":[],"sequence":[]}}')
if __name__=='__main__':
    out=sys.argv[1] if len(sys.argv)>1 else '.'
    m,p=mesh()
    assert m.is_watertight
    print('watertight',m.is_watertight,'volume mm3',round(m.volume,1),'size',np.round(m.bounds[1]-m.bounds[0],2))
    print('bar top below wires',round(-p['bar'].bounds[3],2),'lip top above wire top',round(m.bounds[1][1]-WD,2))
    write_3mf(os.path.join(out,NAME+'.3mf'),m)
