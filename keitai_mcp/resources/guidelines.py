"""Guidelines and Best Practices for Developing Android Apps on Keitai (Fujitsu F-03L)."""

KEITAI_GUIDELINES_TEXT = """# Android Development Guidelines for Japanese Keitai (Fujitsu F-03L)

Developing software for Japanese feature phones ("ガラケー" / Garakei / Keitai) running Android requires a fundamentally different UX mindset compared to modern touch smartphones. Below are the architectural patterns, focus management rules, and keycode behaviors essential for building rock-solid applications on the Fujitsu F-03L.

---

## 1. Focus Management (The Core of Keitai UX)

Since the Fujitsu F-03L does not feature a physical touch screen, users navigate exclusively using the 5-way D-Pad (Up, Down, Left, Right, Center/OK).

### Rule 1.1: Every interactive element MUST be focusable
```xml
<!-- In XML layout -->
<Button
    android:id="@+id/btn_action"
    android:layout_width="match_parent"
    android:layout_height="wrap_content"
    android:focusable="true"
    android:clickable="true"
    android:background="@drawable/keitai_button_selector"
    android:text="Select" />
```

### Rule 1.2: Always provide a distinct visual focus state
Users must never guess where the cursor is. Create a state-list drawable for buttons and list items:
```xml
<!-- res/drawable/keitai_button_selector.xml -->
<selector xmlns:android="http://schemas.android.com/apk/res/android">
    <!-- Focused state (D-pad highlighting) -->
    <item android:state_focused="true">
        <shape android:shape="rectangle">
            <solid android:color="#0055AA" />
            <stroke android:width="3dp" android:color="#FFD700" />
            <corners android:radius="4dp" />
        </shape>
    </item>
    <!-- Default state -->
    <item>
        <shape android:shape="rectangle">
            <solid android:color="#EEEEEE" />
            <stroke android:width="1dp" android:color="#CCCCCC" />
            <corners android:radius="4dp" />
        </shape>
    </item>
</selector>
```

### Rule 1.3: Define explicit navigation chains when ambiguous
When layouts have grids or complex columns, Android's automatic focus direction algorithm may jump unpredictably. Define explicit focus targets:
```xml
<Button
    android:id="@+id/btn_item1"
    android:nextFocusDown="@id/btn_item2"
    android:nextFocusRight="@id/btn_side_menu"
    ... />
```

### Rule 1.4: Set initial focus in Activity or Fragment
```kotlin
override fun onResume() {
    super.onResume()
    // Explicitly request focus on primary interactive view
    binding.firstInput.requestFocus()
}
```

---

## 2. Hardware Key Interception

On the Fujitsu F-03L, standard hardware keys trigger specific Android KeyEvents:

| Physical Key | Android Keycode Constant | Keycode Int | Common Keitai Usage |
|---|---|---|---|
| D-Pad Center | `KeyEvent.KEYCODE_DPAD_CENTER` | 23 | Confirm, Click, Select |
| Clear / Back | `KeyEvent.KEYCODE_BACK` / `KEYCODE_CLEAR` | 4 | Delete char in text, go back |
| Call (Green) | `KeyEvent.KEYCODE_CALL` | 5 | Start call, primary action |
| End Call (Red)| `KeyEvent.KEYCODE_ENDCALL` | 6 | Terminate activity / Exit |
| Left Softkey | `KeyEvent.KEYCODE_F1` | 131 | Submenu 1, Email, Action menu |
| Right Softkey| `KeyEvent.KEYCODE_F2` | 132 | Submenu 2, Browser, Options |
| Numeric 0-9  | `KeyEvent.KEYCODE_0`..`KEYCODE_9` | 7 - 16 | Direct item selection, T9 |
| Star (*)     | `KeyEvent.KEYCODE_STAR` | 17 | Voice sound (濁点), Page up |
| Pound (#)    | `KeyEvent.KEYCODE_POUND` | 18 | Manner mode, Page down |
| Quick 1/2/3  | `KeyEvent.KEYCODE_BUTTON_1`..`3` | 188 - 190 | Favorite shortcuts |

### Handling Key Events in Activity:
```kotlin
override fun onKeyDown(keyCode: Int, event: KeyEvent?): Boolean {
    when (keyCode) {
        KeyEvent.KEYCODE_DPAD_CENTER, KeyEvent.KEYCODE_ENTER -> {
            handleConfirmAction()
            return true
        }
        KeyEvent.KEYCODE_F1 -> {
            openSubmenu()
            return true
        }
        KeyEvent.KEYCODE_F2 -> {
            openOptions()
            return true
        }
        KeyEvent.KEYCODE_1 -> {
            selectOptionIndex(0)
            return true
        }
    }
    return super.onKeyDown(keyCode, event)
}
```

---

## 3. Screen Layout & Typography (480 × 854 @ 240 dpi)

1. **Resolution Constraints**:
   - Total canvas: 480 px width × 854 px height.
   - Status bar occupies ~96 px, leaving ~480 × 758 px usable space.
   - Keep margins compact (8dp to 16dp).
2. **Scrolling**:
   - Keep views vertically oriented.
   - For `RecyclerView`, ensure the layout manager scrolls smoothly when focus changes:
   ```kotlin
   recyclerView.addOnScrollListener(object : RecyclerView.OnScrollListener() {
       // Smooth focus-driven scroll
   })
   ```
3. **Typography**:
   - The screen is physically small (3.4 inches).
   - Use minimum 14sp for body text, 18sp for titles.
   - Ensure high contrast (dark text on light background or vice versa).

---

## 4. Gradle & Build Architecture

1. **Target SDK & Architecture**:
   ```groovy
   android {
       compileSdkVersion 27 // Android 8.1 Oreo

       defaultConfig {
           applicationId "com.example.keitai"
           minSdkVersion 26
           targetSdkVersion 27
           versionCode 1
           versionName "1.0"

           // Fujitsu F-03L is 32-bit ARM Cortex-A7
           ndk {
               abiFilters "armeabi-v7a"
           }
       }
   }
   ```
2. **Memory Constraints (1 GB RAM)**:
   - Keep background memory footprint minimal.
   - Do NOT run heavy persistent foreground services.
   - Scale bitmaps to 480px width max before decoding to avoid `OutOfMemoryError`.
3. **No Google Play Services**:
   - Use standard Android APIs or FOSS libraries (OkHttp, Retrofit, Room, SQLite).
   - For push notifications, consider UnifiedPush or local polling.
"""

