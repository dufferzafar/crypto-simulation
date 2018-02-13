"""
Convert all .dot files to .png files.
"""

import os

OUT_DIR = "output/"

# TODO: Replace with glob.glob
for fn in os.listdir(OUT_DIR):

    if fn.endswith(".dot"):

        fn = os.path.join(OUT_DIR, fn)

        graph = fn[:-4] + ".png"
        cmd = "dot -Tpng %s -o %s" % (fn, graph)

        # TODO: Replace with subprocess.call
        os.system(cmd)
