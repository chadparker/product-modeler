# Appearance

Appearance information is optional. When present, it supplements Interface behavior with:

- reference screenshots and render profiles;
- design tokens, fonts, icons, and assets;
- important component and screen states;
- structural layout descriptions;
- per-screen or per-region Preservation Policies.

Allowed policies in format version `0.1`:

- `exact`
- `structural`
- `adaptive`
- `inspirational`
- `unspecified`

Exact means visually equivalent under a defined render profile, not universally pixel-identical across environments.
