"""Read-only extractor for Naughty Dog PSARC archives (Oodle-compressed, as in
TLOU Part I PC). Uses the game's own oo2core_9_win64.dll for decompression.

usage: psarc.py <archive> list [filter]
       psarc.py <archive> extract <path inside archive> <out file>
       (set OODLE_DLL to the full path of oo2core_9_win64.dll)
"""
import ctypes, hashlib, os, struct, sys


class Psarc:
    def __init__(self, path):
        self.f = open(path, 'rb')
        h = self.f.read(32)
        magic, major, minor, comp, toc_len, entry_size, count, self.block, flags = struct.unpack('>4sHH4sIIIII', h)
        if magic != b'PSAR' or entry_size != 30:
            raise ValueError('not a supported PSARC (magic %r, entry size %d)' % (magic, entry_size))
        self.comp = comp
        toc = self.f.read(toc_len - 32)
        self.entries = []
        self.md5s = []
        for i in range(count):
            e = toc[i * 30:(i + 1) * 30]
            self.md5s.append(e[:16])
            block = struct.unpack('>I', e[16:20])[0]
            size = int.from_bytes(e[20:25], 'big')
            offset = int.from_bytes(e[25:30], 'big')
            self.entries.append((block, size, offset))
        width = 2 if self.block <= 0x10000 else 3 if self.block <= 0x1000000 else 4
        rest = toc[count * 30:]
        self.sizes = [int.from_bytes(rest[i:i + width], 'big') for i in range(0, len(rest) - width + 1, width)]
        self.oodle = None
        self.names = self.read(0).decode('utf-8').rstrip('\0').split('\0')  # entry 0 = manifest, NUL-separated

    def _decompress(self, data, out_len):
        if self.oodle is None:
            self.oodle = ctypes.WinDLL(os.environ['OODLE_DLL'])
            self.oodle.OodleLZ_Decompress.restype = ctypes.c_int64
        out = ctypes.create_string_buffer(out_len)
        n = self.oodle.OodleLZ_Decompress(data, ctypes.c_int64(len(data)), out, ctypes.c_int64(out_len),
                                          1, 0, 0, None, 0, None, None, None, 0, 3)
        if n != out_len:
            raise ValueError('Oodle decompression failed (%d of %d bytes)' % (n, out_len))
        return out.raw

    def read(self, index):
        block, size, offset = self.entries[index]
        out = bytearray()
        self.f.seek(offset)
        while len(out) < size:
            want = min(self.block, size - len(out))
            stored = self.sizes[block] or self.block
            data = self.f.read(stored)
            out += data if stored == want else self._decompress(data, want)
            block += 1
        return bytes(out)

    def find(self, name):
        """Entry index for a path. Entries are keyed by MD5 of the path and are
        not in manifest order, so the manifest position can't be used."""
        want = hashlib.md5(name.strip('/').encode()).digest()
        for i, md5 in enumerate(self.md5s):
            if md5 == want:
                return i
        return None

    def files(self):
        """(path, uncompressed size) for every file in the archive."""
        out = []
        for n in self.names:
            i = self.find(n)
            out.append((n, self.entries[i][1] if i is not None else -1))
        return out


if __name__ == '__main__':
    p = Psarc(sys.argv[1])
    if sys.argv[2] == 'list':
        flt = sys.argv[3].lower() if len(sys.argv) > 3 else ''
        for n, size in p.files():
            if flt in n.lower(): print(size, n)
    elif sys.argv[2] == 'extract':
        i = p.find(sys.argv[3])
        if i is None:
            sys.exit('not in archive: ' + sys.argv[3])
        data = p.read(i)
        with open(sys.argv[4], 'wb') as o: o.write(data)
        print('wrote %d bytes to %s' % (len(data), sys.argv[4]))
