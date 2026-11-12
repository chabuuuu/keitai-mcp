# The Definitive Android Development Guide for Japanese Keitai (Fujitsu F-03L)

This guide documents the technical architecture, UX paradigms, and implementation patterns required to develop and optimize Android applications for Japanese flip phones ("ガラケー" / Garakei / Keitai), specifically the **Fujitsu arrows ケータイ F-03L** (NTT DOCOMO).

---

## 1. Understanding the Platform

The Fujitsu F-03L runs an Android-based firmware tailored for feature phone usage:
- **Operating System**: Android 8.1.0 Oreo (API Level 27)
- **Form Factor**: Clamshell flip phone with physical hinge button (One-Push Open)
- **Processor**: Qualcomm Snapdragon 210 MSM8909 (Quad-Core ARM Cortex-A7 @ 1.1 GHz)
- **Architecture**: 32-bit ARM (`armeabi-v7a`)
- **System RAM**: 1 GB LPDDR3 (~913 MB visible to kernel, ~250–350 MB free)
- **Main Display**: 3.4-inch TFT LCD, 480 × 854 pixels (FWVGA), 240 dpi (hdpi)
- **Sub-Display**: 0.8-inch monochrome OLED (96 × 32 pixels) on the outer lid
- **Primary Input**: Physical 5-way D-Pad, Numeric 0–9 keypad, *, #, and Softkeys (`F1`, `F2`, `CLR`, `CALL`, `ENDCALL`)

---

## 2. The Non-Touch Focus Model

On smartphones, users tap anywhere directly. On the F-03L, **there is no physical touchscreen during normal usage**. Navigation relies entirely on shifting focus between interactive UI elements via the D-Pad.

### 2.1 Focusable Elements
Every interactive element must explicitly declare:
```xml
android:focusable="true"
android:clickable="true"
```

If an element has `clickable="true"` but lacks `focusable="true"`, the user **cannot navigate to it** using the D-Pad.

### 2.2 Visual Focus Highlight (Mandatory)
When an element receives focus, it **must** visually indicate its state with a high-contrast border or background change.

Create a state-list drawable in `res/drawable/keitai_item_selector.xml`:
```xml
<?xml version="1.0" encoding="utf-8"?>
<selector xmlns:android="http://schemas.android.com/apk/res/android">
    <!-- Focused state: highlighted when user moves D-Pad over it -->
    <item android:state_focused="true">
        <shape android:shape="rectangle">
            <solid android:color="#1A73E8" />
            <stroke android:width="3dp" android:color="#FFD700" />
            <corners android:radius="4dp" />
        </shape>
    </item>

    <!-- Pressed state: when D-Pad Center (OK) is held down -->
    <item android:state_pressed="true">
        <shape android:shape="rectangle">
            <solid android:color="#1557B0" />
            <stroke android:width="3dp" android:color="#FFFFFF" />
            <corners android:radius="4dp" />
        </shape>
    </item>

    <!-- Normal default state -->
    <item>
        <shape android:shape="rectangle">
            <solid android:color="#F1F3F4" />
            <stroke android:width="1dp" android:color="#DADCE0" />
            <corners android:radius="4dp" />
        </shape>
    </item>
</selector>
```

Apply this selector to buttons, cards, list items, and text fields:
```xml
<TextView
    android:id="@+id/menu_item_wifi"
    android:layout_width="match_parent"
    android:layout_height="56dp"
    android:gravity="center_vertical"
    android:paddingStart="16dp"
    android:paddingEnd="16dp"
    android:text="Wi-Fi Settings"
    android:textColor="@color/keitai_text_selector"
    android:background="@drawable/keitai_item_selector"
    android:focusable="true"
    android:clickable="true" />
```

### 2.3 Setting Initial Focus
When an Activity starts, Android may leave focus unset until the user presses a D-Pad key. Always assign initial focus programmatically:
```kotlin
override fun onResume() {
    super.onResume()
    binding.primaryActionBtn.requestFocus()
}
```

### 2.4 Explicit Navigation Chains
When views are in non-linear or multi-column layouts, specify explicit focus navigation order:
```xml
<Button
    android:id="@+id/btn_left"
    android:nextFocusRight="@id/btn_right"
    android:nextFocusDown="@id/btn_bottom"
    ... />
```

---

## 3. Hardware Key Interception

The Fujitsu F-03L generates distinct Android KeyEvents for physical keys:

