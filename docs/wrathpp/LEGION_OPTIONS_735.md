# Legion 7.3.5 customization inventory

**Status: not inventoried.** No Legion 7.3.5 table has been read in this session; nothing below is
offered as a list of what Legion had. The registry's two categories are an engineering seed,
marked `"legion": {"verified": false}`, and must be replaced by data from the procedure below
before anything is advertised as "Legion's".

## Source of truth

The user's own Legion 7.3.5 client, build **26972** (the repository's Legion realm uses it:
`LegionClientSetup.kt`, `RealmSpecs.kt`), installed by the app under the Legion game folder. Its
CASC storage holds the client database tables (DB2) and the character models that define what
each race/sex could choose in 7.3.5. Not current retail tables: `mod-allied-races/tools/races.py`
reads retail's `ChrCustomization*` tables (a Shadowlands-era model), which Legion did not have.

## Procedure

1. Export from the 7.3.5 client (any CASC tool the user already has) the DB2 tables that define
   character looks at that build, as CSV, and the character models (`character/<race>/<sex>/*.m2`
   with their `.skin` files) of each race to inventory.
2. Record each file's name, size and SHA-256 with the build number (provenance).
3. For each race/sex: list every look category the 7.3.5 creator offered, its option count, the
   textures/geosets each option uses, class restrictions (demon hunter only, death knight only) and
   exclusions. Record the table rows that prove each.
4. For each geoset category, confirm the group and variants exist in the **Wrath++ client's** model
   for that race (the Alternative HD model the client will actually draw, which may differ from
   7.3.5's): `realm/warcraft/wrathpp/tools/` will get a probe that lists a `.skin` file's geoset ids.
5. Write the result as registry categories with `"legion": {"verified": true, "evidence": ...}`,
   one race/sex at a time (MILESTONES.md phase 6).

## What is known only as a hypothesis (to verify, not to build on)

- Legion added demon hunter looks for blood elves and night elves (horns, blindfolds, tattoos) as
  categories beside the stock ones. Their exact counts per sex and whether tattoo colour was a
  separate category in 7.3.5 are not confirmed.
- In current models geoset group 24 is used for horns (`mod-allied-races` maps the Lightforged
  women's horns from group 24). That this holds for 7.3.5's blood elf / night elf demon hunter
  horns, and that blindfolds are group 25, is unverified; the seed registry uses 24 and 25 only so
  the engineering slice has numbers to carry.
- The Wrath++ realm has no demon hunter class; the seed opens the look to every class
  (`wrathpp_class_rule` in the registry). Whether to keep Legion's class restriction once a demon
  hunter class exists is a later, separate decision.
