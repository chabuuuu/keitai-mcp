"""Fujitsu arrows Keitai F-03L Technical Specifications Resource."""

F03L_SPECS_TEXT = """# Fujitsu arrows ケータイ F-03L - Technical Specifications

## Hardware Specifications
- **Model**: arrows ケータイ F-03L (arrows Keitai F-03L)
- **Manufacturer**: Fujitsu Connected Technologies Limited (FCNT)
- **Carrier**: NTT DOCOMO (Released Summer 2019)
- **Form Factor**: Clamshell / Flip Phone (ガラケー / Garakei) with One-Push Open hinge button
- **SoC**: Qualcomm Snapdragon 210 (MSM8909)
  - **CPU**: Quad-core ARM Cortex-A7 @ 1.1 GHz
  - **Architecture / ABI**: 32-bit ARM (`armeabi-v7a`)
  - **GPU**: Adreno 304
- **Memory (RAM)**: 1 GB LPDDR3 (~913 MB available to OS)
- **Internal Storage (ROM)**: 8 GB (~4.6 GB user partition, ~1.6 GB available)
- **External Storage**: microSDHC / microSDXC slot (up to 32 GB officially supported)
- **Battery**: 1,680 mAh removable Li-ion battery (CA54310-0071 / F34)

## Displays
- **Main Display**:
  - Size: 3.4 inches
  - Technology: TFT LCD (16.77M colors)
  - Resolution: 480 × 854 pixels (FWVGA, ~16:9 aspect ratio)
  - Density: 240 dpi (hdpi)
  - Touchscreen: Non-touch physical display (emulated touch available via ADB/MATVT)
- **Sub-Display (Outer Lid)**:
  - Size: 0.8 inches
  - Technology: Organic EL (OLED, monochrome)
  - Resolution: 96 × 32 pixels
  - Functionality: Displays digital clock, battery status, incoming call/mail alerts, pedometer step counter

## Keypad & Controls
- **Directional Pad (D-Pad)**: Up, Down, Left, Right, Center (決定 / OK)
- **Softkeys**:
  - Left Softkey (F1 / サブメニュー / メール): Keycode 131
  - Right Softkey (F2 / ブラウザ): Keycode 132
- **Standard Navigation**:
  - Clear / Back (CLR / 戻る): Keycode 4
  - Call / Start (発信 - Green): Keycode 5
  - End Call / Power (電源/終話 - Red): Keycode 6
- **Numeric Keypad**: 0 through 9, * (Asterisk / Dakuten), # (Pound / Manner mode)
- **Quick Launch (お気に入り)**: Keys 1, 2, 3 at the bottom of keypad (Keycodes 188, 189, 190)
- **Side Keys**: Volume Up (24), Volume Down (25), Manner Mode toggle

## Software & Operating System
- **OS**: Android 8.1.0 Oreo
- **API Level**: 27
- **Security Patch**: 2019-06-01
- **Google Mobile Services (GMS)**: Not included by default; uses Docomo Feature Phone services
- **Launcher**: NTT DOCOMO AFP Home (`com.nttdocomo.android.afphome`)
- **Input Method (IME)**: Super ATOK ULTIAS for Keitai (`com.fujitsu.mobile_phone.inputmethod.nx_input`) or TT9

## Connectivity & Durability
- **Cellular**: 4G LTE (VoLTE supported), 3G (W-CDMA)
- **Wi-Fi**: IEEE 802.11 b/g/n (2.4 GHz)
- **Bluetooth**: Version 4.2 (HFP, HSP, OPP, SPP, HID, A2DP, AVRCP, PBAP, PAN)
- **NFC / FeliCa**: Osaifu-Keitai (Mobile Suica / iD supported)
- **Infrared**: IrDA supported for address book transfer
- **Connector**: Micro-USB (USB 2.0 with USB Debugging ADB support)
- **Durability**: IPX5/IPX8 water resistance, IP6X dust resistance, MIL-STD-810G compliance (14 test items)
"""

