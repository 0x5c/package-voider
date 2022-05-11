from enum import Enum


class Label(Enum):
    XBPS_SRC = "xbps-src"
    SHLIBS = "shlibs"
    DOCS = "documentation"

    NEW = "new-package"
    CLEANUP = "cleanup-fixup"
    REVBUMP = "revbump"
    UPDATE = "update"
    RENAMED = "renamed"
    DELETE = "deletion"

    TRIVIAL = "trivial"

    NEWLINK = "_link_new"
    NEWTARGET = "_target_new"

INTERNAL_LABELS = {
    Label.NEWLINK,
    Label.NEWTARGET
}
