#!/usr/bin/env python3
"""Procedural chiptune-style audio generator (pure Python, wave module).

Writes 16-bit PCM WAV files into game/assets/audio/:
  music_theme.wav        - main menu / overworld loop (upbeat)
  music_snow.wav         - calm, bell-like snow town loop
  music_beach.wav        - sunny tropical loop
  sfx_coin.wav           - coin pickup blip
  sfx_jump.wav           - jump swoosh
  sfx_hurt.wav           - damage buzz
  sfx_stomp.wav          - slime stomp
  sfx_unlock.wav         - milestone jingle
  sfx_click.wav          - ui click
  sfx_levelup.wav        - world transition fanfare
Run:  python3 tools/gen_audio.py
"""
import os
import math
import random
import struct
import wave

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
OUT = os.path.join(ROOT, "game", "assets", "audio")
SR = 22050

os.makedirs(OUT, exist_ok=True)


def write_wav(name, samples):
    """samples: list of floats in [-1, 1] -> mono 16-bit wav"""
    peak = max((abs(s) for s in samples), default=1.0) or 1.0
    scale = 0.85 / max(peak, 1e-9) * 32767
    data = b"".join(struct.pack("<h", int(max(-1, min(1, s / 0.85)) * 32767 if peak <= 1 else s * scale))
                    for s in samples)
    # simpler: normalize then clamp
    data = bytearray()
    for s in samples:
        v = int(round(max(-1.0, min(1.0, s)) * 32000))
        data += struct.pack("<h", v)
    path = os.path.join(OUT, name)
    with wave.open(path, "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes(bytes(data))
    print("wrote", name, f"({len(samples)/SR:.2f}s)")


def env_ad(t, a, d, total):
    if t < a:
        return t / a
    x = (t - a) / max(d, 1e-9)
    return max(0.0, math.exp(-3.0 * x))


def tone(freq, dur, kind="square", vol=0.5, vib=0.0, slide=0.0):
    n = int(dur * SR)
    out = []
    for i in range(n):
        t = i / SR
        f = freq * (1.0 + slide * t / max(dur, 1e-9))
        ph = 2 * math.pi * f * t
        if kind == "square":
            v = 1.0 if math.sin(ph) >= 0 else -1.0
        elif kind == "saw":
            v = 2.0 * ((ph / (2 * math.pi)) % 1.0) - 1.0
        elif kind == "tri":
            v = 2.0 * abs(2.0 * ((ph / (2 * math.pi)) % 1.0) - 1.0) - 1.0
        elif kind == "sine":
            v = math.sin(ph)
        else:  # noise
            v = random.uniform(-1, 1)
        if vib:
            v *= 1.0 + vib * math.sin(2 * math.pi * 6 * t)
        out.append(v * vol)
    return out


def apply_env(seg, a, d):
    total = len(seg) / SR
    return [s * env_ad(i / SR, a, d, total) for i, s in enumerate(seg)]


def mix(dst, src, at):
    for i, s in enumerate(src):
        j = at + i
        if j >= len(dst):
            dst.extend([0.0] * (j - len(dst) + 1))
        dst[j] += s


NOTE = {}
_names = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]
for octv in range(1, 7):
    for k, nm in enumerate(_names):
        NOTE[f"{nm}{octv}"] = 440.0 * 2 ** ((octv - 4) + (k - 9) / 12.0)
NOTE["A4"] = 440.0


def seq(notes, beat, kind="square", vol=0.4, slide=0.0):
    """notes: list of (pitch_or_None, beats)"""
    out = []
    for p, b in notes:
        n = int(b * beat * SR)
        if p is None:
            out += [0.0] * n
        else:
            seg = tone(NOTE[p], b * beat, kind, vol, slide=slide)
            seg = apply_env(seg, 0.005, b * beat * 0.9)
            out += seg
    return out


# ---------------------------------------------------------------- sfx

def gen_sfx():
    write_wav("sfx_coin.wav",
              seq([("E5", 0.06), ("B5", 0.16)], 0.25, "square", 0.5))
    write_wav("sfx_jump.wav",
              tone(300, 0.18, "square", 0.4, slide=1.6))
    write_wav("sfx_hurt.wav",
              seq([("D4", 0.09), ("A#3", 0.09), ("F3", 0.18)], 0.35, "saw", 0.5))
    stomp = apply_env(tone(180, 0.12, "square", 0.5, slide=-0.9), 0.001, 0.12) \
        + apply_env(noise := [random.uniform(-1, 1) for _ in range(int(0.06 * SR))], 0.001, 0.06)
    buf = [0.0] * int(0.2 * SR)
    mix(buf, stomp, 0)
    write_wav("sfx_stomp.wav", buf)
    click = apply_env(tone(900, 0.04, "square", 0.35), 0.001, 0.04)
    write_wav("sfx_click.wav", click)
    write_wav("sfx_unlock.wav",
              seq([("C5", 0.10), ("E5", 0.10), ("G5", 0.10), ("C6", 0.30)], 0.42, "square", 0.45))
    write_wav("sfx_levelup.wav",
              seq([("G4", .12), ("C5", .12), ("E5", .12), ("G5", .12),
                   ("C6", .12), ("E6", .12), ("G6", .40)], 0.5, "square", 0.45))


# ---------------------------------------------------------------- music

def bass_line(root_seq, beat):
    out = []
    for r in root_seq:
        f = NOTE[r] / 2.0
        n = int(beat * 2 * SR)
        seg = []
        for i in range(n):
            t = i / SR
            v = 1.0 if math.sin(2 * math.pi * f * t) >= 0 else -1.0
            seg.append(v * 0.30 * env_ad(t, 0.005, beat * 1.8, beat * 2))
        out += seg
    return out


