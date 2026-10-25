"""Write a Final Cut Pro 7 XML (xmeml v4) sequence that Premiere Pro can import."""
import json, sys
from xml.sax.saxutils import escape

caps = json.load(open(sys.argv[1]))
out_xml, out_srt = sys.argv[2], sys.argv[3]
FPS, W, H = 60, 1080, 1920
MASTER_FRAMES, END = 691, 811

def rate():
    return f"<rate><timebase>{FPS}</timebase><ntsc>FALSE</ntsc></rate>"

def vfmt():
    return (f"<samplecharacteristics>{rate()}<width>{W}</width><height>{H}</height>"
            "<anamorphic>FALSE</anamorphic><pixelaspectratio>square</pixelaspectratio>"
            "<fielddominance>none</fielddominance></samplecharacteristics>")

defined = set()
def fileref(fid, name, path, dur, still=False, audio=False):
    if fid in defined:
        return f'<file id="{fid}"/>'
    defined.add(fid)
    media = f"<video>{vfmt()}</video>"
    if audio:
        media += ("<audio><samplecharacteristics><depth>16</depth><samplerate>48000</samplerate>"
                  "</samplecharacteristics><channelcount>2</channelcount></audio>")
    return (f'<file id="{fid}"><name>{escape(name)}</name><pathurl>{escape(path)}</pathurl>'
            f"{rate()}<duration>{dur}</duration><media>{media}</media></file>")

def vclip(cid, name, fid, path, start, end, src_in, src_dur, still=False, audio=False, links=""):
    return (f'<clipitem id="{cid}"><name>{escape(name)}</name><enabled>TRUE</enabled>'
            f"<duration>{src_dur}</duration>{rate()}<start>{start}</start><end>{end}</end>"
            f"<in>{src_in}</in><out>{src_in + end - start}</out>"
            + ("<stillframe>TRUE</stillframe>" if still else "")
            + fileref(fid, name, path, src_dur, still, audio)
            + (f"<sourcetrack><mediatype>video</mediatype></sourcetrack>" ) + links + "</clipitem>")

def links(track_ids):
    s = ""
    for i, (cid, mt, tr) in enumerate(track_ids):
        s += (f"<link><linkclipref>{cid}</linkclipref><mediatype>{mt}</mediatype>"
              f"<trackindex>{tr}</trackindex><clipindex>1</clipindex>"
              + (f"<groupindex>1</groupindex>" if mt == "audio" else "") + "</link>")
    return s

master = "media/shiba_bed_vertical_master.mp4"
L = links([("v-master", "video", 1), ("a-master-1", "audio", 1), ("a-master-2", "audio", 2)])
STILL = 108000  # long nominal duration for still images

v1 = (vclip("v-master", "shiba_bed_vertical_master.mp4", "f-master", master, 0, MASTER_FRAMES, 0, MASTER_FRAMES, audio=True, links=L)
      + vclip("v-freeze", "endcard_freeze.png", "f-freeze", "media/endcard_freeze.png", MASTER_FRAMES, END, 0, STILL, still=True))
v2 = "".join(vclip(f"v-{c['file']}", f"{c['file']}.png", f"f-{c['file']}", f"media/telop/{c['file']}.png",
                   c["start"], c["end"], 0, STILL, still=True) for c in caps)
v3 = vclip("v-header", "telop_00_header.png", "f-header", "media/telop/telop_00_header.png", 0, MASTER_FRAMES, 0, STILL, still=True)

def aclip(cid, ch):
    return (f'<clipitem id="{cid}"><name>shiba_bed_vertical_master.mp4</name><enabled>TRUE</enabled>'
            f"<duration>{MASTER_FRAMES}</duration>{rate()}<start>0</start><end>{MASTER_FRAMES}</end>"
            f'<in>0</in><out>{MASTER_FRAMES}</out><file id="f-master"/>'
            f"<sourcetrack><mediatype>audio</mediatype><trackindex>{ch}</trackindex></sourcetrack>{L}</clipitem>")

def vtrack(items):
    return f"<track>{items}<enabled>TRUE</enabled><locked>FALSE</locked></track>"

xml = ('<?xml version="1.0" encoding="UTF-8"?>\n<!DOCTYPE xmeml>\n<xmeml version="4">'
       f'<sequence id="seq-1"><name>豆柴ショート_新しいベッドで寝床づくり</name><duration>{END}</duration>{rate()}'
       "<timecode><rate><timebase>60</timebase><ntsc>FALSE</ntsc></rate><string>00:00:00:00</string>"
       "<frame>0</frame><displayformat>NDF</displayformat></timecode>"
       f"<media><video><format>{vfmt()}</format>{vtrack(v1)}{vtrack(v2)}{vtrack(v3)}</video>"
       "<audio><numOutputChannels>2</numOutputChannels>"
       "<format><samplecharacteristics><depth>16</depth><samplerate>48000</samplerate></samplecharacteristics></format>"
       f"<track>{aclip('a-master-1', 1)}<enabled>TRUE</enabled><locked>FALSE</locked><outputchannelindex>1</outputchannelindex></track>"
       f"<track>{aclip('a-master-2', 2)}<enabled>TRUE</enabled><locked>FALSE</locked><outputchannelindex>2</outputchannelindex></track>"
       "</audio></media></sequence></xmeml>\n")
open(out_xml, "w", encoding="utf-8").write(xml)

def tc(f):
    ms = round(f * 1000 / FPS)
    return f"{ms // 3600000:02}:{ms // 60000 % 60:02}:{ms // 1000 % 60:02},{ms % 1000:03}"

srt = []
for i, c in enumerate(caps, 1):
    text = "\n".join(l for l, _ in c["lines"])
    srt.append(f"{i}\n{tc(c['start'])} --> {tc(c['end'])}\n{text}\n")
open(out_srt, "w", encoding="utf-8").write("\n".join(srt))
