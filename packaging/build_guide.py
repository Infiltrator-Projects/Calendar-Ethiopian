#!/usr/bin/env python3
"""Create the illustrated public calendar guide from provider-owned facts."""
import json
import sys
from pathlib import Path
from reportlab.lib.colors import HexColor
from reportlab.lib.pagesizes import A4
from reportlab.lib.utils import simpleSplit
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas

W,H=A4
INK=HexColor("#22334A")
RUST=HexColor("#B45C36")
FAINT=HexColor("#64788C")
PALE=HexColor("#F1ECE3")
BG=HexColor("#FAF8F3")
FONT="Helvetica"
BOLD="Helvetica-Bold"
for name,file in [("Guide","DejaVuSans.ttf"),("GuideBold","DejaVuSans-Bold.ttf")]:
    file=Path("/usr/share/fonts/truetype/dejavu")/file
    if file.exists():
        pdfmetrics.registerFont(TTFont(name,str(file)))
if "Guide" in pdfmetrics.getRegisteredFontNames():
    FONT,BOLD="Guide","GuideBold"
def draw(c,s,x,y,size=10,bold=False,color=INK):
    c.setFillColor(color);c.setFont(BOLD if bold else FONT,size);c.drawString(x,y,str(s))
def para(c,s,x,y,width,size=10,step=18):
    c.setFont(FONT,size);c.setFillColor(INK)
    for paragraph in str(s).split("\n"):
        for line in simpleSplit(paragraph,FONT,size,width):
            c.drawString(x,y,line);y-=step
    return y
def page(c,index,title):
    c.setFillColor(BG);c.rect(0,0,W,H,fill=1,stroke=0)
    draw(c,"INFILTRATOR  /  CALENDAR LIBRARY",48,H-37,8,True,FAINT)
    draw(c,title,48,H-103,22,True)
    c.setStrokeColor(PALE);c.line(48,49,W-48,49)
    draw(c,"ILLUSTRATED CALENDAR GUIDE",48,30,8,False,FAINT)
    draw(c,f"{index} / 3",W-78,30,8,False,FAINT)
def ring(c,x,y,months):
    import math
    c.setStrokeColor(RUST);c.setLineWidth(6);c.circle(x,y,55,fill=0,stroke=1)
    for k in range(months):
        a=math.pi*2*k/12
        c.setStrokeColor(FAINT);c.setLineWidth(1)
        c.line(x+48*math.cos(a),y+48*math.sin(a),
               x+66*math.cos(a),y+66*math.sin(a))
    draw(c,str(months),x-20,y+2,28,True)
    draw(c,"MONTHS",x-23,y-18,8,True,FAINT)
def main():
    data=json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
    dest=Path(sys.argv[2]);dest.parent.mkdir(parents=True,exist_ok=True)
    c=canvas.Canvas(str(dest),pagesize=A4,invariant=1)
    c.setTitle(data["title"]+" - Illustrated guide")
    c.setAuthor("Infiltrator Projects")
    page(c,1,"WHAT IS THIS CALENDAR?")
    draw(c,data["title"],48,H-161,15,True,RUST)
    para(c,data["intro"],48,H-202,305,11,21)
    ring(c,W-118,H-245,data["months"])
    c.setFillColor(PALE);c.roundRect(48,H-461,W-96,112,10,fill=1,stroke=0)
    draw(c,"THE IDEA IN ONE SENTENCE",65,H-377,10,True,RUST)
    para(c,data["summary"],65,H-405,W-133,12,20)
    draw(c,data["epoch_heading"],48,H-532,11,True,RUST)
    para(c,data["epoch"],48,H-565,W-96,11,21)
    draw(c,"For curious readers - not a programmer's manual.",48,95,10,False,FAINT)
    c.showPage()
    page(c,2,"HOW A YEAR IS ARRANGED")
    para(c,data["year_rule"],48,H-149,W-96,11,19)
    x,y,width=48,H-306,W-96
    for i in range(data["months"]):
        sx=x+i*width/data["months"]
        c.setFillColor(INK if i%2 else FAINT)
        c.rect(sx,y,width/data["months"]-1,48,fill=1,stroke=0)
        draw(c,str(i+1),sx+8,y+17,9,True,HexColor("#FFFFFF"))
    at=data.get("intercalary_after_month",data["months"])
    marker=x+width*at/data["months"]
    c.setFillColor(RUST);c.rect(min(marker-3,x+width-7),y,6,48,fill=1,stroke=0)
    draw(c,data["bar_caption"],48,y-28,10,True)
    draw(c,data["bar_highlight"],48,y-51,9,False,RUST)
    draw(c,data["period_heading"],48,H-423,11,True,RUST)
    months=data["month_names"]
    columns=3 if len(months)<=13 else 4
    rows=(len(months)+columns-1)//columns
    cell=(W-96)/columns
    for i,name in enumerate(months):
        col=i//rows;row=i%rows
        px=48+col*cell;py=H-456-row*31
        c.setFillColor(PALE);c.roundRect(px,py-7,cell-10,27,4,fill=1,stroke=0)
        draw(c,f"{i+1:02d}  {name}",px+8,py+2,8.8)
    draw(c,data["after_heading"],48,138,10,True,RUST)
    para(c,data["after_note"],48,114,W-96,9.5,16)
    c.showPage()
    page(c,3,"HISTORY AND INTERPRETATION")
    draw(c,data["history_heading"],48,H-150,12,True,RUST)
    para(c,data["history"],48,H-180,W-96,11,19)
    y=H-350
    c.setLineWidth(5);c.setStrokeColor(FAINT);c.line(76,y,W-76,y)
    c.setStrokeColor(RUST);c.line(76,y-51,W-96,y-51)
    for i in range(4):
        px=76+i*126
        c.setFillColor(INK);c.circle(px,y,4,fill=1,stroke=0)
        c.setFillColor(RUST);c.circle(px-5*i if data.get("drifts") else px,y-51,4,fill=1,stroke=0)
    draw(c,data["comparison_top"],76,y+19,8,True,FAINT)
    draw(c,data["comparison_bottom"],76,y-76,8,True,RUST)
    draw(c,"WHAT THE MODEL DOES NOT CLAIM",48,H-541,11,True,RUST)
    para(c,data["limits"],48,H-569,W-96,10.5,19)
    draw(c,"More history and evidence:",48,125,9,True)
    para(c,data["source"],48,104,W-96,8,13)
    c.save()
if __name__=="__main__":
    main()
