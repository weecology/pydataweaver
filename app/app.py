
import wx


class Frame(wx.Frame):
    def __init__(self, parent, id, title):
        wx.Frame.__init__(self, parent, id, title, wx.DefaultPosition, wx.Size(450, 350))
 
        hbox = wx.BoxSizer(wx.HORIZONTAL)
        vbox = wx.BoxSizer(wx.VERTICAL)
        panel1 = wx.Panel(self, -1)
        panel2 = wx.Panel(self, -1)
 
        self.tree = wx.TreeCtrl(panel1, 1, wx.DefaultPosition, (-1,-1), wx.TR_HIDE_ROOT|wx.TR_HAS_BUTTONS)
        root = self.tree.AddRoot('weaver Data')
        os = self.tree.AppendItem(root, 'Gis data')
        pl = self.tree.AppendItem(root, 'Time Series')

        cl = self.tree.AppendItem(pl, 'Integrated Data')
        sl = self.tree.AppendItem(pl, 'world data')
        self.tree.AppendItem(cl, 'Plants')

        self.tree.Bind(wx.EVT_TREE_SEL_CHANGED, self.OnSelChanged, id=1)
        self.display = wx.StaticText(panel2, -1, '',(10,10), style=wx.ALIGN_CENTRE)
        vbox.Add(self.tree, 1, wx.EXPAND)
        hbox.Add(panel1, 1, wx.EXPAND)
        hbox.Add(panel2, 1, wx.EXPAND)
        panel1.SetSizer(vbox)
        self.SetSizer(hbox)
        self.Centre()
 
    def OnSelChanged(self, event):
        item =  event.GetItem()
        self.display.SetLabel(self.tree.GetItemText(item))
 
class App(wx.App):
    def OnInit(self):
        frame = Frame(None, -1, 'treectrl.py')
        frame.Show(True)
        self.SetTopWindow(frame)
        return True