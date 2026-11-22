/*
 * icu.dll shim for the ForeverNXT worldserver under Winlator's Wine: a UTC-only time zone database.
 *
 * worldserver.exe is built with C++20 <chrono> time zones. Its Microsoft C++ runtime (msvcp140_atomic_wait.dll, which the server
 * package ships) answers std::chrono::current_zone() and get_tzdb() by looking up 14 functions of Windows' own icu.dll
 * (ucal_*, uenum_*) at run time. Wine has no icu.dll: the lookup fails, the runtime throws from a static initialiser
 * (GameTime's StartTime, found with Wine's debugger on the real server, 22 November 2026) and the server dies in its crash handler.
 *
 * This answers those calls with one zone, "UTC", with no transitions and an offset of zero. The server then runs on UTC time zone
 * rules (what a time-zone-aware reset time or log time does is UTC's). It goes in the games' C:\windows\system32, which is where the
 * runtime looks (LOAD_LIBRARY_SEARCH_SYSTEM32).
 *
 * Written from ICU's documented C API (unicode.org); no ICU code. The names are the unversioned ones Windows' icu.dll exports.
 * Build (scripts/build-tools.sh): zig cc -target x86_64-windows-gnu -shared -O2 -s icu.c -o icu.dll
 */
#include <windows.h>
#include <stdint.h>
#include <string.h>
#include <stdlib.h>

typedef uint16_t UChar;
typedef int32_t UErrorCode;
typedef int8_t UBool;
typedef double UDate;

#define U_ZERO_ERROR 0
#define U_BUFFER_OVERFLOW_ERROR 15
#define UCAL_ZONE_OFFSET 15
#define UCAL_DST_OFFSET 16
#define API __declspec(dllexport)

static const UChar UTC[] = { 'U', 'T', 'C', 0 };
static const UChar UTC_NAME[] = { 'C', 'o', 'o', 'r', 'd', 'i', 'n', 'a', 't', 'e', 'd', ' ', 'U', 'n', 'i', 'v', 'e', 'r', 's', 'a', 'l', ' ', 'T', 'i', 'm', 'e', 0 };

/* Copies a UChar string into a caller's buffer the ICU way: the length needed is always returned, an overflow is flagged. */
static int32_t put(const UChar *src, UChar *dst, int32_t cap, UErrorCode *status)
{
	int32_t n = 0;
	while (src[n]) n++;
	if (dst && cap >= n) {
		memcpy(dst, src, n * sizeof(UChar));
		if (cap > n) dst[n] = 0;
	} else if (status) {
		*status = U_BUFFER_OVERFLOW_ERROR;
	}
	return n;
}

typedef struct { int32_t position; } Enumeration; /* one zone: position 0 is "UTC", then the end */
typedef struct { UDate millis; } Calendar;

API void *ucal_openTimeZoneIDEnumeration(int zoneType, const char *region, const int32_t *rawOffset, UErrorCode *status)
{
	(void)zoneType; (void)region; (void)rawOffset;
	if (status) *status = U_ZERO_ERROR;
	return calloc(1, sizeof(Enumeration));
}

API int32_t uenum_count(void *e, UErrorCode *status)
{
	(void)e;
	if (status) *status = U_ZERO_ERROR;
	return 1;
}

API const UChar *uenum_unext(void *e, int32_t *length, UErrorCode *status)
{
	Enumeration *en = (Enumeration *)e;
	if (status) *status = U_ZERO_ERROR;
	if (!en || en->position > 0) { if (length) *length = 0; return NULL; }
	en->position++;
	if (length) *length = 3;
	return UTC;
}

API void uenum_close(void *e) { free(e); }

API int32_t ucal_getDefaultTimeZone(UChar *result, int32_t cap, UErrorCode *status)
{
	if (status) *status = U_ZERO_ERROR;
	return put(UTC, result, cap, status);
}

API int32_t ucal_getCanonicalTimeZoneID(const UChar *id, int32_t len, UChar *result, int32_t cap, UBool *isSystemID, UErrorCode *status)
{
	(void)id; (void)len;
	if (status) *status = U_ZERO_ERROR;
	if (isSystemID) *isSystemID = 1;
	return put(UTC, result, cap, status);
}

API const char *ucal_getTZDataVersion(UErrorCode *status)
{
	if (status) *status = U_ZERO_ERROR;
	return "2025a";
}

API void *ucal_open(const UChar *zoneID, int32_t len, const char *locale, int type, UErrorCode *status)
{
	(void)zoneID; (void)len; (void)locale; (void)type;
	if (status) *status = U_ZERO_ERROR;
	return calloc(1, sizeof(Calendar));
}

API void ucal_close(void *cal) { free(cal); }

API void ucal_setMillis(void *cal, UDate millis, UErrorCode *status)
{
	if (cal) ((Calendar *)cal)->millis = millis;
	if (status) *status = U_ZERO_ERROR;
}

/* UTC: no zone offset, no daylight saving offset. */
API int32_t ucal_get(const void *cal, int field, UErrorCode *status)
{
	(void)cal; (void)field;
	if (status) *status = U_ZERO_ERROR;
	return 0;
}

API UBool ucal_inDaylightTime(const void *cal, UErrorCode *status)
{
	(void)cal;
	if (status) *status = U_ZERO_ERROR;
	return 0;
}

/* No transitions at all. */
API UBool ucal_getTimeZoneTransitionDate(const void *cal, int type, UDate *transition, UErrorCode *status)
{
	(void)cal; (void)type; (void)transition;
	if (status) *status = U_ZERO_ERROR;
	return 0;
}

/* Standard name: "UTC"; the long name: the full one. */
API int32_t ucal_getTimeZoneDisplayName(const void *cal, int type, const char *locale, UChar *result, int32_t cap, UErrorCode *status)
{
	(void)cal; (void)locale;
	if (status) *status = U_ZERO_ERROR;
	/* UCAL_STANDARD = 0, UCAL_SHORT_STANDARD = 1, UCAL_DST = 2, UCAL_SHORT_DST = 3 */
	return put((type == 0 || type == 2) ? UTC_NAME : UTC, result, cap, status);
}
