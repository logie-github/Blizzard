# Body shapes (Wrath++)

Makes `wrathpp-body.zip`, the body presets the app imports (`WrathppBody`, the held menu's **Body shapes (Wrath++)**).
The zip is the user's own; it is never in the app, the repository or a release. Nothing of Blizzard's is in it but
vertex data and a skin made from the looks' own model.

1. `refine.py`: the looks' model (`.m2` and `00.skin` from the `wrathpp-looks` release) with the triangles of the chest
   and seat split finer (red-green: a neighbour is split along the shared edge only; new vertices on the surface by
   Phong tessellation's edge midpoint, weights mixed). The worn gear's pieces (not the bare variant 01) and then the hair
   (at most 10%) give way so the skin stays within 3.3.5's 65535 indices.
2. The shapes: the body options' preview viewer (not in this repository) built on the refined model reshapes it to each
   preset (MakeHuman's CC0 chest and seat targets carried onto the model, the lower pole rounded, the areola mapped onto
   the shape's tip) and exports each preset's rest positions and texture coordinates.
3. `presets.py`: those written into the refined model's vertices (other pieces at the same places moved with them,
   normals turned by how much the shape turned the surface).
4. `pack.py`: the zip: `wrathpp-body.json`, the refined skin and one vertex block per preset, per race, named for the
   SHA-256 of the looks' model they were made from. The app puts a block at the end of that model and points its header
   at it; a model of other looks is left as drawn.

Races done: Human (14 November 2026). Each race is checked by rendering the very files the app makes with
`modules/mod-allied-races/tools/render_m2.py` (standing and running) before it goes into the zip.
