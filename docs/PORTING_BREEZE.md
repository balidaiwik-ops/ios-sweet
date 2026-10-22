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
`breeze.dtb` is byte-for-byte identical to one of the DTBs embedded in
`vendor_boot.img` (SHA-256
`7f44ef8173f936ef060cb72b6c4ecded8bf6e2cebad601e6f1f338d982b0e203`).

The matched DTB identifies `Qualcomm Technologies, Inc. Parrot SoC`,
compatible `qcom,parrot`, with MSM IDs `0x219` and `0x265`, board ID `0,0`,
and eight CPU nodes with MPIDRs `0x0` through `0x700`. Its top-level Linux
`memory/reg` is zeroed, so this DTB alone does not establish the RAM map used
at boot. Vendor boot contains 14 concatenated DTBs for several SoC variants;
the supplied file matches the Parrot `board-id 0,0` entry.

The DTBO image has 34 overlay entries, including Parrot ATP, IDP and QRD
families. Their configuration includes multiple panel choices and touch
controllers (including FocalTech, Novatek and Goodix variants). The exact
overlay selected on the physical phone is still unknown; do not pick one by
guessing. The images are Android boot header version 4 (`boot.img` and
`vendor_boot.img`) and a DTBO table. `vendor_boot.img` and `vbmeta.img` are
present in the same firmware folder, even though they were not in the initial
file list.

The base Parrot tree also gives a GICv3 distributor at `0x17200000`,
redistributors at `0x17260000`, and a 19.2 MHz architected timer with virtual
timer PPI 11. The UFS controller is listed at `0x01d84000` but is `disabled`
in that base tree; the bootloader's live state must establish whether the
controller is actually usable. The firmware exposes CPU nodes for eight
MPIDRs (`0x0` through `0x700`); the product CPU mix is six Cortex-A55 and two
Cortex-A78 cores.

The repository now has an experimental `BREEZE` XNU machine configuration
that shares the existing generic ARM/GICv3 bring-up definitions and uses PPI
11. The shim build also accepts `SHIM_DTB=/absolute/path/to/board.dtb`, and
`tools/extract-vendor-dtbs.py` extracts/indexes the DTBs from a vendor boot
image. This is kernel-build scaffolding only: the runtime RAM layout, selected
panel/touch overlay, framebuffer handoff, and board-specific platform expert
and drivers remain unimplemented. Do not boot a BREEZE image yet.

## Required before device bring-up

The matching factory images are now available. Keep all extracted/dumped
artifacts outside git. The main remaining device-side evidence is the live
DTB/selected-overlay result and bootloader handoff. At minimum, record:

1. Model/region and firmware build; bootloader unlock state.
2. The live DTB/DTBO selected by the bootloader. The factory `boot`,
   `vendor_boot`, `dtbo`, and `vbmeta` images are already available; preserve
   the originals for recovery.
3. Live memory map, reserved-memory carve-outs, CPU MPIDRs/topology, GIC
   distributor/redistributor, timer frequency/interrupt, and framebuffer
   physical address/format.
4. UFS controller/PHY state and bootloader handoff behavior.
5. Display panel, touch controller and bus, PMIC/button wiring, regulators,
   and any required power-domain setup.

Use those facts to create a separate `breeze` board profile and platform
expert, rather than changing `sweet` constants in place. First milestone is a
temporary boot that reaches an XNU debug console without writing partitions;
then add storage and display, and only later input and userland. Keep all
existing `sweet` behavior selectable and unchanged.

## Reference sources

- Xiaomi kernel source index: <https://github.com/MiCode/Xiaomi_Kernel_OpenSource>
  (`breeze-u-oss`, Redmi Note 13R).
- Xiaomi Redmi 13 5G specifications:
  <https://www.mi.com/in/product/redmi-13-5g/specs/>

This document is a porting assessment, not a claim that `breeze` boots this
project. No bootable image can be built responsibly until the board data above
is available and the XNU/shim drivers are adapted and validated.
