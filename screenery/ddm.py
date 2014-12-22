#!/usr/bin/env python

class DeviceDisplayMatrix():

    def __init__(self):
        self.verticle_screen = 1920
        self.horizontal_screen = 1080
        self.screens = 3
        self.workspaces_verticle = 4
        self.workspaces_horizontal = 4
        self.vdl = [[[[0, 0] for i in range(self.screens)] for j in range(
            self.workspaces_verticle)] for k in range(self.workspaces_horizontal)]

    def setup_matrix(self):
        """ temporary settings for now, will be set per device out of the registry. """

        i = j = k = hs = vs = 0
        for row in self.vdl:
            for workspace in row:
                for screen in workspace:
                    self.vdl[i][j][k] = [vs, hs]
                    vs += self.verticle_screen
                    k += 1
                k = 0
                j += 1
            hs += self.horizontal_screen
            vs = 0
            j = 0
            i += 1

        print("Resolution matrix of offsets:\n")
        for row in self.vdl:
            print("%s" % row)

        print("Row 2, workspace 3, screen 2 H: %s, V: %s\n" %
              (self.vdl[1][2][1][0], self.vdl[1][2][1][1]))
        print("Row 1, workspace 1, screen 1 H: %s, V: %s\n" %
              (self.vdl[0][0][0][0], self.vdl[0][0][0][1]))

    def restore_app(self, window_title, x, y, z, h, v):
        e = "0,{},{},-1,-1".format(self.vdl[x][y][z][0], self.vdl[x][y][z][1])
        print("e: %s" % (e))
        subprocess.call("wmctrl -r %s -e %s" % (window_title, e), shell=True)
