package com.logie.blizz.porter.view

/** The character preview's native half (porter/engine, libporter.so). Every call but [create] on the preview's GL thread. */
internal object Native {
    init { System.loadLibrary("porter") }

    /** A viewer reading the game's files from [dir] (each named by its id). */
    @JvmStatic external fun create(dir: String): Long
    @JvmStatic external fun destroy(handle: Long)
    @JvmStatic external fun initGl(handle: Long)
    @JvmStatic external fun releaseGl(handle: Long)
    @JvmStatic external fun clear(handle: Long)
    @JvmStatic external fun setCharacter(handle: Long, model: Int, groupKeys: IntArray, groupValues: IntArray): Boolean
    /** [layers]: six numbers a layer (file, x, y, width, height, blend). */
    @JvmStatic external fun setCanvas(handle: Long, type: Int, width: Int, height: Int, layers: IntArray)
    @JvmStatic external fun setTexture(handle: Long, type: Int, file: Int)
    @JvmStatic external fun attach(handle: Long, attachment: Int, model: Int, texKeys: IntArray, texValues: IntArray): Boolean
    @JvmStatic external fun addSkinned(handle: Long, model: Int, texKeys: IntArray, texValues: IntArray, geosets: IntArray): Boolean
    @JvmStatic external fun setAnim(handle: Long, anim: Int)
    /** Radians, radians, 1 for the whole character, 0..1 up the character. */
    @JvmStatic external fun setView(handle: Long, yaw: Float, pitch: Float, zoom: Float, lift: Float)
    @JvmStatic external fun setBackdrop(handle: Long, top: FloatArray, bottom: FloatArray)
    @JvmStatic external fun render(handle: Long, width: Int, height: Int, nowMs: Long)
    @JvmStatic external fun hasCharacter(handle: Long): Boolean
}
