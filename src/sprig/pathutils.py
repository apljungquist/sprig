"""Some nice to have functions for interacting with paths"""
import collections
import filecmp
import os
import stat


class ldircmp(filecmp.dircmp):
    """Like `filecmp.dircmp` but with `os.lstat` instead of `os.stat`"""

    # pylint: disable=C0103,C0111,W0201,W0612

    def phase2(self):  # Distinguish files, directories, funnies
        self.common_dirs = []
        self.common_files = []
        self.common_funny = []

        for x in self.common:
            a_path = os.path.join(self.left, x)
            b_path = os.path.join(self.right, x)

            ok = 1
            try:
                a_stat = os.lstat(a_path)
            except OSError as why:
                # print('Can\'t stat', a_path, ':', why.args[1])
                ok = 0
            try:
                b_stat = os.lstat(b_path)
            except OSError as why:
                # print('Can\'t stat', b_path, ':', why.args[1])
                ok = 0

            if ok:
                a_type = stat.S_IFMT(a_stat.st_mode)
                b_type = stat.S_IFMT(b_stat.st_mode)
                if a_type != b_type:
                    self.common_funny.append(x)
                elif stat.S_ISDIR(a_type):
                    self.common_dirs.append(x)
                elif stat.S_ISREG(a_type):
                    self.common_files.append(x)
                else:
                    self.common_funny.append(x)
            else:
                self.common_funny.append(x)

    def phase4(self):  # Find out differences between common subdirectories
        # A new dircmp object is created for each common subdirectory,
        # these are stored in a dictionary indexed by filename.
        # The hide and ignore properties are inherited from the parent
        self.subdirs = {}
        for x in self.common_dirs:
            a_x = os.path.join(self.left, x)
            b_x = os.path.join(self.right, x)
            self.subdirs[x] = ldircmp(a_x, b_x, self.ignore, self.hide)

    methodmap = dict(  # type: ignore
        subdirs=phase4,
        same_files=filecmp.dircmp.phase3,
        diff_files=filecmp.dircmp.phase3,
        funny_files=filecmp.dircmp.phase3,
        common_dirs=phase2,
        common_files=phase2,
        common_funny=phase2,
        common=filecmp.dircmp.phase1,
        left_only=filecmp.dircmp.phase1,
        right_only=filecmp.dircmp.phase1,
        left_list=filecmp.dircmp.phase0,
        right_list=filecmp.dircmp.phase0
    )


def rcmp(dcmp: filecmp.dircmp) -> bool:
    """Check `filecmp.dircmp` recursively for any difference

    :param dcmp: The `filecmp.dircmp` object to check.
    :return: `True` if no difference is found, `False` otherwise
    """
    dcmps = collections.deque([dcmp])
    while dcmps:
        dcmp = dcmps.popleft()
        if any([dcmp.left_only, dcmp.right_only, dcmp.common_funny,
                dcmp.diff_files]):
            return False
        dcmps.extend(dcmp.subdirs.values())
    return True
