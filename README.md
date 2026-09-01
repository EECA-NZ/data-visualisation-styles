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

A release contains each generated format, the existing map style, a complete
tarball, `SHA256SUMS`, and a generated manifest recording its version, tag, and
source commit. GitHub generates the human-readable release notes from the
commits associated with the tag.

To release, merge the approved style changes and push a tag for that exact
commit. The workflow creates the corresponding GitHub Release, so a Release
does not need to be published manually through the GitHub UI:

```bash
git tag v0.1.0
git push origin v0.1.0
```

If a GitHub Release already exists for the tag, the workflow updates its title
and uploads the generated assets with replacement enabled. This makes a failed
or manually initiated release safely rerunnable without moving the tag.

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
grep -E ' (\./)?databricks-dashboard-theme.json$' SHA256SUMS | sha256sum -c -
```

The downloaded theme can then be merged into the dashboard's
`uiSettings.theme` during its build, before bundle validation and deployment.

### Use a pinned release in an R Shiny dashboard

Download and verify the required assets during the application build rather
than making the deployed application depend on GitHub at runtime:

```bash
styles_version="v0.1.0"
release_url="https://github.com/EECA-NZ/data-visualisation-styles/releases/download/${styles_version}"
download_dir="$(mktemp -d)"

curl -fsSLo "${download_dir}/tokens.css" "${release_url}/tokens.css"
curl -fsSLo "${download_dir}/tokens.json" "${release_url}/tokens.json"
curl -fsSLo "${download_dir}/SHA256SUMS" "${release_url}/SHA256SUMS"

(
  cd "${download_dir}"
  grep -E ' (\./)?(tokens.css|tokens.json)$' SHA256SUMS | sha256sum -c -
)

install -D "${download_dir}/tokens.css" www/vendor/eeca/tokens.css
install -D "${download_dir}/tokens.json" www/vendor/eeca/tokens.json
```

Load the CSS tokens in `app.R` and read the same release's JSON tokens for
Plotly colours:

```r
library(jsonlite)
library(plotly)
library(shiny)

tokens <- read_json(
  file.path("www", "vendor", "eeca", "tokens.json"),
  simplifyVector = TRUE
)

ui <- fluidPage(
  tags$head(
    tags$link(rel = "stylesheet", href = "vendor/eeca/tokens.css"),
    tags$link(rel = "stylesheet", href = "app.css")
  ),
  h1("Energy use in New Zealand"),
  div(class = "dashboard-card", plotlyOutput("energy_plot"))
)

server <- function(input, output, session) {
  output$energy_plot <- renderPlotly({
    plot_ly(
      iris,
      x = ~Sepal.Length,
      y = ~Petal.Length,
      color = ~Species,
      colors = tokens$palettes$categorical,
      type = "scatter",
      mode = "markers"
    ) |>
      layout(
        font = list(
          family = "Arial, sans-serif",
          size = 14,
          color = tokens$colors$interface$text
        ),
        paper_bgcolor = tokens$colors$interface$surface,
        plot_bgcolor = tokens$colors$interface$surface
      )
  })
}

shinyApp(ui, server)
```

Application-specific layout can then reference the shared properties from
`www/app.css` without copying brand values:

```css
body {
  background: var(--eeca-page);
  color: var(--eeca-text);
  font-family: var(--eeca-font-family-web);
}

.dashboard-card {
  background: var(--eeca-surface);
  border: 1px solid var(--eeca-border);
  border-radius: var(--eeca-corner-radius);
  padding: 1rem;
}
```

An authorised app can load its licensed National 2 web fonts before
`tokens.css`; otherwise the shared font stack falls back to Arial. Apps that
compile Sass can pin and download `_tokens.scss` in the same way.
