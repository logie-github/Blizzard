# The game's archives keep some files bzip2-compressed: the core's bzip2 (built for the map tools)
# lets the Skyborne's patch read them too.
if(TARGET bzip2)
  target_link_libraries(modules PRIVATE bzip2)
  target_compile_definitions(modules PRIVATE SKYBORNE_BZIP2)
endif()
