# Self-hosted fonts

Two variable fonts, Latin subset only, served from this origin.

| File | Family | Weight axis | Size |
|---|---|---|---|
| `inter-latin-var.woff2` | Inter | 100–900 | 48 KB |
| `space-grotesk-latin-var.woff2` | Space Grotesk | 300–700 | 22 KB |

## Why these are self-hosted

They were previously loaded from `fonts.googleapis.com`, which meant two extra
DNS + TLS handshakes on the critical path before any text could render in the
intended face — expensive on Kenyan mobile latency — and it sent every
visitor's IP address to Google on every page load, before any consent was
asked for. Serving them from here removes both, and lets the Cookie Policy
truthfully say the site makes no third-party requests until you opt in.

Because both are variable fonts, every weight the design uses comes from a
single file per family: 70 KB total, not one file per weight.

## Licence

Both are licensed under the SIL Open Font License 1.1, which permits
redistribution and web embedding.

- Inter — © The Inter Project Authors — <https://github.com/rsms/inter>
- Space Grotesk — © Florian Karsten — <https://github.com/floriankarsten/space-grotesk>

Full licence text: <https://openfontlicense.org/>

## Updating

Fetched from the Google Fonts CSS API (`css2`), taking the `/* latin */`
`@font-face` source for each family. Replace the files and confirm the weight
axis ranges in `main.css` still match.
