import os

#iso modding utility by mpoadmin2978

# === CONFIG ===
ORIGINAL_ISO = "mpo.iso"
NEW_ISO = "mpo-net-patch.iso"
REPLACEMENT_FILE = "_zar"

# === CONSTANTS ===
REPLACE_OFFSET = 0x27FB0000         # where _zar is in the ISO
SIZE_LE_OFFSET = 0x2A060A           # little-endian file size location
SIZE_BE_OFFSET = 0x2A06AE           # big-endian file size location
SECTOR_SIZE = 2048                  # ISO sector size (0x800)

# === Load replacement file ===
zar_data = open(REPLACEMENT_FILE, "rb").read()
zar_size = len(zar_data)
zar_padded_size = (zar_size + SECTOR_SIZE - 1) & ~(SECTOR_SIZE - 1)

# === Write the patched ISO ===
with open(ORIGINAL_ISO, "rb") as f_in, open(NEW_ISO, "wb") as f_out:
    # Copy up to _zar
    f_out.write(f_in.read(REPLACE_OFFSET))

    # Write new _zar with padding
    f_out.write(zar_data)
    f_out.write(b'\x00' * (zar_padded_size - zar_size))

    # Skip original _zar and continue copying the rest
    f_in.seek(REPLACE_OFFSET + zar_padded_size)
    f_out.write(f_in.read())

# === Patch size values ===
with open(NEW_ISO, "r+b") as f:
    # Write little-endian size
    f.seek(SIZE_LE_OFFSET)
    f.write(zar_size.to_bytes(4, "little"))

    # Write big-endian size
    f.seek(SIZE_BE_OFFSET)
    f.write(zar_size.to_bytes(4, "big"))

print(f"✔ ISO patched successfully!")
print(f"🔁 Replaced _zar at offset 0x{REPLACE_OFFSET:X}")
print(f"📏 _zar size: {zar_size} bytes (padded to {zar_padded_size})")
print(f"✍️  Size (LE) updated at 0x{SIZE_LE_OFFSET:X}")
print(f"✍️  Size (BE) updated at 0x{SIZE_BE_OFFSET:X}")
