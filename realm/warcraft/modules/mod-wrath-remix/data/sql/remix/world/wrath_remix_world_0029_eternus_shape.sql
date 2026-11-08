-- Eternus in her own shape (src/RemixModels.cpp, tools/models.py): her dragon as the realm knows
-- it. The game's patch gets the same two rows (ClientPatch.cpp) with her model's files, which the
-- server package fetches and converts into the module's data/models (never in the repository).
-- Her parts take this look only when the patch has her; without it these rows are unused.
--   CreatureModelData 3500: the game's dragon's (2723, Creature\Dragon\Dragon.mdx, her size) with
--     her model and its bounds (the newer games', standing).
--   CreatureDisplayInfo 32900: that dragon's look (23746) with her skin, at scale 1 (her parts have
--     their own: 0.4 at the Bazaar and in her scenes, 0.5 at the last hour).
--   creature_model_info: her reach and size at scale 1, a woman's look.

DELETE FROM `creaturemodeldata_dbc` WHERE `ID` = 3500;
INSERT INTO `creaturemodeldata_dbc` (`ID`, `Flags`, `ModelName`, `SizeClass`, `ModelScale`, `BloodID`, `FootprintTextureID`,
    `FootprintTextureLength`, `FootprintTextureWidth`, `FootprintParticleScale`, `FoleyMaterialID`, `FootstepShakeSize`,
    `DeathThudShakeSize`, `SoundID`, `CollisionWidth`, `CollisionHeight`, `MountHeight`, `GeoBoxMinX`, `GeoBoxMinY`, `GeoBoxMinZ`,
    `GeoBoxMaxX`, `GeoBoxMaxY`, `GeoBoxMaxZ`, `WorldEffectScale`, `AttachedEffectScale`, `MissileCollisionRadius`,
    `MissileCollisionPush`, `MissileCollisionRaise`) VALUES
(3500, 0, 'Creature\\Eternus\\Eternus.mdx', 4, 1, 1, 5, 30, 20, 3, 0, 2, 12, 191, 0.6111, 2.031, 8.139,
 -19.34, -9.86, -0.55, 10.24, 9.66, 13.43, 1, 1, 0, 0, 0);

DELETE FROM `creaturedisplayinfo_dbc` WHERE `ID` = 32900;
INSERT INTO `creaturedisplayinfo_dbc` (`ID`, `ModelID`, `SoundID`, `ExtendedDisplayInfoID`, `CreatureModelScale`, `CreatureModelAlpha`,
    `TextureVariation_1`, `TextureVariation_2`, `TextureVariation_3`, `PortraitTextureName`, `BloodLevel`, `BloodID`, `NPCSoundID`,
    `ParticleColorID`, `CreatureGeosetData`, `ObjectEffectPackageID`) VALUES
(32900, 3500, 0, 0, 1, 255, 'EternusSkin', 'EternusSkin', '', '', 3, 0, 0, 0, 0, 0);

DELETE FROM `creature_model_info` WHERE `DisplayID` = 32900;
INSERT INTO `creature_model_info` (`DisplayID`, `BoundingRadius`, `CombatReach`, `Gender`, `DisplayID_Other_Gender`, `VerifiedBuild`) VALUES
(32900, 2.5, 10, 1, 0, 0);
