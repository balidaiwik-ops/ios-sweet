#!/usr/bin/env python3
"""Extract concatenated FDT blobs from an Android vendor_boot v4 image.

Usage: extract-vendor-dtbs.py vendor_boot.img OUT_DIR

Outputs only DTBs and a small text index. Keep device dumps outside git.
"""
import os
import re
import struct
import sys

FDT_MAGIC = b"\xd0\x0d\xfe\xed"
VENDOR_BOOT_MAGIC = b"VNDRBOOT"
PAGE_SIZE_OFF = 12
VENDOR_RAMDISK_SIZE_OFF = 24
HEADER_SIZE_OFF = 2096
DTB_SIZE_OFF = 2100


def align(value, boundary):
    return (value + boundary - 1) // boundary * boundary


def fdt_strings(blob):
    """Return a few root identity properties from a flattened device tree."""
    if len(blob) < 40 or blob[:4] != FDT_MAGIC:
        raise ValueError("not an FDT blob")
    (magic, total, struct_off, strings_off, _rsv_off, version, _last,
     _bootcpu, strings_size, struct_size) = struct.unpack_from(">10I", blob)
    if magic != 0xD00DFEED or total > len(blob) or struct_off + struct_size > total:
        raise ValueError("invalid FDT header")
    strings = blob[strings_off:strings_off + strings_size]
    p = struct_off
    depth = 0
    props = {}
    while p + 4 <= struct_off + struct_size:
        token, = struct.unpack_from(">I", blob, p)
        p += 4
        if token == 1:  # FDT_BEGIN_NODE
            end = blob.find(b"\0", p, total)
            if end < 0:
                raise ValueError("unterminated FDT node name")
            depth += 1
            p = align(end + 1, 4)
        elif token == 2:  # FDT_END_NODE
            depth -= 1
        elif token == 3:  # FDT_PROP
            if p + 8 > total:
                raise ValueError("truncated FDT property")
            length, name_off = struct.unpack_from(">II", blob, p)
            p += 8
            end = p + length
            if end > total or name_off >= len(strings):
                raise ValueError("invalid FDT property bounds")
            name_end = strings.find(b"\0", name_off)
            if name_end < 0:
                raise ValueError("invalid FDT property name")
            name = strings[name_off:name_end].decode("ascii", "replace")
            if depth == 1 and name in ("model", "compatible", "qcom,msm-id", "qcom,board-id"):
                value = blob[p:end]
                if name in ("model", "compatible"):
                    props[name] = "|".join(x.decode("ascii", "replace") for x in value.rstrip(b"\0").split(b"\0"))
                elif len(value) % 4 == 0:
                    props[name] = " ".join(f"0x{x:x}" for x in struct.unpack(f">{len(value) // 4}I", value))
            p = align(end, 4)
        elif token == 4:  # FDT_NOP
            continue
        elif token == 9:  # FDT_END
            return total, props
        else:
            raise ValueError(f"unknown FDT token {token} at {p - 4:#x}")
    raise ValueError("FDT has no FDT_END token")


def safe_name(value):
    return re.sub(r"[^A-Za-z0-9_.-]+", "_", value).strip("_.-") or "unknown"


def main(argv):
    if len(argv) != 3:
        raise SystemExit(__doc__.strip())
    image_path, out_dir = argv[1:]
    with open(image_path, "rb") as f:
        image = f.read()
    if image[:8] != VENDOR_BOOT_MAGIC:
        raise SystemExit(f"{image_path}: not an Android vendor_boot image")
    version, = struct.unpack_from("<I", image, 8)
    page_size, = struct.unpack_from("<I", image, PAGE_SIZE_OFF)
    ramdisk_size, = struct.unpack_from("<I", image, VENDOR_RAMDISK_SIZE_OFF)
    if version < 3 or page_size == 0:
        raise SystemExit(f"unsupported vendor_boot header version {version}")
    header_size, = struct.unpack_from("<I", image, HEADER_SIZE_OFF)
    dtb_size, = struct.unpack_from("<I", image, DTB_SIZE_OFF)
    if version >= 4 and header_size < 2128:
        raise SystemExit(f"invalid vendor_boot v4 header size {header_size}")
    start = page_size + align(ramdisk_size, page_size)
    end = start + dtb_size
    if end > len(image):
        raise SystemExit(f"DTB section [{start:#x}, {end:#x}) exceeds image size")

    os.makedirs(out_dir, exist_ok=True)
    index_path = os.path.join(out_dir, "index.txt")
    records = []
    pos = start
    while pos < end:
        found = image.find(FDT_MAGIC, pos, end)
        if found < 0:
            break
        try:
            total, props = fdt_strings(image[found:end])
        except ValueError:
            pos = found + 4
            continue
        if total == 0 or found + total > end:
            pos = found + 4
            continue
        identity = safe_name(props.get("compatible", "unknown").split("|")[0])
        model = safe_name(props.get("model", "board"))
        name = f"{len(records):02d}-{identity}-{model}.dtb"
        with open(os.path.join(out_dir, name), "wb") as f:
            f.write(image[found:found + total])
        records.append((name, found, total, props))
        pos = found + total

    if not records:
        raise SystemExit("no valid FDT blobs found in vendor_boot DTB section")
    with open(index_path, "w", encoding="utf-8", newline="\n") as f:
        f.write(f"vendor_boot version={version} page_size={page_size} dtb_section={start:#x}+{dtb_size:#x}\n")
        for name, offset, total, props in records:
            f.write(f"{name}\toffset={offset:#x}\tsize={total}\tmodel={props.get('model', '')}\tcompatible={props.get('compatible', '')}\tmsm-id={props.get('qcom,msm-id', '')}\tboard-id={props.get('qcom,board-id', '')}\n")
    print(f"extracted {len(records)} DTBs to {out_dir}; index: {index_path}")


if __name__ == "__main__":
    main(sys.argv)
