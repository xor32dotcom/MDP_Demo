import struct

# === Paths ===
original_iso_path = "mpo.iso"
new_iso_path = "mpo-net-patch.iso"
replacement_file_path = "_zar"

# === Constants ===
# Offset where the size pair (LE + BE) is located
file_size_offset = 0x2A060A

# === Get new file size ===
with open(replacement_file_path, "rb") as f:
    new_size = len(f.read())

# === Convert to little-endian and big-endian 4-byte formats ===
size_le = struct.pack("<I", new_size)
size_be = struct.pack(">I", new_size)

# === Copy original ISO and patch the size field ===
with open(original_iso_path, "rb") as infile, open(new_iso_path, "wb") as outfile:
    # Copy everything up to the patch point
    chunk_size = 1024 * 1024
    bytes_remaining = file_size_offset
    while bytes_remaining > 0:
        read_len = min(chunk_size, bytes_remaining)
        data = infile.read(read_len)
        if not data:
            raise IOError("Reached EOF before patch offset")
        outfile.write(data)
        bytes_remaining -= len(data)

    # Write new size LE+BE
    outfile.write(size_le)
    outfile.write(size_be)

    # Skip the original 8 bytes in the source ISO
    infile.seek(8, 1)

    # Write the rest of the ISO
    while True:
        data = infile.read(chunk_size)
        if not data:
            break
        outfile.write(data)

print(f"✅ Patched ISO written to: {new_iso_path}")
