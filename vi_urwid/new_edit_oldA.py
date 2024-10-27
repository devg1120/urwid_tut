#!/usr/bin/env python


from __future__ import annotations

import sys
import typing

import urwid

class UserInput(urwid.Edit):
    esc_mode = False
    def __init__(self,a,b,allow_tab ):
        #super("", expanded, allow_tab=True)
        super().__init__(a,b, allow_tab = allow_tab)
        self.esc_mode = False
"""
    def keypress(self, size, key):
        if key == 'q':
            raise urwid.ExitMainLoop()
        if key == 'esc':
            if self.esc_mode:
                self.esc_mode = False
            else:
                self.esc_mode = True

            return None
        else:
            return super().keypress(size, key)
"""

class LineWalker(urwid.ListWalker):
    """ListWalker-compatible class for lazily reading file contents."""

    def __init__(self, name: str) -> None:
        # do not overcomplicate example
        self.file = open(name, encoding="utf-8")  # noqa: SIM115  # pylint: disable=consider-using-with
        self.logfile = open("linewalker.log", mode="w")
        self.lines = []
        self.focus = 0
        self.read_all_lines()


    def __del__(self) -> None:
        self.file.close()

    def log(self, msg):
        print(msg , file=self.logfile, flush=True)

    def get_focus(self):
        return self._get_at_pos(self.focus)

    def set_focus(self, focus) -> None:
        self.focus = focus
        self._modified()

    def get_next(self, position: int) -> tuple[urwid.Edit, int] | tuple[None, None]:
    #def get_next(self, position: int) -> tuple[UserInput, int] | tuple[None, None]:
        return self._get_at_pos(position + 1)

    def get_prev(self, position: int) -> tuple[urwid.Edit, int] | tuple[None, None]:
    #def get_prev(self, position: int) -> tuple[UserInput, int] | tuple[None, None]:
        return self._get_at_pos(position - 1)

    def read_all_lines(self) -> None:
        """Read another line from the file."""
        self.log("read_all_lines")

        lines = self.file.readlines()
        ln= 0
        for next_line in lines:
            ln += 1
            if not next_line or next_line[-1:] != "\n":
                # no newline on last line of file
                self.file = None
            else:
                # trim newline characters
                next_line = next_line[:-1]

            expanded = next_line.expandtabs()

            #edit = urwid.Edit(str(ln).zfill(3)+" ", expanded, allow_tab=True)
            edit = urwid.Edit("", expanded, allow_tab=True)
            #attr = ({"ABC": "select"}, "")
            #edit = urwid.Edit(attr, expanded, allow_tab=True)

            #edit_ = urwid.AttrMap(edit,"")
            ## https://urwid.org/manual/displayattributes.html
            #edit = urwid.AttrMap(urwid.Edit("", expanded, allow_tab=True),"edit")

            #edit = UserInput("", expanded, allow_tab=True)
            edit.edit_pos = 0
            edit.original_text = next_line
            #edit_ = urwid.AttrMap(edit,"")
            edit_ = urwid.AttrMap(edit,"", "focus")
            #edit_ = urwid.AttrMap(edit,"")
            edit_.set_attr_map({"ABC": "rect"})
            edit_.set_focus_map({None : "focus"})
            self.lines.append(edit_)

            #self.log(edit_.original_widget)
            #self.log(edit_.attr_map)


    def read_next_line(self) -> str:
        """Read another line from the file."""

        next_line = self.file.readline()

        if not next_line or next_line[-1:] != "\n":
            # no newline on last line of file
            self.file = None
        else:
            # trim newline characters
            next_line = next_line[:-1]

        expanded = next_line.expandtabs()

        edit = urwid.Edit("", expanded, allow_tab=True)
        #edit = UserInput("", expanded, allow_tab=True)
        edit.edit_pos = 0
        edit.original_text = next_line
        edit_ = urwid.AttrMap(edit,"")
        self.lines.append(edit_)

        return next_line

    def _get_at_pos(self, pos: int) -> tuple[urwid.Edit, int] | tuple[None, None]:
    #def _get_at_pos(self, pos: int) -> tuple[UserInput, int] | tuple[None, None]:
        """Return a widget for the line number passed."""

        if pos < 0:
            # line 0 is the start of the file, no more above
            return None, None

        if len(self.lines) > pos:
            # we have that line so return it
            return self.lines[pos], pos

        if self.file is None:
            # file is closed, so there are no more lines
            return None, None

        assert pos == len(self.lines), "out of order request?"  # noqa: S101  # "assert" is ok in examples

        self.read_next_line()

        return self.lines[-1], pos

    def split_focus(self) -> None:
        """Divide the focus edit widget at the cursor location."""

        focus = self.lines[self.focus]
        #pos = focus.edit_pos
        pos = focus.original_widget.edit_pos
        edit = urwid.Edit("", focus.original_widget.edit_text[pos:], allow_tab=True)
        #edit = UserInput("", focus.edit_text[pos:], allow_tab=True)
        edit.original_text = ""
        #focus.set_edit_text(focus.edit_text[:pos])
        focus.original_widget.set_edit_text(focus.original_widget.edit_text[:pos])
        edit.edit_pos = 0
        edit_ = urwid.AttrMap(edit,"")
        self.lines.insert(self.focus + 1, edit_)

    def combine_focus_with_prev(self) -> None:
        """Combine the focus edit widget with the one above."""

        above, _ = self.get_prev(self.focus)
        if above is None:
            # already at the top
            return

        focus = self.lines[self.focus]
        #above.set_edit_pos(len(above.edit_text))
        #above.set_edit_text(above.edit_text + focus.edit_text)
        above.original_widget.set_edit_pos(len(above.original_widget.edit_text))
        above.original_widget.set_edit_text(above.original_widget.edit_text + focus.original_widget.edit_text)
        del self.lines[self.focus]
        self.focus -= 1


    def combine_focus_with_next(self) -> None:

        below, _ = self.get_next(self.focus)
        if below is None:
            # already at bottom
            return

        focus = self.lines[self.focus]
        #focus.set_edit_text(focus.edit_text + below.edit_text)
        focus.original_widget.set_edit_text(focus.original_widget.edit_text + below.original_widget.edit_text)
        del self.lines[self.focus + 1]

    def delete_line(self) -> None:
        del self.lines[self.focus ]
        self._modified()

    def yank_line(self) -> str:
        #line_str =  self.lines[self.focus ].get_edit_text()
        line_str =  self.lines[self.focus ].original_widget.edit_text
        return line_str

    def paste_line(self, line_str) -> None:
        expanded = line_str.expandtabs()
        edit = urwid.Edit("", expanded, allow_tab=True)
        edit.edit_pos = 0
        edit.original_text = line_str
        edit_ = urwid.AttrMap(edit,"")
        self.lines.insert(self.focus + 1,edit_)
        self._modified()

    def insert_next_line(self) -> None:
        edit = urwid.Edit("", "", allow_tab=True)
        edit.edit_pos = 0
        edit.original_text = ""
        self.lines.insert(self.focus + 1,edit)
        self.focus += 1
        self._modified()

    def focus_head(self) -> None:
        self.focus = 0
        self._modified()
    
    def focus_tail(self) -> None:
        self.focus = len(self.lines) -1
        self._modified()

    def replace(self, key) -> None:
        edit = self.lines[self.focus]    
        #edit.insert_text(key)    
        pos = edit.original_widget.edit_pos    
        text = edit.original_widget.edit_text    
        textlist = list(text)    
        textlist[pos:pos+1] = key    
        new_text = "".join(textlist)    
        edit.original_widget.set_edit_text(new_text)  

    def pos_line_head(self):
        edit = self.lines[self.focus]
        #edit.edit_pos = 0
        edit.original_widget.edit_pos = 0
        self._modified()

    def pos_line_tail(self):
        edit = self.lines[self.focus]
        #edit.edit_pos = len(edit.edit_text) 
        edit.original_widget.edit_pos = len(edit.original_widget.edit_text) 
        self._modified()

    def start_V_mode(self):
        edit = self.lines[self.focus]
        self.start_V_mode_pos = self.focus
        self.lines[self.focus] = urwid.AttrMap(edit.original_widget,"select")
        self._modified()

    """
    def down_V_mode_(self):
        self.focus += 1
        edit = self.lines[self.focus]
        self.lines[self.focus] = urwid.AttrMap(edit.original_widget,"select")
        self._modified()
    def up_V_mode_(self):
        self.focus -= 1
        edit = self.lines[self.focus]
        self.lines[self.focus] = urwid.AttrMap(edit.original_widget,"select")
        self._modified()
    """

    def down_V_mode(self):
        if self.focus == len(self.lines)-1:
            return
        if self.start_V_mode_pos > self.focus:
          edit = self.lines[self.focus]
          self.lines[self.focus] = urwid.AttrMap(edit.original_widget,"")
          #self.lines[self.focus] = urwid.AttrMap(edit.original_text,"")
          self.focus += 1
        else:
          self.focus += 1
          edit = self.lines[self.focus]
          self.lines[self.focus] = urwid.AttrMap(edit.original_widget,"select")
        self._modified()
    def up_V_mode(self):
        if self.focus == 0:
            return
        if self.start_V_mode_pos < self.focus:
          edit = self.lines[self.focus]
          self.lines[self.focus] = urwid.AttrMap(edit.original_widget,"")
          self.focus -= 1
        else:
          self.focus -= 1
          edit = self.lines[self.focus]
          self.lines[self.focus] = urwid.AttrMap(edit.original_widget,"select")
          #self.lines[self.focus] = urwid.AttrMap(edit.original_text,"select")
        self._modified()

    def lines_dump(self):
        ln = 0
        for edit_ in self.lines:
            ln += 1
            self.log(str(ln).zfill(2) + " widget: " + str(edit_.original_widget))
            self.log("  " + " attr_map: " + str(edit_.attr_map))

    def lines_reset_attr_map(self):
        for edit_ in self.lines:
            edit_.attr_map = {None : '', 'E': 'rect'}
            edit_.focus_map = {None : 'focus'}

    def test1(self):
        for edit_ in self.lines:
            edit_.attr_map = {None : 'rect'}
    def test2(self):
        for edit_ in self.lines:
            #edit_.attr_map = {None : 'rect'}
            self.log(edit_.original_widget)
            self.log(edit_.original_widget.original_text)
            self.log(edit_.original_widget.text)
            #edit_.original_widget.original_text = ('rect', "abcdef")

    def test(self):
        line_ = self.lines[0]
        edit_ =line_.original_widget
        text = edit_.original_text
        edit_.set_edit_text("ABC")
        c = edit_.render((1,))  # 5 = length
        c.content(cols=3, rows=1, attr = {None: "rect"})
        b = urwid.TextCanvas(["xyz".encode("utf-8")])
        cl = c.content(b)
        for ci in cl:
           self.log(str(ci))
           #c[0] = ({"A": "rect"}, None, b'X')
           #c[0] = (None, None, b'X')
           #self.log(str(c[0][0]))
           #self.log(str(c))

        #p = urwid.CompositeCanvas(c)
        #p.fill_attr_apply({"ABC":"rect"})

        #edit = urwid.Edit(u"head",('rect',u"ABC"),text, text.expandtabs, allow_tab=True)
        #edit = urwid.Edit("","ABC",  text.expandtabs, allow_tab=True)
        #self.lines[0] = urwid.AttrMap(edit,"")
        self._modified()


