import urwid

t1 = urwid.Text('lorem')
t2 = urwid.Text('ipsum')
cols = urwid.Columns([t1, t2], dividechars=2)
root = urwid.Filler(cols)
urwid.MainLoop(root).run()