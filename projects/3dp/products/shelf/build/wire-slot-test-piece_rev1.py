# wire-slot-test-piece_rev1 build script (product.unicoly-wire-shelf), 2026-09-30.
# Run: python3 wire-slot-test-piece_rev1.py  -> writes wire-slot-test-piece_rev1.stl (needs numpy).
# Output is already in print orientation (on its side): front face (Z=0) on the bed,
# labels on the face up from the bed (Z=12), slot openings face sideways (+Y).
import numpy as np, struct
boxes=[]
def box(x0,x1,y0,y1,z0,z1): boxes.append((x0,x1,y0,y1,z0,z1))
L,H,D=85.0,12.0,12.0; depth=3.0; pitch=7.0
xc=[7.5+pitch*i for i in range(11)]; w=[round(2.5+0.1*(i+1),1) for i in range(11)]
# base below slots (print frame: X along bar, Y = installed up, Z = installed front-back)
box(0,L,0,H-depth+0.1,0,D)
# teeth between slots
edges=[0.0]
for c,ww in zip(xc,w): edges += [c-ww/2, c+ww/2]
edges.append(L)
for i in range(0,len(edges),2): box(edges[i],edges[i+1],H-depth,H,0,D)
# labels on top face (Z=D): rib=5, pip=1, column below each slot
rz0,rz1=D-0.1,D+0.6
for n,c in enumerate(xc,1):
    ribs,pips=divmod(n,5); y=H-depth-0.8
    for r in range(ribs):
        box(c-1.7,c+1.7,y-1.2,y,rz0,rz1); y-=1.9
    for p in range(pips):
        col=p%2; 
        if p%2==0 and p>0: y-=2.1
        px=c-1.0 if col==0 else c+1.0
        box(px-0.7,px+0.7,y-1.4,y,rz0,rz1)
tris=[]
for x0,x1,y0,y1,z0,z1 in boxes:
    v=np.array([[x0,y0,z0],[x1,y0,z0],[x1,y1,z0],[x0,y1,z0],[x0,y0,z1],[x1,y0,z1],[x1,y1,z1],[x0,y1,z1]])
    f=[(0,2,1),(0,3,2),(4,5,6),(4,6,7),(0,1,5),(0,5,4),(2,3,7),(2,7,6),(1,2,6),(1,6,5),(0,4,7),(0,7,3)]
    for a,b,cc in f: tris.append((v[a],v[b],v[cc]))
with open('wire-slot-test-piece_rev1.stl','wb') as fh:
    fh.write(b'wire-slot-test-piece_rev1'.ljust(80,b' ')); fh.write(struct.pack('<I',len(tris)))
    for a,b,cc in tris:
        n=np.cross(b-a,cc-a); n=n/np.linalg.norm(n)
        fh.write(struct.pack('<12fH',*n,*a,*b,*cc,0))
allv=np.array([p for t in tris for p in t])
print('bounds',allv.min(0),allv.max(0),'tris',len(tris))
print('slot widths',[round(edges[2*i+2]-edges[2*i+1],2) for i in range(11)])
print('min wall',min(edges[2*i+1]-edges[2*i] for i in range(1,11)))
