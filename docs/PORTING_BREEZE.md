# Redmi 13 5G (`breeze`) port status

The current implementation is **not compatible** with `breeze`. It is a
bring-up for Redmi Note 10 Pro (`sweet`, SM7150), and its generated Apple
Device Tree contains board-specific memory, interrupt-controller, timer,
framebuffer and UFS addresses. The kernel also contains drivers for the
`sweet` PMIC buttons and Goodix touchscreen. Changing only the device name or
SoC string would not make a bootable port.

## Known facts

- Redmi 13 5G codename: `breeze`.
- SoC: Snapdragon 4 Gen 2 AE (Qualcomm SM4450 family); 2 Cortex-A78 plus 6
  Cortex-A55 CPU cores.
- Xiaomi publishes a `breeze-u-oss` kernel source branch for Redmi Note 13R,
  a sibling product. It is a useful starting point, but its board DTS must be
  checked against the Redmi 13 5G hardware and firmware before reuse.
- This repository's `tools/mkadt.py`, `shim/` boot path, and XNU platform and
  peripheral drivers are currently specific to `sweet`.

## Files inspected (2026-10-22)

The provided Global India OS3.0.9.0.WNUINXM firmware set includes `boot.img`,
`vendor_boot.img`, `dtbo.img`, `vbmeta.img`, and `super.img`. The separate
`Resources/DTBs/breeze.dtb` is byte-for-byte identical to a Parrot entry in
`vendor_boot.img` (SHA-256
`7f44ef8173f936ef060cb72b6c4ecded8bf6e2cebad601e6f1f338d982b0e203`), but
that is not the tree selected on the connected Redmi 13 5G.

That external DTB identifies `Qualcomm Technologies, Inc. Parrot SoC`,
compatible `qcom,parrot`, with MSM IDs `0x219` and `0x265`, board ID `0,0`,
and eight CPU nodes with MPIDRs `0x0` through `0x700`. Its top-level Linux
`memory/reg` is zeroed, so this DTB alone does not establish the RAM map used
at boot. Vendor boot contains 14 concatenated DTBs for several SoC variants;
the supplied file matches the Parrot `board-id 0,0` entry. The connected
phone reports boot DTB index 11, which is Ravelin; it also reports DTBO index
32. Use that Ravelin selection for BREEZE.

The DTBO image has 34 overlay entries, including Parrot ATP, IDP and QRD
families. Their configuration includes multiple panel choices and touch
controllers (including FocalTech, Novatek and Goodix variants). The exact
overlay selected on the physical phone is still unknown; do not pick one by
guessing. The images are Android boot header version 4 (`boot.img` and
`vendor_boot.img`) and a DTBO table. `vendor_boot.img` and `vbmeta.img` are
present in the same firmware folder, even though they were not in the initial
file list.

### Live FDT supplied separately

The user supplied `C:\Users\Administrator\Downloads\platform-tools\fdt`
and confirmed the phone's bootloader is unlocked. ADB identifies the connected
phone as model `2406ERN9CI`, product `breeze_in`, SoC `SM4450`, on vendor build
`OS3.0.9.0.WNUINXM`. `ro.boot.dtb_idx=11` and `ro.boot.dtbo_idx=32` select
factory DTB 11 and DTBO 32. DTB 11 is the Ravelin SoC tree; the supplied live
tree identifies as `Qualcomm Technologies, Inc. Ravelin QRD`, so this is
consistent with the phone. The live file is a valid 546,261-byte FDT, SHA-256
`97b6ee36c32f5f58b01c4ef0d9380dd5f02d40921f7d045b0da649b05ac1e396`. The
factory vendor_boot also contains Parrot and Montague alternatives for other
variants; those are not the selected board. ADB cannot read back the live FDT
directly from sysfs without root, so keep the supplied dump as the live-tree
evidence and validate important properties against DTB/DTBO indices 11/32.

The selected Ravelin tree gives a GICv3 distributor at `0x17200000`,
redistributors at `0x17260000`, and a 19.2 MHz architected timer with virtual
timer PPI 11. The UFS controller is listed at `0x01d84000`; the merged live
tree has it enabled. The firmware exposes CPU nodes for eight
MPIDRs (`0x0` through `0x700`); the product CPU mix is six Cortex-A55 and two
Cortex-A78 cores.

The `BREEZE` ADT profile uses the live Ravelin GIC, timer, UFS, splash
framebuffer and CPU topology, plus a conservative 263 MiB XNU memory bank
from the selected tree. The timer binding's virtual PPI index 11 maps to GIC
INTID 27. `shim/build.sh` selects Breeze hardware constants with
`BREEZE_BOARD=1` and requires `SHIM_DTB` to point at the selected Ravelin
FDT. SWEET defaults remain unchanged. This is first-stage bring-up scaffolding;
panel driving, board power management, touchscreen and full userland/storage
validation remain to be implemented.

Generate the ADT with `python3 tools/mkadt.py shim/out/breeze.adt --breeze`.
Build the shim with `BREEZE_BOARD=1 SHIM_DTB=/path/to/live-ravelin-fdt
shim/build.sh`. Build XNU with `MACHINE_CONFIG=BREEZE`.

## Required before device bring-up

The factory images and selected-tree evidence are available. Keep extracted
device dumps outside git. Remaining work:

1. Build XNU with `MACHINE_CONFIG=BREEZE` and validate the kernel boot path.
2. Verify splash framebuffer stride/format and active panel mode before
   enabling XNU display output.
3. Implement platform power management, touchscreen, PMIC/buttons, regulators
   and remaining peripheral drivers.
4. Validate UFS DMA and storage through read-only temporary boots before using
   any writable root volume. Keep all SWEET behavior selectable and unchanged.

## Reference sources

- Xiaomi kernel source index: <https://github.com/MiCode/Xiaomi_Kernel_OpenSource>
  (`breeze-u-oss`, Redmi Note 13R).
- Xiaomi Redmi 13 5G specifications:
  <https://www.mi.com/in/product/redmi-13-5g/specs/>

This document is a porting assessment, not a claim that `breeze` boots this
project. No bootable image can be built responsibly until the board data above
is available and the XNU/shim drivers are adapted and validated.
