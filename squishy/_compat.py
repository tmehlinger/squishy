import sys

import six


if sys.version_info[:2] == (2, 6):
    def viewkeys(d):
        return d.keys()
else:
    def viewkeys(d):
        return six.viewkeys(d)
