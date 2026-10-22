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

## Required before device bring-up

Obtain a matching stock firmware and a complete device dump from the exact
Redmi 13 5G variant. Keep all dumps outside git. At minimum, record:

1. Model/region and firmware build; bootloader unlock state.
2. `boot`, `vendor_boot`, `dtbo`, and `vbmeta` images, plus the live DTB/DTBO
   selected by the bootloader. Preserve the originals for recovery.
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
