# The data tools of War1gus and Wargus for Android (arm64), as programs the app runs on the phone:
# war1tool turns Warcraft I's GOG files into War1gus's data, wartool Warcraft II Battle.net
# Edition's into Wargus's. scripts/build-stratagus.sh builds them with the zlib, libpng and bzip2
# the engine's build made (STRATAGUS_BUILD), from the pinned War1gus and Wargus (WAR1GUS_SRC,
# WARGUS_SRC). Linked statically to the C++ library, they need nothing beside them.
cmake_minimum_required(VERSION 3.16)
project(warcraft_tools C CXX)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_POSITION_INDEPENDENT_CODE ON)

set(DEPS ${STRATAGUS_BUILD})
set(ZLIB_INC ${DEPS}/zlib/src/zlib-build)
set(ZLIB_LIB ${DEPS}/zlib/src/zlib-build/libz.a)
set(PNG_INC ${DEPS}/png/src/png-build)
set(PNG_LIB ${DEPS}/png/src/png-build/libpng.a)
set(BZ2_INC ${STRATAGUS_SRC}/third-party/bzip2)
set(BZ2_LIB ${DEPS}/bzip2/src/bzip2-build/libbz2.a)

# StormLib (Wargus's copy), for Warcraft II Battle.net Edition's MPQ archives.
add_subdirectory(${WARGUS_SRC}/StormLib stormlib EXCLUDE_FROM_ALL)

add_executable(wartool
	${WARGUS_SRC}/pud.cpp
	${WARGUS_SRC}/wartool.cpp
	${WARGUS_SRC}/xmi2mid.cpp
	${WARGUS_SRC}/rip_music_unix.cpp
)
target_include_directories(wartool PRIVATE ${WARGUS_SRC} ${WARGUS_SRC}/StormLib/src ${PNG_INC} ${ZLIB_INC} ${STRATAGUS_INCLUDE_DIR})
# rip_music_unix.cpp (audio CDs, unused here) names glibc's type for a device number.
target_compile_definitions(wartool PRIVATE USE_STORMLIB __dev_t=dev_t)
target_link_libraries(wartool PRIVATE storm ${PNG_LIB} ${ZLIB_LIB} ${BZ2_LIB} -static-libstdc++)

add_executable(war1tool
	${WAR1GUS_SRC}/war1tool.cpp
	${WAR1GUS_SRC}/xmi2mid.cpp
	${WAR1GUS_SRC}/scale2x.cpp
)
target_include_directories(war1tool PRIVATE ${WAR1GUS_SRC} ${PNG_INC} ${ZLIB_INC} ${STRATAGUS_INCLUDE_DIR})
target_link_libraries(war1tool PRIVATE ${PNG_LIB} ${ZLIB_LIB} -static-libstdc++)
