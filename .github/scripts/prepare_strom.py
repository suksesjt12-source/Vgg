
from pathlib import Path
import sys

if len(sys.argv) != 2:
    raise SystemExit("Usage: prepare_strom.py upstream")

ROOT = Path(sys.argv[1]).resolve()
APP = ROOT / "app" / "app" / "src" / "main"
JAVA = APP / "java" / "com" / "winlator"

def replace_once(path, old, new):
    if not path.exists():
        raise SystemExit(f"Missing file: {path}")

    content = path.read_text(encoding="utf-8")

    if old not in content:
        raise SystemExit(f"Patch anchor not found: {path}")

    path.write_text(content.replace(old, new, 1), encoding="utf-8")


# App branding
replace_once(
    APP / "res/values/strings.xml",
    '<string name="app_name">Winlator</string>',
    '<string name="app_name">Strom Launcher</string>'
)


# Strom settings panel
strom_java = r'''package com.winlator;

import android.content.Context;
import android.content.SharedPreferences;
import android.graphics.Color;
import android.view.View;
import android.view.ViewGroup;
import android.widget.ArrayAdapter;
import android.widget.LinearLayout;
import android.widget.ScrollView;
import android.widget.Spinner;
import android.widget.Switch;
import android.widget.TextView;

import androidx.appcompat.widget.AppCompatSpinner;

public final class StromSettingsPanel {
    private final Context context;
    private final SharedPreferences preferences;

    private Spinner profile;
    private Spinner resolution;
    private Switch vsync;
    private Switch dxvkAsync;

    public StromSettingsPanel(
            Context context,
            SharedPreferences preferences) {
        this.context = context;
        this.preferences = preferences;
    }

    private int dp(float value) {
        return (int) (value *
            context.getResources().getDisplayMetrics().density);
    }

    private TextView label(String value) {
        TextView text = new TextView(context);
        text.setText(value);
        text.setTextColor(Color.WHITE);
        text.setTextSize(14);
        text.setPadding(0, dp(10), 0, dp(5));
        return text;
    }

    private Spinner makeSpinner(String[] values, String selected) {
        AppCompatSpinner spinner = new AppCompatSpinner(context);

        ArrayAdapter<String> adapter = new ArrayAdapter<>(
            context,
            android.R.layout.simple_spinner_item,
            values
        );

        adapter.setDropDownViewResource(
            android.R.layout.simple_spinner_dropdown_item
        );

        spinner.setAdapter(adapter);

        for (int i = 0; i < values.length; i++) {
            if (values[i].equals(selected)) {
                spinner.setSelection(i);
                break;
            }
        }

        return spinner;
    }

    private Switch makeSwitch(String title, boolean checked) {
        Switch control = new Switch(context);
        control.setText(title);
        control.setTextColor(Color.WHITE);
        control.setTextSize(14);
        control.setChecked(checked);
        control.setPadding(0, dp(8), 0, dp(8));
        return control;
    }

    public void attach(View root) {
        ScrollView scroll = findScrollView(root);
        if (scroll == null || !(scroll.getChildAt(0) instanceof LinearLayout)) {
            return;
        }

        LinearLayout content = (LinearLayout) scroll.getChildAt(0);

        LinearLayout panel = new LinearLayout(context);
        panel.setOrientation(LinearLayout.VERTICAL);
        panel.setPadding(dp(16), dp(14), dp(16), dp(14));
        panel.setBackgroundColor(Color.rgb(27, 39, 59));

        TextView heading = label("STROM CUSTOM SETTINGS");
        heading.setTextColor(Color.rgb(100, 181, 246));
        heading.setTextSize(18);
        heading.setPadding(0, 0, 0, dp(8));
        panel.addView(heading);

        TextView description = label(
            "Custom configuration preferences"
        );
        description.setTextColor(Color.LTGRAY);
        panel.addView(description);

        panel.addView(label("Performance profile"));

        profile = makeSpinner(
            new String[]{"Cool", "Balanced", "Performance"},
            preferences.getString("strom_profile", "Balanced")
        );
        panel.addView(profile);

        panel.addView(label("Default game resolution"));

        resolution = makeSpinner(
            new String[]{
                "960x540",
                "1024x576",
                "1280x720",
                "1600x900"
            },
            preferences.getString("strom_resolution", "960x540")
        );
        panel.addView(resolution);

        vsync = makeSwitch(
            "VSync preference",
            preferences.getBoolean("strom_vsync", false)
        );
        panel.addView(vsync);

        dxvkAsync = makeSwitch(
            "DXVK Async preference",
            preferences.getBoolean("strom_dxvk_async", true)
        );
        panel.addView(dxvkAsync);

        View separator = new View(context);
        separator.setBackgroundColor(Color.rgb(75, 91, 112));

        LinearLayout.LayoutParams separatorParams =
            new LinearLayout.LayoutParams(
                ViewGroup.LayoutParams.MATCH_PARENT,
                dp(1)
            );

        separatorParams.topMargin = dp(12);
        panel.addView(separator, separatorParams);

        TextView note = label(
            "These are saved Strom preferences. " +
            "They do not yet automatically change active containers."
        );
        note.setTextColor(Color.LTGRAY);
        note.setTextSize(12);
        panel.addView(note);

        View confirm = root.findViewById(R.id.BTConfirm);
        int index = confirm == null ? -1 : content.indexOfChild(confirm);

        if (index >= 0) {
            content.addView(panel, index);
        } else {
            content.addView(panel);
        }

        LinearLayout.LayoutParams params =
            (LinearLayout.LayoutParams) panel.getLayoutParams();

        params.bottomMargin = dp(16);
        panel.setLayoutParams(params);
    }

    private ScrollView findScrollView(View root) {
        if (root instanceof ScrollView) {
            return (ScrollView) root;
        }

        if (root instanceof ViewGroup) {
            ViewGroup group = (ViewGroup) root;

            for (int i = 0; i < group.getChildCount(); i++) {
                ScrollView result =
                    findScrollView(group.getChildAt(i));

                if (result != null) return result;
            }
        }

        return null;
    }

    public void save(SharedPreferences.Editor editor) {
        if (profile == null || resolution == null ||
            vsync == null || dxvkAsync == null) {
            return;
        }

        editor.putString(
            "strom_profile",
            profile.getSelectedItem().toString()
        );

        editor.putString(
            "strom_resolution",
            resolution.getSelectedItem().toString()
        );

        editor.putBoolean("strom_vsync", vsync.isChecked());
        editor.putBoolean("strom_dxvk_async", dxvkAsync.isChecked());
    }
}
'''

(JAVA / "StromSettingsPanel.java").write_text(
    strom_java,
    encoding="utf-8"
)


# Connect panel to existing settings screen
settings_file = JAVA / "SettingsFragment.java"

replace_once(
    settings_file,
    'preferences = PreferenceManager.getDefaultSharedPreferences(context);',
    '''preferences = PreferenceManager.getDefaultSharedPreferences(context);

        StromSettingsPanel stromSettings =
            new StromSettingsPanel(context, preferences);

        stromSettings.attach(view);'''
)

replace_once(
    settings_file,
    'if (editor.commit()) {',
    '''stromSettings.save(editor);

            if (editor.commit()) {'''
)

print("Strom custom settings panel installed.")
