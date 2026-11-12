
from pathlib import Path
import sys

if len(sys.argv) != 2:
    raise SystemExit("Usage: prepare_strom.py upstream")

ROOT = Path(sys.argv[1]).resolve()
APP = ROOT / "app" / "app" / "src" / "main"

def replace_once(path, old, new):
    if not path.exists():
        raise SystemExit(f"Missing file: {path}")

    content = path.read_text(encoding="utf-8")

    if old not in content:
        raise SystemExit(f"Expected text not found in {path}")

    path.write_text(
        content.replace(old, new, 1),
        encoding="utf-8"
    )

# Strom branding
replace_once(
    APP / "res/values/strings.xml",
    '<string name="app_name">Winlator</string>',
    '<string name="app_name">Strom Launcher</string>'
)

# Custom Strom dashboard header
layout = APP / "res/layout/main_activity.xml"

content = layout.read_text(encoding="utf-8")

toolbar = """        <androidx.appcompat.widget.Toolbar
            android:layout_width="match_parent"
            android:layout_height="?actionBarSize"
            android:id="@+id/Toolbar"
            app:layout_scrollFlags="enterAlways|scroll"
            app:title="@string/app_name" />"""

header = toolbar + """
        <com.google.android.material.card.MaterialCardView
            android:layout_width="match_parent"
            android:layout_height="wrap_content"
            android:layout_marginStart="14dp"
            android:layout_marginEnd="14dp"
            android:layout_marginTop="8dp"
            android:layout_marginBottom="8dp"
            app:cardCornerRadius="16dp"
            app:cardElevation="3dp"
            app:cardBackgroundColor="#18233A">

            <LinearLayout
                android:layout_width="match_parent"
                android:layout_height="wrap_content"
                android:orientation="vertical"
                android:padding="16dp">

                <TextView
                    android:layout_width="wrap_content"
                    android:layout_height="wrap_content"
                    android:text="STROM"
                    android:textColor="#64B5F6"
                    android:textSize="22sp"
                    android:textStyle="bold"
                    android:letterSpacing="0.12" />

                <TextView
                    android:layout_width="wrap_content"
                    android:layout_height="wrap_content"
                    android:layout_marginTop="3dp"
                    android:text="WINDOWS GAMING ENVIRONMENT"
                    android:textColor="#FFFFFF"
                    android:textSize="11sp"
                    android:letterSpacing="0.08" />

                <TextView
                    android:layout_width="wrap_content"
                    android:layout_height="wrap_content"
                    android:layout_marginTop="8dp"
                    android:text="Manage containers • Configure runtime • Launch games"
                    android:textColor="#B8C7DC"
                    android:textSize="12sp" />
            </LinearLayout>
        </com.google.android.material.card.MaterialCardView>"""

if content.count(toolbar) != 1:
    raise SystemExit("Unexpected main_activity.xml structure")

layout.write_text(
    content.replace(toolbar, header, 1),
    encoding="utf-8"
)

print("Strom branding and custom interface applied.")
