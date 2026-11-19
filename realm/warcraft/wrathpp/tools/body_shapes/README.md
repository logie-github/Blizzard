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
   RACES.json: per race its scale, fold height, body sections and hair patch (`layer.py`), or the race whose files
   it is drawn with; the package's list carries each race's entry (`layer`) for the app to make the layer itself.
8. `check.py PACKAGE.zip LOOKS_CLIENT_DIR`: every model the package makes checked as the 3.3.5 client loads it (the
   header's arrays and texture names in the file, the combiner list, the skin's arrays, each section's vertices, indices
   and bones, each batch's references, the section starts read wide, the layer's batch and section).

9. `measure.py LOOKS_DIR RACES.json Name=id ...`: a race's entry of `races.json` measured on the looks' own woman (her scale
   from the hip and knee key bones, the fold estimated, the body's sections, the hair patch; a race without hair
   textures draws the design over her own body texture). The fold is looked at in a render and corrected by hand.
10. `shapes.py`: the Human's three shapes carried onto every other race's woman without the viewer (which is gone):
    `source` makes the shapes' field over her body from the format 1 zip and her refined model (yours, as the zip is);
    `carry` gives each race a format 1 entry: the field taken by the place on the body texture, turned and scaled as her
    body is against the Human's there, on her model refined where the shapes move it. `pack2.py` takes its zip.
11. `render.py PACKAGE.zip LOOKS_DIR OUT_DIR`: the package's models as the app makes them, drawn (the layer close, the
    chest and seat of each shape, standing and running): what is looked at before a package goes anywhere.

The whole package for new looks (LOOKS: the looks package unpacked, MAPS: your design maps, FIELD: `shapes.py source`'s):

    python3 rebase.py HUMAN_V1.zip OLD_LOOKS/client LOOKS/client human_v1.zip      # (when the Human's model only moved)
    python3 shapes.py carry FIELD.npz human_v1.zip LOOKS races.json v1_all.zip
    python3 pack2.py wrathpp-body.zip LOOKS/client races.json MAPS v1_all.zip
    python3 check.py wrathpp-body.zip LOOKS/client && python3 render.py wrathpp-body.zip LOOKS out --views close,chest,seat,run

Done (18 November 2026): the layer and the three shapes for the women of all 23 races (22 models: the High Elf is drawn
with the Void Elf's files), on the looks of commit b20fe1e. Each race is checked by rendering the very files the app
makes (`render.py`). On looks the package was not made for, the app makes the layer itself (`WrathppBodyLayer`: `layer.py`'s
`add` in Kotlin, the same bytes) and carries the shapes onto the looks' own mesh, so one import lasts; a package made
again for the new looks gives the shapes their finer mesh back.
