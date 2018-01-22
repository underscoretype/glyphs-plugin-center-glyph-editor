# encoding: utf-8

###########################################################################################################
#
#
#	Center Glyph Editor
#
#   A simple Plugin for Glyphs App to center the Glyph selected for editing
#
#   (c) Johannes "kontur" Neumeier 2018
#
#
#   My thanks for a plentitude of code examples borrowed from:
#   - Georg Seifert (@schriftgestalt) https://github.com/schriftgestalt/GlyphsSDK
#   - Rainer Erich Scheichelbauer (@mekkablue) https://github.com/mekkablue/SyncSelection
#
#
###########################################################################################################


from GlyphsApp.plugins import *
from GlyphsApp import *

class CenterGlyphEditor(GeneralPlugin):

    def settings(self):
        self.name = Glyphs.localize({
            'en': u'Center Glyph Editor'
        })

        NSUserDefaults.standardUserDefaults().registerDefaults_(
            {
                "com.underscoretype.CenterGlyphEditor.state": False
            }
        )


    def start(self):
        try:
            # no logging in production version
            self.logging = False

            menuItem = NSMenuItem(self.name, self.toggleMenu)
            menuItem.setState_(bool(Glyphs.defaults["com.underscoretype.CenterGlyphEditor.state"]))
            Glyphs.menu[GLYPH_MENU].append(menuItem)
        
        except Exception as e:
            self.log("Registering menu entry did not work")
            self.log("Exception: %s" % str(e))

        self.lastCursor = ""

        if Glyphs.defaults["com.underscoretype.CenterGlyphEditor.state"]:
            self.addSyncCallback()

        self.log("CenterGlyphEditor start()")


    # use local debugging flag to enable or disable verbose output
    def log(self, message):
        if self.logging:
            self.logToConsole(message)
    

    def toggleMenu(self, sender):
        self.log("CenterGlyphEditor toggleMenu()")
        self.log(Glyphs.defaults["com.underscoretype.CenterGlyphEditor.state"])

        if Glyphs.defaults["com.underscoretype.CenterGlyphEditor.state"]:
            Glyphs.defaults["com.underscoretype.CenterGlyphEditor.state"] = False
            self.removeSyncCallback()
        else:
            Glyphs.defaults["com.underscoretype.CenterGlyphEditor.state"] = True
            self.addSyncCallback()
        
        currentState = Glyphs.defaults["com.underscoretype.CenterGlyphEditor.state"]
        Glyphs.menu[GLYPH_MENU].submenu().itemWithTitle_(self.name).setState_(currentState)


    def addSyncCallback(self):
        try:
            Glyphs.addCallback(self.keepGlyphCenter, DRAWFOREGROUND)
            self.log("CenterGlyphEditor addSyncCallback()")
        except Exception as e:
            self.log("CenterGlyphEditor addSyncCallback() Exception: %s" % str(e))
    

    def removeSyncCallback(self):
        try:
            Glyphs.removeCallback(self.keepGlyphCenter, DRAWFOREGROUND)
            self.log("CenterGlyphEditor removeSyncCallback()")
        except Exception as e:
            self.log("CenterGlyphEditor removeSyncCallback() Exception: %s" % str(e))


    # use the foreground drawing loop hook to check if metrics updates are required
    def keepGlyphCenter(self, layer, info):
        tab = Glyphs.fonts[0].currentTab
        tool = Glyphs.currentDocument.windowController().toolDrawDelegate()

        # if there are no nodes nor components in the layer (e.g. it is empty)
        # don't try to center
        if not layer.paths and not layer.components:
            return

        # only center for certain tools (i.e. not for annotation, and text tool has it's own jump to cursor)
        if tool.__class__.__name__ not in ["GlyphsToolSelect", "PenTool", "GlyphsToolRotate", "GlyphsToolScale", "GlyphsToolTrueTypeInstructor"]:
            return

        # Only trigger an update when a new glyph is selected
        if tab.layersCursor != self.lastCursor or self.lastCursor is None:
            self.log("New active glyph %s" % str(layer.parent))
            self.lastCursor = tab.layersCursor
            self.centerGlyph()


    def centerGlyph(self):
        tab = Glyphs.fonts[0].currentTab
        layer = tab.layers[tab.layersCursor]
        height = Glyphs.fonts[0].upm * 1.5
        w = layer.width * tab.scale
        h = height * tab.scale
        x = tab.selectedLayerOrigin.x
        y = tab.selectedLayerOrigin.y - h / 3
        rect = NSMakeRect(x, y, w, h )
        view = Glyphs.fonts[0].currentTab.graphicView()
        view.zoomViewToRect_(rect)