| Key Name | Android KeyCode Constant | Keycode Int | Purpose |
|---|---|---|---|
| D-Pad Center | `KeyEvent.KEYCODE_DPAD_CENTER` | 23 | Confirm / Select / Activate |
| CLR / Back | `KeyEvent.KEYCODE_BACK` | 4 | Delete text char / Go back |
| Call (Green) | `KeyEvent.KEYCODE_CALL` | 5 | Primary dial / Call action |
| End (Red) | `KeyEvent.KEYCODE_ENDCALL` | 6 | Terminate call / Return home |
| Left Softkey | `KeyEvent.KEYCODE_F1` | 131 | Submenu / Mail / Quick actions |
| Right Softkey| `KeyEvent.KEYCODE_F2` | 132 | Options / Browser / Tools |
| Numeric 0–9  | `KeyEvent.KEYCODE_0`..`KEYCODE_9` | 7–16 | Direct number shortcuts |
| Star (*)     | `KeyEvent.KEYCODE_STAR` | 17 | Symbol / Page Up |
| Pound (#)    | `KeyEvent.KEYCODE_POUND` | 18 | Manner mode / Page Down |

### Kotlin Implementation Example
```kotlin
package com.example.keitai

import android.os.Bundle
import android.view.KeyEvent
import android.widget.Toast
import androidx.appcompat.app.AppCompatActivity

class KeitaiMainActivity : AppCompatActivity() {

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)
    }

    override fun onKeyDown(keyCode: Int, event: KeyEvent?): Boolean {
        when (keyCode) {
            KeyEvent.KEYCODE_DPAD_CENTER, KeyEvent.KEYCODE_ENTER -> {
                // User pressed OK on keypad
                val currentFocusView = currentFocus
                currentFocusView?.performClick()
                return true
            }
            KeyEvent.KEYCODE_F1 -> {
                // Left softkey: open submenu
                openSubmenu()
                return true
            }
            KeyEvent.KEYCODE_F2 -> {
                // Right softkey: open options
                openOptionsMenu()
                return true
            }
            KeyEvent.KEYCODE_1 -> {
                // Quick shortcut: jump to section 1
                selectTab(0)
                return true
            }
            KeyEvent.KEYCODE_2 -> {
                selectTab(1)
                return true
            }
        }
        return super.onKeyDown(keyCode, event)
    }

    private fun openSubmenu() {
        Toast.makeText(this, "Submenu opened", Toast.LENGTH_SHORT).show()
    }

    private fun selectTab(index: Int) {
        Toast.makeText(this, "Selected Tab $index", Toast.LENGTH_SHORT).show()
    }
}
```

---

## 4. Screen Geometry & Typography (480 × 854 @ 240 dpi)

1. **Resolution Constraints**:
   - Canvas width: **480 px** (320 dp).
   - Canvas height: **854 px** (~569 dp).
   - System status bar uses ~96 px (~64 dp), leaving **480 × 758 px** for your application.
2. **Typography**:
   - Japanese characters require legible sizing:
     - Titles: `18sp` to `20sp` bold.
     - Body text: `14sp` to `16sp`.
     - Small annotations: minimum `12sp`.
3. **RecyclerView D-Pad Scrolling**:
   - Set `android:descendantFocusability="afterDescendants"` on your RecyclerView layout to ensure smooth item-to-item focus traversal.

---

## 5. Build Configuration (`build.gradle.kts`)

Target Android 8.1 (API 27) and restrict native code to 32-bit ARM:

```kotlin
android {
    compileSdk = 27

    defaultConfig {
        applicationId = "com.example.keitai.app"
        minSdk = 26
        targetSdk = 27
        versionCode = 1
        versionName = "1.0.0"

        // Fujitsu F-03L is 32-bit ARM Cortex-A7
        ndk {
            abiFilters.addAll(listOf("armeabi-v7a"))
        }
    }

    buildTypes {
        release {
            isMinifyEnabled = true
            isShrinkResources = true
            proguardFiles(getDefaultProguardFile("proguard-android-optimize.txt"), "proguard-rules.pro")
        }
    }
}
```

### Memory Considerations (1 GB RAM)
- Avoid loading full-resolution images into memory. Always decode with `BitmapFactory.Options.inSampleSize` to downscale bitmaps to 480 px width max.
- Do not run continuous background foreground services. Android 8.1 imposes strict background execution limits; use `JobScheduler` or `WorkManager`.

---

## 6. Testing & Automating with Keitai MCP

Using **Keitai MCP**, you or your AI agent can verify your app on the real Fujitsu F-03L:

```bash
# Sideload your built APK
keitai-mcp run (via agent) OR:
adb install -r -g app-release.apk

# Launch the app
adb shell monkey -p com.example.keitai.app 1

# Check which element received initial focus
keitai-mcp ui --focused-only

# Verify navigation: press DOWN, check if focus moved to next element
keitai-mcp key DOWN
keitai-mcp ui --focused-only

# Capture screenshot for visual inspection
keitai-mcp screenshot -o app_screen.png
```
