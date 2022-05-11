from collections import defaultdict

from github import File

from .labels import INTERNAL_LABELS, Label


def ischange(line: str):
    return line.startswith(("+", "-"))


def patch_changes(patch: str):
    return list(filter(ischange, patch.splitlines()))


def file_sieve(files: list[File.File]) -> tuple[list[Label], dict[str, list[Label]]]:
    """Takes a list of File objects and figures out what tags apply."""
    labels: list[Label] = []
    packages: dict[str, list[Label]] = defaultdict(lambda: list())
    for file in files:
        filename = file.filename
        if filename.startswith(("xbps-src", "common/", "etc/")):
            if filename == "common/shlibs":
                labels += [Label.SHLIBS]
                continue
            labels += [Label.XBPS_SRC]
            continue
        if filename in ("Manual.md", "README.md", "CONTRIBUTING.md"):
            labels += [Label.DOCS]
            continue
        if filename.startswith(("srcpkgs/")):
            filename = filename.removeprefix("srcpkgs/")
            fp = filename.split("/")
            pkg = fp[0]
            if len(fp) >= 2:
                # the file is in the package's directory
                if fp[1] == "template":
                    match file.status:
                        case "added":
                            packages[pkg] += [Label.NEW]
                        case "removed":
                            packages[pkg] += [Label.DELETE]
                        case _:
                            changes = patch_changes(file.patch)
                            for chg in changes:
                                if chg.startswith(("-version=", "+version=")):
                                    packages[pkg] += [Label.UPDATE]
                                    continue
                                if chg.startswith(("-revision=", "+revision=")):
                                    packages[pkg] += [Label.REVBUMP]
                                elif chg.startswith(("-checksum=", "+checksum=")):
                                    pass
                                else:
                                    packages[pkg] += [Label.CLEANUP]
                else:
                    # the modified file is not the template
                    packages[pkg] += [Label.CLEANUP]
            else:
                # we have a symlink to a package
                match file.status:
                    case "added":
                        # Could be a package being renamed or a new subpackage
                        packages[pkg] += [Label.NEWLINK]
                        target = patch_changes(file.patch)[0].removeprefix("+")
                        packages[target] += [Label.NEWTARGET]
                    case "removed":
                        packages[pkg] += [Label.DELETE]
    return (labels, packages)


def  package_sieve(labels: list[Label], packages: dict[str, list[Label]]) -> list[Label]:
    for pkg, l in packages.items():
        if Label.DELETE in l and Label.NEWLINK in l:
            # If the package is a new link and has a deleted template,
            # it has moved to a new name.
            labels += [Label.RENAMED]
            continue
        if Label.NEW in l and Label.NEWTARGET in l:
            # If the package both has a new template or is the target
            # of a new symlink, it is the result of a rename operation
            labels += [Label.RENAMED]
            continue
        if Label.DELETE in l:
            # The package is GONE, TURNED TO ETERNAL DUST
            # and we thus not care about anything else from it.
            labels += [Label.DELETE]
            continue
        if Label.NEW in l:
            # If the package is new, any other info is noise
            labels += [Label.NEW]
            continue
        if Label.UPDATE in l:
            # In the case of package update, we don't care if that package
            # got minor change labels like revbump or cleanup-fixups
            labels += [Label.UPDATE]
            continue
        # We only have revbump and/or cleanup-fixups
        labels += l
    deduped = list(set(labels))
    if deduped == [Label.UPDATE]:
        # <ahesford> it would be nice to have an automatic label added if the only change is version, revision and checksum
        # <Piraty> [SIMPLE]
        # <ahesford> [DECEPTIVELY SIMPLE]
        # <Piraty> [TRIVIAL]
        deduped += [Label.TRIVIAL]
    return deduped