#urwid.Frame(urwid.AttrMap(self.listbox, "body"), footer=self.footer)
class Container(urwid.Frame):
    esc_mode = False
    footer_data = (
        "foot",
        [
            "Text Editor    ",
            "Goo ",
            ("key", "F5"),
            " save  ",
            ("key", "F8"),
            " quit",
        ],
    )
    def __init__(self,attrmap,walker, logfile):
        self.esc_mode = False
        self.walker = walker
        self.footer_text = urwid.Text(self.footer_data)
        self.footer = urwid.AttrMap(self.footer_text, "foot")
        self.edit_command = urwid.Edit(":", "", allow_tab=True)
        super().__init__(attrmap, footer=self.footer)
        #super().__init__(attrmap, footer=self.edit_command)
        self.logfile = logfile

        self.d_key = False  # dd  line-delete
        self.y_key = False  # yy  line-yank
        self.g_key = False  # gg  focus head
        self.yank = False
        self.yank_line = ""
        self.replace = False
        self.command_mode = False
        self.V_mode = False

    def log(self, msg):
        print(msg , file=self.logfile, flush=True)

    def keypress(self, size, key):
        if self.replace:
           self.esc_mode = False
           self.replace = False
           self.walker.replace(key)
           return True

        if key == 'q':
            if  self.esc_mode:
               raise urwid.ExitMainLoop()
        elif key == ':':
            if  self.esc_mode:
                self.command_mode = True
                #edit_command = urwid.Edit(":", "", allow_tab=True)
                self.footer = self.edit_command
                #super().__init__(attrmap, footer=self.footer)
                return True

        elif key == 'x':
            if  self.esc_mode:
                key = "delete"
            else:
                 pass

        elif key == 'd':
            if  self.esc_mode:
                if self.d_key:
                   self.walker.delete_line()
                   self.d_key = False;
                else:
                   self.d_key = True;
                return True
            else:
                 pass

        elif key == 'y':
            if  self.esc_mode:
                if self.y_key:
                   self.yank_line = self.walker.yank_line()
                   self.y_key = False;
                   self.yank = True;
                else:
                   self.y_key = True;
                return True
            else:
                 pass

        elif key == 'g':
            if  self.esc_mode:
                if self.g_key:
                   self.walker.focus_head()
                   self.g_key = False;
                else:
                   self.g_key = True;
                return True
            else:
                 pass

        elif key == 'G':
            if  self.esc_mode:
                self.walker.focus_tail()
                return True
            else:
                 pass

        elif key == 'p':
            if  self.esc_mode:
                if self.yank:
                   self.walker.paste_line(self.yank_line)
                   self.yank = False;
                   return True
            else:
                 pass

        elif key == 'o':
            if  self.esc_mode:
                 self.walker.insert_next_line()
                 return True
            else:
                 pass
        elif key == 'r':
            if  self.esc_mode:
                self.replace = True
                return True

        elif key == 'I':
            if  self.esc_mode:
                self.walker.pos_line_head()
                return True
        elif key == 'A':
            if  self.esc_mode:
                self.walker.pos_line_tail()
                return True
        elif key == 'V':
            if  self.esc_mode:
                self.V_mode = True
                self.walker.start_V_mode()
                return True
        elif key == 'down':
            if  self.esc_mode:
                if self.V_mode:
                  self.walker.down_V_mode()
                  return True
        elif key == 'up':
            if  self.esc_mode:
                if self.V_mode:
                  self.walker.up_V_mode()
                  return True
        elif key == 'S':
            if  self.esc_mode:
                  #self.walker.save_file()
                  key = "SaveFile"
                  #return True
        elif key == 'T':
            if  self.esc_mode:
                  self.walker.test()
                  return True

        elif key == 'esc':
            if self.esc_mode:
                self.esc_mode = False
                tmp = self.footer_text.get_text()
                self.log("ESC OFF "+tmp[0])

                self.footer_data[1][1] = "** "
                footer_text = urwid.Text(self.footer_data)
                self.footer_text.set_text(footer_text.text)
                self.footer = urwid.AttrMap(self.footer_text, "foot")
                #self.footer_text.set_text("OK 1")
                #self.walker.lines_dump()
                self.walker.lines_reset_attr_map()

            else:
                self.esc_mode = True
                tmp = self.footer_text.get_text()
                self.log("ESC ON "+tmp[0])
                self.footer_data[1][1] = "$$ "
                footer_text = urwid.Text(self.footer_data)
                self.footer_text.set_text(footer_text.text)
                self.footer = urwid.AttrMap(self.footer_text, "foot2")

                #self.footer_text.set_text("OK 2")

            return None

        return super().keypress(size, key)

    
