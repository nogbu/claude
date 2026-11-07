# bore-test-piece_rev1.py: builds bore-test-piece_rev1.stl (unicoly-wire-shelf).
# Six 12 x 12 x 17 mm sleeves, blind bores 6.0-6.5 mm x 15 deep, 2 mm end wall, 2 mm vent, ID pips on top.
# Needs only numpy. Run: python3 bore-test-piece_rev1.py (writes the STL to the current folder).
import numpy as np, struct
N=128  # segments; multiple of 8 so the square's corners fall on sample angles
W=12.0; BORE_DEPTH=15.0; END=2.0; L=BORE_DEPTH+END; VENT=2.0
SIZES=[6.0,6.1,6.2,6.3,6.4,6.5]
def ring_circle(r,y,cx,cz):
    a=np.arange(N)*2*np.pi/N
    return np.stack([cx+r*np.cos(a),np.full(N,y),cz+r*np.sin(a)],1)
def ring_square(y,cx,cz):
    a=np.arange(N)*2*np.pi/N; c,s=np.cos(a),np.sin(a)
    t=(W/2)/np.maximum(abs(c),abs(s))
    return np.stack([cx+t*c,np.full(N,y),cz+t*s],1)
def strip(A,B):  # quads between two rings of N points
    T=[]
    for i in range(N):
        j=(i+1)%N
        T+= [(A[i],A[j],B[j]),(A[i],B[j],B[i])]
    return T
def box(x0,y0,z0,x1,y1,z1):
    p=lambda x,y,z:np.array([x,y,z],float)
    v=[p(x0,y0,z0),p(x1,y0,z0),p(x1,y1,z0),p(x0,y1,z0),p(x0,y0,z1),p(x1,y0,z1),p(x1,y1,z1),p(x0,y1,z1)]
    f=[(0,2,1),(0,3,2),(4,5,6),(4,6,7),(0,1,5),(0,5,4),(1,2,6),(1,6,5),(2,3,7),(2,7,6),(3,0,4),(3,4,7)]
    return [(v[a],v[b],v[c]) for a,b,c in f]
def sleeve(d,cx,npips):
    cz=W/2
    S0,S1=ring_square(0,cx,cz),ring_square(L,cx,cz)
    C0,C1=ring_circle(d/2,0,cx,cz),ring_circle(d/2,BORE_DEPTH,cx,cz)
    V0,V1=ring_circle(VENT/2,BORE_DEPTH,cx,cz),ring_circle(VENT/2,L,cx,cz)
    T=[]
    T+=strip(S0,C0)      # open end face (y=0)
    T+=strip(C0,C1)      # bore wall
    T+=strip(C1,V0)      # bore bottom
    T+=strip(V0,V1)      # vent wall
    T+=strip(V1,S1)      # closed end face (y=L)
    T+=strip(S1,S0)      # outer walls
    body=T
    pips=[]
    for k in range(npips):  # ID pips on top, near the open end; overlap 0.2 into the body
        y=1.5+k*2.4
        pips.append(box(cx-0.7,y,W-0.2,cx+0.7,y+1.4,W+0.8))
    return body,pips
def fix_orientation(T):
    T=np.array(T)
    vol=np.einsum('ij,ij->i',T[:,0],np.cross(T[:,1],T[:,2])).sum()/6
    return (T[:,[0,2,1]] if vol<0 else T), abs(vol)
def check(T):
    from collections import Counter
    key=lambda p:tuple(np.round(p,6))
    e=Counter()
    for t in T:
        for a,b in ((0,1),(1,2),(2,0)): e[(key(t[a]),key(t[b]))]+=1
    bad=[k for k,v in e.items() if v!=1 or e.get((k[1],k[0]),0)!=1]
    return len(bad)
shells=[]
for i,d in enumerate(SIZES):
    body,pips=sleeve(d,i*(W+6),i+1)
    b,vol=fix_orientation(body)
    print(f"bore {d}: body edges bad={check(b)}, volume={vol:.1f} mm3, pips={len(pips)}")
    shells.append(b)
    for p in pips:
        pp,_=fix_orientation(p); assert check(pp)==0; shells.append(pp)
T=np.concatenate(shells)
with open('bore-test-piece_rev1.stl','wb') as f:
    f.write(b'bore-test-piece_rev1'.ljust(80,b' ')); f.write(struct.pack('<I',len(T)))
    for t in T:
        n=np.cross(t[1]-t[0],t[2]-t[0]); n/=np.linalg.norm(n) or 1
        f.write(struct.pack('<12fH',*n,*t[0],*t[1],*t[2],0))
print(len(T),"triangles; bbox",T.reshape(-1,3).min(0),T.reshape(-1,3).max(0))
