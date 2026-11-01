# SPDX-License-Identifier: GPL-3.0-only
# Blast Wind (Japan) recompilation project.
#
# The toolkit is the copy in satrecomp/ (made by satrecomp/tools/sync-toolkit.sh).
# local.mk is the developer's own file (git-ignored) and may set DISC to an
# absolute path containing spaces.
GAME ?= blastwind
SR ?= satrecomp

-include local.mk

include $(SR)/build.mk

# check.sh reads DISC from the environment, not from make; keep the path set in
# local.mk (or on the command line) available to it.
export DISC
