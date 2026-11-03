# Appends one call to $CALLS_LOG: program, arguments, working folder, the environment the programs read.
record() {
	name=$1
	shift
	{
		printf 'PROG %s\n' "$name"
		for a in "$@"; do printf 'ARG %s\n' "$a"; done
		printf 'CWD %s\n' "$(pwd)"
		for v in LD_PRELOAD OPENSSL_MODULES HOME TMPDIR TZ AC_DISABLE_INTERACTIVE WOW_MODULES_CONF_DIR WOW_CLIENT_DIR \
			WOW_REPORTS_DIR WOW_TRANSFERS_DIR WOW_SELECTION_FILE WOW_CUTSCENE_FILE WOW_INTERFACE_FILE WOW_ZONES_DIR; do
			eval "printf 'ENV $v=%s\n' \"\${$v-<unset>}\""
		done
		echo END
	} >> "$CALLS_LOG"
	cat > /dev/null
}
