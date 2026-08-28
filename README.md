# EECA Data Visualisation Styles

The shared source of truth for EECA data visualisation colours, typography, and
platform-specific style assets. The initial tokens are based on the current
`eeud-dashboard` styling.

## Structure

- `tokens/tokens.json` is the only manually maintained token file.
- `dist/` contains generated SCSS, CSS, Python, and JSON assets.
- `maps/` contains specialised map styles that are maintained separately from
  the generated design tokens.
- `scripts/generate.py` generates all distribution files without third-party
  dependencies.

Do not edit files under `dist/` directly.
Semantic colours and platform settings use `{token.path}` aliases so each
primitive brand colour is maintained once and resolved during generation.
For example, changing `colors.brand.sky-blue-light` updates the shared
selection role and the generated Databricks light-mode selection colour.

Consumers should pin a release tag or commit rather than referencing `main`, so
style changes can be reviewed and adopted deliberately.

## Generate and verify

```bash
python3 scripts/generate.py
python3 scripts/generate.py --check
python3 -m unittest discover -s tests
```

## Fonts

Web applications prefer National 2 and fall back to Arial and the browser's
sans-serif font. National 2 is commercially licensed and its font files must
not be stored or published from this repository. Each authorised application
is responsible for serving its licensed copies.

Plotly uses Arial because static chart exports cannot be assumed to have
National 2 installed. Databricks uses its supported Inter font. The Databricks
font roles use the Enquire dashboard scale: 14px for base text, field titles,
and descriptions; 16px for field values and widget titles. The Databricks theme
JSON can be refined after the live development-workspace theme has been
retrieved and compared.

## Generated assets

- `dist/scss/_tokens.scss`: Sass variables and palettes for Shiny/Quarto.
- `dist/css/tokens.css`: CSS custom properties for web applications.
- `dist/python/eeca_visualisation_styles.py`: Python constants and a Plotly
  layout dictionary.
- `dist/json/tokens.json`: platform-neutral JSON for JavaScript and other
  consumers.
- `dist/json/databricks-dashboard-theme.json`: portable AI/BI dashboard theme
  block using supported fonts.

Domain-specific colour mappings, such as EEUD's energy taxonomy, should stay
with the owning product unless multiple products agree on the same semantics.

## Deployment

Pull requests and pushes to `main` validate that generated assets are current.
Pushing a semantic tag builds and publishes immutable GitHub Release assets:

- Stable: `v1.2.3`
- Pre-release: `v1.2.3-rc1`

The tag without its leading `v` must exactly match `version` in
`tokens/tokens.json`. A release contains each generated format, the existing map
style, a complete tarball, and `SHA256SUMS`.

To release, update the token version in a pull request, merge it, and tag that
exact commit:

```bash
git tag v0.1.0
git push origin v0.1.0
```

The GitHub Pages site at
https://eeca-nz.github.io/data-visualisation-styles/ remains useful for the
existing map and current assets, but downstream builds should use immutable
release assets.

### Pin a downstream build

For example, an Enquire build can pin and verify the Databricks JSON:

```bash
styles_version="v0.1.0"
release_url="https://github.com/EECA-NZ/data-visualisation-styles/releases/download/${styles_version}"

curl -fsSLO "${release_url}/databricks-dashboard-theme.json"
curl -fsSLO "${release_url}/SHA256SUMS"
grep ' databricks-dashboard-theme.json$' SHA256SUMS | sha256sum -c -
```

The downloaded theme can then be merged into the dashboard's
`uiSettings.theme` during its build, before bundle validation and deployment.
