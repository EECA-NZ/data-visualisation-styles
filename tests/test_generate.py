import json
import re
import unittest

from scripts.generate import (
    TOKENS_PATH,
    databricks_theme,
    generate,
    load_tokens,
    render_css,
    render_python,
    render_scss,
)


class TokenTests(unittest.TestCase):
    def setUp(self):
        self.tokens = load_tokens()

    def test_all_colors_are_six_digit_hex(self):
        colors = [
            value
            for group in self.tokens["colors"].values()
            for value in group.values()
        ]
        colors.extend(
            value
            for palette in self.tokens["palettes"].values()
            for value in palette
        )
        self.assertTrue(all(re.fullmatch(r"#[0-9A-F]{6}", value) for value in colors))

    def test_categorical_palette_matches_approved_order(self):
        self.assertEqual(
            self.tokens["palettes"]["categorical"],
            [
                "#0A3C61",
                "#2ADEA9",
                "#5A1A5E",
                "#F8CE7D",
                "#74DCDB",
                "#05422D",
                "#D2B7FE",
                "#3C6280",
                "#57E5BA",
                "#7B467E",
                "#376856",
            ],
        )

    def test_semantic_colors_reference_primitive_tokens(self):
        raw = json.loads(TOKENS_PATH.read_text())
        self.assertEqual(raw["colors"]["interface"]["page"], "{colors.neutral.silver}")
        self.assertEqual(
            raw["platforms"]["databricks"]["theme"]["selectionColor"]["light"],
            "{colors.interface.selection}",
        )

    def test_databricks_interface_settings_match_approved_values(self):
        theme = databricks_theme(self.tokens)
        self.assertEqual(theme["canvasBackgroundColor"], {"light": "#FBFBFB", "dark": "#1A2B25"})
        self.assertEqual(theme["widgetBackgroundColor"], {"light": "#FFFFFF", "dark": "#0F1F1A"})
        self.assertEqual(theme["widgetBorderColor"], {"light": "#E8ECEE", "dark": "#2A3D35"})
        self.assertEqual(theme["gridLineColor"], {"light": "#C0EBEB", "dark": "#3C3E42"})
        self.assertEqual(theme["axisLineColor"], {"light": "#9CA2B0", "dark": "#555E64"})
        self.assertEqual(theme["widgetCornerRadius"], 0)
        self.assertEqual(theme["widgetPadding"], 14)
        self.assertEqual(theme["widgetMargin"], 10)
        self.assertEqual(theme["widgetShadow"], 0)

    def test_dark_mode_tokens_are_available_to_all_consumers(self):
        self.assertIn("$eeca-dark-mode-canvas: #1A2B25;", render_scss(self.tokens))
        self.assertIn("--eeca-dark-mode-canvas: #1A2B25;", render_css(self.tokens))
        self.assertIn("'dark-mode-canvas': '#1A2B25'", render_python(self.tokens))

    def test_palettes_do_not_repeat_colors(self):
        for name, palette in self.tokens["palettes"].items():
            with self.subTest(palette=name):
                self.assertEqual(len(palette), len(set(palette)))

    def test_platform_fonts_use_supported_defaults(self):
        platforms = self.tokens["typography"]["platforms"]
        self.assertEqual(platforms["charts"][0], "Arial")
        self.assertEqual(platforms["databricks"], ["Inter"])

    def test_databricks_font_sizes_match_enquire_dashboard(self):
        theme = databricks_theme(self.tokens)
        sizes = {
            role: settings["fontSize"]
            for role, settings in theme["fontSettings"].items()
        }
        self.assertEqual(
            sizes,
            {
                "base": 14,
                "fieldTitle": 14,
                "fieldValue": 16,
                "widgetDescription": 14,
                "widgetTitle": 16,
            },
        )

    def test_generated_files_are_current(self):
        self.assertTrue(generate(check=True))

    def test_source_is_valid_json(self):
        self.assertIsInstance(json.loads(TOKENS_PATH.read_text()), dict)


if __name__ == "__main__":
    unittest.main()