def melody(notes, beat, kind, vol):
    return seq(notes, beat, kind, vol)


def drum(pattern, beat):
    """pattern: string per 8th: k kick, s snare, h hat, . rest"""
    out = []
    step = int(beat * 0.5 * SR)
    for ch in pattern:
        n = step
        if ch == "k":
            seg = apply_env(tone(90, 0.12, "sine", 0.8, slide=-0.5), 0.001, 0.12)
        elif ch == "s":
            seg = apply_env([random.uniform(-1, 1) for _ in range(int(0.09 * SR))], 0.001, 0.09)
            seg = [v * 0.5 for v in seg]
        elif ch == "h":
            seg = [random.uniform(-1, 1) * 0.18 * math.exp(-18 * i / SR) for i in range(int(0.05 * SR))]
        else:
            seg = [0.0]
        buf = [0.0] * n
        mix(buf, seg, 0)
        out += buf
    return out


def gen_music_theme():
    beat = 60.0 / 132.0
    bars = 8
    total = int(bars * 4 * beat * SR) + SR
    buf = [0.0] * total
    roots = ["A3", "A3", "F3", "F3", "G3", "G3", "E3", "E3"][:bars]
    mix(buf, bass_line(roots, beat), 0)
    mel = [("E5", .5), ("A5", .5), ("C6", 1), ("B5", .5), ("A5", .5), ("E5", 1),
           ("F5", .5), ("A5", .5), ("C6", 1), ("A5", 1), ("G5", .5), ("A5", .5),
           ("B5", 1), ("G5", .5), ("A5", .5), ("C6", 1), ("B5", .5), ("A5", .5),
           ("G5", 1), ("E5", .5), ("G5", .5), ("A5", 1), ("G5", .5), ("E5", .5),
           ("D5", 1), ("E5", .5), ("G5", .5), ("A5", 1.5), (None, .5)]
    mix(buf, melody(mel, beat, "square", 0.28), 0)
    arp = []
    for r, ch in zip(roots, ["Am", "Am", "F", "F", "G", "G", "Em", "Em"]):
        chord = {"Am": ["A4", "C5", "E5"], "F": ["F4", "A4", "C5"],
                 "G": ["G4", "B4", "D5"], "Em": ["E4", "G4", "B4"]}[ch]
        for rep in range(4):
            for c in chord:
                arp.append((c, 0.25))
    mix(buf, melody(arp, beat, "triangle", 0.12), 0)
    mix(buf, drum("k.h.s.h." if False else "khshkhs h".replace(" ", "."), beat), 0)
    trim(buf, total)
    fade_out(buf)
    write_wav("music_theme.wav", buf)


def gen_music_snow():
    beat = 60.0 / 92.0
    total = int(8 * 4 * beat * SR) + SR
    buf = [0.0] * total
    pad_chords = [["C4", "E4", "G4"], ["A3", "C4", "E4"], ["F3", "A3", "C4"], ["G3", "B3", "D4"]]
    t = 0
    for ci in range(8):
        ch = pad_chords[ci % 4]
        for p in ch:
            seg = apply_env(tone(NOTE[p], beat * 4, "sine", 0.10), 0.4, beat * 3.6)
            mix(buf, seg, int(t * SR))
        t += beat * 4
    bells = [("E5", 1), ("G5", 1), ("C6", 2), ("B5", 1), ("G5", 1), ("E5", 2),
             ("A5", 1), ("C6", 1), ("G5", 2), ("E5", 1), ("D5", 1), ("C5", 2)]
    mix(buf, melody(bells, beat, "sine", 0.22), 0)
    mix(buf, bass_line(["C3", "A2", "F2", "G2", "C3", "A2", "F2", "G2"], beat), 0)
    trim(buf, total)
    fade_out(buf)
    write_wav("music_snow.wav", buf)


def gen_music_beach():
    beat = 60.0 / 112.0
    total = int(8 * 4 * beat * SR) + SR
    buf = [0.0] * total
    roots = ["C3", "C3", "F2", "F2", "G2", "G2", "F2", "G2"]
    mix(buf, bass_line(roots, beat), 0)
    mel = [("E5", .5), ("G5", .5), ("A5", 1), ("G5", .5), ("E5", .5), ("D5", 1),
           ("C5", .5), ("D5", .5), ("F5", 1), ("A5", .5), ("G5", .5), ("F5", 1),
           ("A5", .5), ("G5", .5), ("F5", 1), ("E5", .5), ("D5", .5), ("C5", 1),
           ("D5", .5), ("E5", .5), ("G5", 1), ("A5", 1), ("G5", 1), ("E5", 1)]
    mix(buf, melody(mel, beat, "triangle", 0.30), 0)
    # steel-drum-ish square harmony
    for i, r in enumerate(roots):
        pass
    shak = []
    for _ in range(64):
        shak.append(0.5)
    # maracas: filtered noise on offbeats
    step = int(beat * 0.5 * SR)
    for i in range(64):
        if i % 2 == 1:
            seg = [random.uniform(-1, 1) * 0.10 * math.exp(-14 * j / SR) for j in range(step)]
            mix(buf, seg, i * step)
    kick = []
    pat = "k..sk..kk..sk..k" * 4
    mix(buf, drum(pat.replace(" ", "."), beat), 0)
    trim(buf, total)
    fade_out(buf)
    write_wav("music_beach.wav", buf)


def trim(buf, n):
    del buf[n:]


def fade_out(buf, secs=1.2):
    n = int(secs * SR)
    L = len(buf)
    for i in range(min(n, L)):
        buf[L - n + i] *= (1 - i / n)


if __name__ == "__main__":
    random.seed(7)
    gen_sfx()
    gen_music_theme()
    gen_music_snow()
    gen_music_beach()
    print("audio generation complete")
