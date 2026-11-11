#!/usr/bin/env bash
# A release's description: the patch note of every change since the previous release, then how to install.
#
# Each change that reaches main adds one file to notes/ (notes/README.md): YYYY-MM-DD-what.txt, one line in plain words.
# The notes are those files added since the newest blizzard-build-N tag (the previous release), in their names' order
# (oldest first), each as "- <line>"; the app reads those "- " lines from the releases list (update/PatchNotes.kt) and
# shows them on Settings' Games page. A run cancelled by a newer push leaves its notes to the next release.
#
# Run from the repository with its history and tags (CI: actions/checkout with fetch-depth 0). Prints to stdout.
set -euo pipefail

prefix="${RELEASE_TAG_PREFIX:-blizzard-build}"
# The previous release: the newest release tag in this history.
previous=""
for number in $(git tag -l "$prefix-*" | sed -n "s/^$prefix-\([0-9][0-9]*\)\$/\1/p" | sort -rn); do
	if git merge-base --is-ancestor "$prefix-$number" HEAD 2>/dev/null; then
		previous="$prefix-$number"
		break
	fi
done
if [ -n "$previous" ]; then
	added=$(git diff --name-only --diff-filter=A "$previous" HEAD -- notes/)
else
	# No release before this one: every note there is.
	added=$(git ls-files notes/)
fi

for file in $added; do
	case "$file" in
		notes/*.txt) ;;
		*) continue ;;
	esac
	[ -f "$file" ] || continue
	# The file's first line with words; a leading "-" or "*" the writer put there isn't doubled.
	line=$(grep -m 1 -v '^[[:space:]]*$' "$file" | sed -e 's/^[[:space:]]*//' -e 's/^[-*][[:space:]]*//' -e 's/[[:space:]]*$//' || true)
	[ -n "$line" ] && printf -- '- %s\n' "$line"
done
printf '\nInstall Blizzard.apk on the phone; it installs over earlier releases.\n'
