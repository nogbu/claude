"""Build Delta_SEM_Sept_2026_rev1.pptx: the client's "Delta Delta_SEM_Sept 2026.pptx" with slide 10's
chart image (Picture 8, ppt/media/image23.png, used only on slide 10) replaced by
sept2026_slide10_chart.png (RAQs and Enrollments by month, Sep 2025 to Oct 2026; user upload 2026-10-07).
The picture keeps its position and width; its height follows the new image's aspect ratio.

Usage: python3 Delta_SEM_Sept_2026_rev1.py "<source deck>" <out.pptx>
"""
import os, re, sys, zipfile
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
NEW_IMG = os.path.join(HERE, 'sept2026_slide10_chart.png')
SLIDE = 'ppt/slides/slide10.xml'
MEDIA = 'ppt/media/image23.png'


def main(src, out):
    w, h = Image.open(NEW_IMG).size
    zin = zipfile.ZipFile(src)
    xml = zin.read(SLIDE).decode('utf-8')
    pic = re.search(r'<p:pic><p:nvPicPr><p:cNvPr id="9" name="Picture 8">.*?</p:pic>', xml).group(0)
    cx = int(re.search(r'<a:ext cx="(\d+)" cy="\d+"/>', pic).group(1))
    cy = round(cx * h / w)
    new_pic = re.sub(r'<a:ext cx="\d+" cy="\d+"/>', f'<a:ext cx="{cx}" cy="{cy}"/>', pic, count=1)
    xml = xml.replace(pic, new_pic)
    with zipfile.ZipFile(out, 'w', zipfile.ZIP_DEFLATED) as zout:
        for item in zin.infolist():
            if item.filename == SLIDE:
                zout.writestr(item, xml.encode('utf-8'))
            elif item.filename == MEDIA:
                zout.writestr(item, open(NEW_IMG, 'rb').read())
            else:
                zout.writestr(item, zin.read(item.filename))
    print('slide 10 picture ext', cx, cy, '->', out)


if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2])
