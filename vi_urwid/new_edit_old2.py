#!/usr/bin/env python

"""
Urwid example lazy text editor suitable for tabbed and flowing text

Features:
- custom list walker for lazily loading text file

Usage:
edit.py <filename>

REF
https://stackoverflow.com/questions/65147261/how-does-urwid-handle-keypress-hierarchy

"""

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
        self.lines = []
        self.focus = 0

    def __del__(self) -> None:
        self.file.close()

    def get_focus(self):
        return self._get_at_pos(self.focus)

    def set_focus(self, focus) -> None:
        self.focus = focus
        self._modified()

    #def get_next(self, position: int) -> tuple[urwid.Edit, int] | tuple[None, None]:
    def get_next(self, position: int) -> tuple[UserInput, int] | tuple[None, None]:
        return self._get_at_pos(position + 1)

    #def get_prev(self, position: int) -> tuple[urwid.Edit, int] | tuple[None, None]:
    def get_prev(self, position: int) -> tuple[UserInput, int] | tuple[None, None]:
        return self._get_at_pos(position - 1)

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

        #edit = urwid.Edit("", expanded, allow_tab=True)
        edit = UserInput("", expanded, allow_tab=True)
        edit.edit_pos = 0
        edit.original_text = next_line
        self.lines.append(edit)

        return next_line

    #def _get_at_pos(self, pos: int) -> tuple[urwid.Edit, int] | tuple[None, None]:
    def _get_at_pos(self, pos: int) -> tuple[UserInput, int] | tuple[None, None]:
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
        pos = focus.edit_pos
        #edit = urwid.Edit("", focus.edit_text[pos:], allow_tab=True)
        edit = UserInput("", focus.edit_text[pos:], allow_tab=True)
        edit.original_text = ""
        focus.set_edit_text(focus.edit_text[:pos])
        edit.edit_pos = 0
        self.lines.insert(self.focus + 1, edit)

    def combine_focus_with_prev(self) -> None:
        """Combine the focus edit widget with the one above."""

        above, _ = self.get_prev(self.focus)
        if above is None:
            # already at the top
            return

        focus = self.lines[self.focus]
        above.set_edit_pos(len(above.edit_text))
        above.set_edit_text(above.edit_text + focus.edit_text)
        del self.lines[self.focus]
        self.focus -= 1

    def combine_focus_with_next(self) -> None:
        """Combine the focus edit widget with the one below."""

        below, _ = self.get_next(self.focus)
        if below is None:
            # already at bottom
            return

        focus = self.lines[self.focus]
        focus.set_edit_text(focus.edit_text + below.edit_text)
        del self.lines[self.focus + 1]


#urwid.Frame(urwid.AttrMap(self.listbox, "body"), footer=self.footer)
class Container(urwid.Frame):
    esc_mode = False
    def __init__(self,attrmap,footer , footer_text, logfile):
        #super("", expanded, allow_tab=True)
        super().__init__(attrmap, footer=footer)
        self.esc_mode = False
        self.footer = footer
        self.footer_text = footer_text
        self.logfile = logfile

    footer_data = (
        "foot2",
        [
            "Text Editor    ",
            "*** ",
            ("key", "F5"),
            " save  ",
            ("key", "F8"),
            " quit",
        ],
    )
    def keypress(self, size, key):
        #print(key, file=self.logfile)
        #print(self.footer, file=self.logfile)
        #print(self.footer.attr_map, file=self.logfile)
        if key == 'q':
            raise urwid.ExitMainLoop()
        if key == 'esc':
            if self.esc_mode:
                self.esc_mode = False
                tmp = self.footer_text.get_text()
                print("ESC ON "+tmp[0], file=self.logfile)

                self.footer_data[1][1] = "$$ "
                footer_text = urwid.Text(self.footer_data)
                self.footer_text.set_text(footer_text.text)
                self.footer = urwid.AttrMap(self.footer_text, "foot2")
                #self.footer_text.set_text("OK 1")

                tmp = self.footer_text.get_text()
                print("ESC ON "+tmp[0], file=self.logfile)
            else:
                self.esc_mode = True
                tmp = self.footer_text.get_text()
                print("ESC OFF "+tmp[0], file=self.logfile)
                self.footer_text.set_text("OK 2")
                tmp = self.footer_text.get_text()
                print("ESC OFF "+tmp[0], file=self.logfile)

            return None
        else:
            return super().keypress(size, key)

    


class EditDisplay:
    palette: typing.ClassVar[list[tuple[str, str, str, ...]]] = [
        ("body", "default", "default"),
        ("foot", "dark cyan", "dark blue", "bold"),
        ("foot2", "yellow", "dark green", "bold"),
        ("key", "light cyan", "dark blue", "underline"),
    ]

    footer_data = (
        "foot",
        [
            "Text Editor    ",
            "foo ",
            ("key", "F5"),
            " save  ",
            ("key", "F8"),
            " quit",
        ],
    )

    def __init__(self, name: str, log) -> None:
        self.save_name = name
        self.walker = LineWalker(name)
        self.listbox = urwid.ListBox(self.walker)
        self.footer_text = urwid.Text(self.footer_data)
        #self.footer_text = urwid.Text("footer_data")
        self.footer = urwid.AttrMap(self.footer_text, "foot")
        self.view = Container(urwid.AttrMap(self.listbox, "body"), footer=self.footer,footer_text=self.footer_text, logfile=log)


    def main(self) -> None:
        self.loop = urwid.MainLoop(self.view, self.palette, unhandled_input=self.unhandled_keypress)
        self.loop.run()

    def unhandled_keypress(self, k: str | tuple[str, int, int, int]) -> bool | None:
        """Last resort for keypresses."""

        if k == "f5":
            self.save_file()
        elif k == "f8":
            raise urwid.ExitMainLoop()
        elif k == "ctrl q":
            raise urwid.ExitMainLoop()
        elif k == "delete":
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
