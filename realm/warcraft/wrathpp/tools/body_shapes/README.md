# Body shapes (Wrath++)

Makes `wrathpp-body.zip`, the body options package the app imports (`WrathppBody`, Settings' Wrath++ page, **Body
options**; the options themselves are each woman's, on the creator's Body tab: the main README, "Body options").
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
4. `pack.py`: the format 1 zip (the refined skin and one vertex block per preset), which `pack2.py` reads.
5. `layer.py`: the body layer over a model (a skin section of its own, geoset 1901, its vertices the body's own lifted
   0.4 mm; one batch, the character's hair texture times the display's design: the module's docstring has how the game
   draws it), the room for its indices made by `refine.py`'s `reserve`.
6. `masks.py`: the designs, one texture a style and density, from the design maps (yours, never in the repository).
7. `pack2.py OUT.zip LOOKS_CLIENT_DIR RACES.json MAPS_DIR [SHAPES_V1.zip]`: the package (format 2): per race the looks'
   own model with the layer, the body shapes' models where the format 1 zip has them (their three skins one), each a
   patch of the looks' model (its header and what follows its end, checked by both SHA-256s), and the designs.
   RACES.json: per race its scale, fold height, body sections and hair patch (`layer.py`).

Body shapes done: Human (14 November 2026). The layer: all ten races. Each race is checked by rendering the very files the app makes with
`modules/mod-allied-races/tools/render_m2.py` (standing and running) before it goes into the zip.