"""
https://urwid.org/manual/displayattributes.html
前景色
'black'
'dark red'
'dark green'
'brown'
'dark blue'
'dark magenta'
'dark cyan'
'light gray'
'dark gray'
'light red'
'light green'
'yellow'
'light blue'
'light magenta'
'light cyan'
'white'


背景色
'black'
'dark red'
'dark green'
'brown'
'dark blue'
'dark magenta'
'dark cyan'
'light gray'

「明るい」背景色¶
'dark gray'
'light red'
'light green'
'yellow'
'light blue'
'light magenta'
'light cyan'
'white'


太字、下線、目立つ¶
'bold'
'underline'
'standout'
'blink'
'italics'
'strikethrough'
"""

class EditDisplay:
    palette: typing.ClassVar[list[tuple[str, str, str, ...]]] = [
        ("body", "default", "default"),
        ("foot", "dark cyan", "dark blue", "bold"),
        ("foot2", "yellow", "dark green", "bold"),
        ("edit", "", "", ""),
        ("select", "yellow", "dark gray", "bold"),
        ("focus",  "black", "dark blue", "bold"),
        ("rect",  "black",   "dark blue", "bold"),
        ("key", "light cyan", "dark blue", "underline"),
    ]


    def __init__(self, name: str, log) -> None:
        self.save_name = name
        self.walker = LineWalker(name)
        self.listbox = urwid.ListBox(self.walker)
        self.view = Container(urwid.AttrMap(self.listbox, "body"), walker=self.walker, logfile=log)


    def main(self) -> None:
        self.loop = urwid.MainLoop(self.view, self.palette, unhandled_input=self.unhandled_keypress)
        self.loop.run()

    def unhandled_keypress(self, k: str | tuple[str, int, int, int]) -> bool | None:
        """Last resort for keypresses."""

        if k == "f5":
            self.save_file()
        elif k == "SaveFile":
            self.save_file()
        elif k == "f8":
            raise urwid.ExitMainLoop()
        elif k == "Quit":
            raise urwid.ExitMainLoop()
        elif k == "ctrl q":
            raise urwid.ExitMainLoop()
        elif k == "delete":
            # delete at end of line
            self.walker.combine_focus_with_next()
        elif k == "x":
            # delete at end of line
            self.walker.combine_focus_with_next()
        elif k == "backspace":
            # backspace at beginning of line
            self.walker.combine_focus_with_prev()
        elif k == "enter":
            # start new line
            self.walker.split_focus()
            # move the cursor to the new line and reset pref_col
            self.loop.process_input(["down", "home"])
        elif k == "right":
            w, pos = self.walker.get_focus()
            w, pos = self.walker.get_next(pos)
            if w:
                self.listbox.set_focus(pos, "above")
                self.loop.process_input(["home"])
        elif k == "left":
            w, pos = self.walker.get_focus()
            w, pos = self.walker.get_prev(pos)
            if w:
                self.listbox.set_focus(pos, "below")
                self.loop.process_input(["end"])
        else:
            return None
        return True

    def save_file(self) -> None:
        """Write the file out to disk."""

        lines = []
        walk = self.walker
        for edit in walk.lines:
            # collect the text already stored in edit widgets
            #if edit.original_text.expandtabs() == edit.edit_text:
            if edit.original_widget.original_text.expandtabs() == edit.original_widget.edit_text:
                lines.append(edit.original_widget.original_text)
            else:
                lines.append(re_tab(edit.original_widget.edit_text))

        # then the rest
        while walk.file is not None:
            lines.append(walk.read_next_line())

        # write back to disk
        with open(self.save_name, "w", encoding="utf-8") as outfile:
            prefix = ""
            for line in lines:
                outfile.write(prefix + line)
                prefix = "\n"

    def save_file_org(self) -> None:
        """Write the file out to disk."""

        lines = []
        walk = self.walker
        for edit in walk.lines:
            # collect the text already stored in edit widgets
            if edit.original_text.expandtabs() == edit.edit_text:
                lines.append(edit.original_text)
            else:
                lines.append(re_tab(edit.edit_text))

        # then the rest
        while walk.file is not None:
            lines.append(walk.read_next_line())

        # write back to disk
        with open(self.save_name, "w", encoding="utf-8") as outfile:
            prefix = ""
            for line in lines:
                outfile.write(prefix + line)
                prefix = "\n"


def re_tab(s) -> str:
    """Return a tabbed string from an expanded one."""
    line = []
    p = 0
    for i in range(8, len(s), 8):
        if s[i - 2 : i] == "  ":
            # collapse two or more spaces into a tab
            line.append(f"{s[p:i].rstrip()}\t")
            p = i

    if p == 0:
        return s

    line.append(s[p:])
    return "".join(line)


def main() -> None:
    try:
        name = sys.argv[1]
        # do not overcomplicate example
        assert open(name, "ab")  # noqa: SIM115,S101  # pylint: disable=consider-using-with
    except OSError:
        sys.stderr.write(__doc__)
        return
    log = open("./log",mode='w')
    EditDisplay(name,log).main()


if __name__ == "__main__":
    main()
