#pragma once

/* Hardware facts for the selected factory/live Redmi 13 5G tree. */
#ifdef BREEZE_BOARD
#define FB_BASE        0xb8000000UL
#define FB_SIZE        0x02b00000UL
#define FB_W           1080
#define FB_H           2460
#define GICD_BASE      0x17200000UL
#define GICR_BASE      0x17260000UL
#define VTIMER_INTID   27 /* DT PPI index 11 maps to GIC INTID 16 + 11 */
#define PTIMER_INTID   30 /* DT PPI index 14 maps to GIC INTID 16 + 14 */
#define UFS_BASE       0x01d84000UL
#define NR_CPUS        8
#else
#define FB_BASE        0x9c000000UL
#define FB_SIZE        0x01700000UL
#define FB_W           1080
#define FB_H           2400
#define GICD_BASE      0x17a00000UL
#define GICR_BASE      0x17a60000UL
#define VTIMER_INTID   19
#define PTIMER_INTID   18
#define UFS_BASE       0x01d84000UL
#define NR_CPUS        8
#endif

#define FB_STRIDE      (FB_W * 4)
