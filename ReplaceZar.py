import os

# === File paths ===
original_iso_path = "mpo.iso"
new_iso_path = "mpo-net-patch.iso"
zar_file_path = "_zar"

# === File location in ISO (known offset) ===
zar_offset = 0x27FB0000
sector_size = 0x800  # 2048 bytes

with open(original_iso_path, "rb") as iso_in, \
     open(new_iso_path, "wb") as iso_out, \
     open(zar_file_path, "rb") as zar_file:

    # Step 1: Copy everything up to _zar file location
    iso_in.seek(0)
    while iso_in.tell() < zar_offset:
        chunk_size = min(1024 * 1024, zar_offset - iso_in.tell())
        iso_out.write(iso_in.read(chunk_size))

    # Step 2: Write _zar content
    zar_data = zar_file.read()
    iso_out.write(zar_data)

    # Step 3: Pad to next 0x800 boundary
    pad_len = (-len(zar_data)) % sector_size
    if pad_len:
        iso_out.write(b'\x00' * pad_len)

    # Step 4: Skip old _zar content + padding in original ISO
    iso_in.seek(zar_offset + ((len(zar_data) + pad_len + (sector_size - 1)) // sector_size) * sector_size)

    # Step 5: Write rest of ISO
    while True:
        data = iso_in.read(1024 * 1024)
        if not data:
            break
        iso_out.write(data)

print(f"✅ Patched ISO written to: {new_iso_path}")
