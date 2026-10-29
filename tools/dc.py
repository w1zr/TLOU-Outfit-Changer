"""Minimal reader for Naughty Dog DC (.bin) script files.

Layout seen in TLOU Part I PC bin/dc1:
  0x00 '00CD'  0x04 version  0x08 size of data  0x0C string-table offset
  0x10 module header: u32 ?, u32 entry count, u64 entries offset
  entries: {u64 name sid, u64 type sid, u64 ptr}   (24 bytes)
  after `size`: u32 byte count, then bitmap, one bit per qword, set = qword is a pointer (file offset)
Strings are SIDs: FNV-1a 64.
"""
import re, struct, sys

def sid(s):
    h = 0xCBF29CE484222325
    for b in s.encode():
        h ^= b
        h = (h * 0x100000001B3) & 0xFFFFFFFFFFFFFFFF
    return h

class DC:
    def __init__(self, data):
        assert data[:4] == b'00CD', 'not a DC file'
        self.d = data
        self.size, self.strtab = struct.unpack_from('<II', data, 8)
        bm = data[self.size + 4:]  # u32 bitmap byte count first
        self.ptrs = set()
        for i in range(self.size // 8):
            if i // 8 < len(bm) and bm[i // 8] >> (i % 8) & 1:
                self.ptrs.add(i * 8)
        _, n, off = struct.unpack_from('<IIQ', data, 0x10)
        self.entries = [struct.unpack_from('<QQQ', data, off + 24 * i) for i in range(n)]

    def u64(self, o): return struct.unpack_from('<Q', self.d, o)[0]
    def u32(self, o): return struct.unpack_from('<I', self.d, o)[0]
    def is_ptr(self, o): return o in self.ptrs
    def cstr(self, o):
        e = self.d.index(b'\0', o)
        return self.d[o:e].decode('latin1')

def names_from(blobs):
    out = {}
    for b in blobs:
        for m in re.findall(rb'[\x21-\x7e]{3,}', b):
            s = m.decode('latin1')
            out[sid(s)] = s
            for part in re.split(r'[\s"\'(),]+', s):
                if len(part) >= 3: out[sid(part)] = part
    return out
