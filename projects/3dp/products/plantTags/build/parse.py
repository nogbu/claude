"""Parts of plantTags.3mf (unzipped to ./src) in plate placement: out[object id] = [(path, id, vertices, triangles)]."""
import xml.etree.ElementTree as ET, numpy as np, re
NS={'m':'http://schemas.microsoft.com/3dmanufacturing/core/2015/02'}
def T(s):
    a=np.array(list(map(float,s.split())));M=np.eye(4);M[:3,:3]=a[:9].reshape(3,3).T;M[:3,3]=a[9:];return M
def meshes(path,oid):
    r=ET.parse(path).getroot()
    for o in r.iter('{%s}object'%NS['m']):
        if o.get('id')==str(oid):
            v=np.array([[float(x.get(k)) for k in 'xyz'] for x in o.iter('{%s}vertex'%NS['m'])])
            t=np.array([[int(x.get(k)) for k in ('v1','v2','v3')] for x in o.iter('{%s}triangle'%NS['m'])])
            return v,t
root=ET.parse('src/3D/3dmodel.model').getroot()
out={}
for o in root.find('m:resources',NS).findall('m:object',NS):
    for c in o.iter('{%s}component'%NS['m']):
        p=c.get('{http://schemas.microsoft.com/3dmanufacturing/production/2015/06}path')
        v,t=meshes('src'+p,c.get('objectid')); M=T(c.get('transform'))
        V=(np.c_[v,np.ones(len(v))]@M.T)[:,:3]
        out.setdefault(o.get('id'),[]).append((p,c.get('objectid'),V,t))
if __name__=='__main__':
    for k,L in out.items():
        for p,i,V,t in L: print(k,p,i,len(t),V.min(0).round(3),V.max(0).round(3))
