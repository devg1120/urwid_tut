#!/usr/bin/env python


from __future__ import annotations
from urwid.canvas import apply_text_layout

import sys
import typing
from urwid.util import decompose_tagmarkup, get_encoding
from pprint import pprint

import urwid
from enum import Enum

DBF = open("./dbp.log", mode = "w")
def pp(obj):
    pprint(obj, stream = DBF )
def p(msg):
    print(msg, file = DBF, flush = True )
    
def pn(*msgs):
    print(msgs, file = DBF, flush = True )

class Attr(Enum):
       INS = 1
       BS  = 2
       DEL = 3
class UserInput(urwid.Edit):
    esc_mode = False
    line_number = False
    line_number_len = 4

    def __init__(self,ln,b,allow_tab ):
        #super("", expanded, allow_tab=True)
        caps = ""
        if self.line_number:
           caps = str(ln).rjust(self.line_number_len) + " "
        super().__init__(caps,b, allow_tab = allow_tab)
        self.esc_mode = False


    def text_render(
        self,
        size: tuple[int] | tuple[()],  # type: ignore[override]
        focus: bool = False,
     ) -> urwid.TextCanvas:
        """
        Render contents with wrapping and alignment.  Return canvas.

        See :meth:`Widget.render` for parameter details.

        >>> Text(u"important things").render((18,)).text
        [b'important things  ']
        >>> Text(u"important things").render((11,)).text
        [b'important  ', b'things     ']
        >>> Text("demo text").render(()).text
        [b'demo text']
        """
        text, attr = self.get_text()
        """
        attr = [
                #("select",1),
                ("",1),
                ("rect",3),
                ("RGB",3)
                ]
        """
        if size:
            (maxcol,) = size
        else:
            maxcol, _ = self.pack(focus=focus)

        #trans = self.get_line_translation(maxcol, (text, attr))
        trans = super().get_line_translation(maxcol, (text, attr))
        return apply_text_layout(text, attr, trans, maxcol)


    def set_text(self, markup: str | tuple[Hashable, str] | list[str | tuple[Hashable, str]]) -> None:
        """
        Set content of text widget.

        :param markup: see :class:`Text` for description.
        :type markup: text markup

        >>> t = Text(u"foo")
        >>> print(t.text)
        foo
        >>> t.set_text(u"bar")
        >>> print(t.text)
        bar
        >>> t.text = u"baz"  # not supported because text stores text but set_text() takes markup
        Traceback (most recent call last):
        AttributeError: can't set attribute
        """
        #self._text, self._attrib = decompose_tagmarkup(markup)
        self._edit_text, self._attrib = decompose_tagmarkup(markup)
        self._invalidate()



    ## https://github.com/urwid/urwid/blob/master/urwid/widget/edit.py#L581

    def render(
        self,
        size: tuple[int],  # type: ignore[override]
        focus: bool = False,
    ) -> urwid.TextCanvas | urwid.CompositeCanvas:
        """
        Render edit widget and return canvas.  Include cursor when in
        focus.

        >>> edit = Edit("? ","yes")
        >>> c = edit.render((10,), focus=True)
        >>> c.text
        [b'? yes     ']
        >>> c.cursor
        (5, 0)
        """
        self._shift_view_to_cursor = bool(focus)  # noqa: FURB123,RUF100

        #canv: urwid.TextCanvas | urwid.CompositeCanvas = super().render(size, focus)
        canv: urwid.TextCanvas | urwid.CompositeCanvas = self.text_render(size, focus)
        if focus:
            canv = urwid.CompositeCanvas(canv)
            canv.cursor = self.get_cursor_coords(size)

        # .. will need to FIXME if I want highlight to work again
        # if self.highlight:
        #    hstart, hstop = self.highlight_coords()
        #    d.coords['highlight'] = [ hstart, hstop ]
        #d.coords['highlight'] = [ 1, 3 ]

        return canv


    def update_attr(self, t):

        dlist = []
        pos = 0
        for e in self._attrib:
            dlist.append((pos, pos + e[1] -1,e))
            pos = pos + e[1]

        p(self._attrib)
        p(dlist)
        new_attrib = []

        if t == Attr.INS :
           #p("pos:" + str(self.edit_pos))
           pos = self.edit_pos 
           if pos == 0:                      # head
              new_attrib.append(("",1))
              for  dl in dlist:
                 new_attrib.append(dl[2])
           elif pos == len(self._edit_text):  # tail
              for  dl in dlist:
                 new_attrib.append(dl[2])
              new_attrib.append(("",1))
           else:                              # mid
              for  dl in dlist:
                if pos   == dl[0]:
                   #p("#pre insert")
                   new_attrib.append(("",1))
                   new_attrib.append(dl[2])
                elif dl[0] < pos and pos  <= dl[1]:
                   #p("#mid insert")
                   d1 = dl[2]
                   d2 = (d1[0],d1[1]+1)
                   new_attrib.append(d2)
                else:
                   new_attrib.append(dl[2])
           #p(new_attrib)
           self._attrib = new_attrib
           
        elif t == Attr.BS :
           pos = self.edit_pos  
           for  dl in dlist:
              if dl[0] < pos  and pos -1 <= dl[1]:
                   #p("#mid insert")
                   d1 = dl[2]
                   d2 = (d1[0],d1[1]-1)
                   new_attrib.append(d2)
              else:
                   new_attrib.append(dl[2])
           #p(new_attrib)
           self._attrib = new_attrib
           
        elif t == Attr.DEL :
           pos = self.edit_pos  
           for  dl in dlist:
              #if dl[0] < pos  and pos -1 <= dl[1]:
              if dl[0] <= pos  and pos -1 < dl[1]:
              #if dl[0] < pos -1  and pos  <= dl[1]:
                   #p("#mid insert")
                   d1 = dl[2]
                   d2 = (d1[0],d1[1]-1)
                   new_attrib.append(d2)
              else:
                   new_attrib.append(dl[2])
           #p(new_attrib)
           self._attrib = new_attrib
           

    def insert_text(self, text: str) -> None:

        p('insert_text:' + str(self.edit_pos) + ":" + text)
        self.update_attr(Attr.INS)
        super().insert_text(text)

    def keypress(self, size, key):
        if key == 'backspace':
            p('backspace:' + str(self.edit_pos))
            self.update_attr(Attr.BS)
        elif key == 'delete':
            p('delete:' + str(self.edit_pos))
            self.update_attr(Attr.DEL)
        
        return super().keypress(size, key)


class CommandBar(urwid.Edit):
    esc_mode = False
    #line_number = False
    #line_number_len = 4

    def __init__(self,caps,b,allow_tab ):
        super().__init__(caps,b, allow_tab = allow_tab)
        self.esc_mode = False
        urwid.register_signal(self.__class__, ['command_exec'])
        

    def mouse_event(
        self,
        size: tuple[int],  # type: ignore[override]
        event: str,
        button: int,
        col: int,
        row: int,
        focus: bool,
        ) -> bool | None:
        """
        Move the cursor to the location clicked for button 1.

        >>> size = (20,)
        >>> e = Edit("","words here")
        >>> e.mouse_event(size, 'mouse press', 1, 2, 0, True)
        True
        >>> e.edit_pos
        2
        """
        pn("mouse_event:" , size,event,button,col,row,focus)
        if button == 1:
            return super().move_cursor_to_coords(size, col, row)
        return False

    def text_render(
        self,
        size: tuple[int] | tuple[()],  # type: ignore[override]
        focus: bool = False,
     ) -> urwid.TextCanvas:
        """
        Render contents with wrapping and alignment.  Return canvas.

        See :meth:`Widget.render` for parameter details.

        >>> Text(u"important things").render((18,)).text
        [b'important things  ']
        >>> Text(u"important things").render((11,)).text
        [b'important  ', b'things     ']
        >>> Text("demo text").render(()).text
        [b'demo text']
        """
        text, attr = self.get_text()
        """
        attr = [
                #("select",1),
                ("",1),
                ("rect",3),
                ("RGB",3)
                ]
        """
        if size:
            (maxcol,) = size
        else:
            maxcol, _ = self.pack(focus=focus)

        #trans = self.get_line_translation(maxcol, (text, attr))
        trans = super().get_line_translation(maxcol, (text, attr))
        return apply_text_layout(text, attr, trans, maxcol)


    def set_text(self, markup: str | tuple[Hashable, str] | list[str | tuple[Hashable, str]]) -> None:
        """
        Set content of text widget.

        :param markup: see :class:`Text` for description.
        :type markup: text markup

        >>> t = Text(u"foo")
        >>> print(t.text)
        foo
        >>> t.set_text(u"bar")
        >>> print(t.text)
        bar
        >>> t.text = u"baz"  # not supported because text stores text but set_text() takes markup
        Traceback (most recent call last):
        AttributeError: can't set attribute
        """
        #self._text, self._attrib = decompose_tagmarkup(markup)
        self._edit_text, self._attrib = decompose_tagmarkup(markup)
        self._invalidate()



    ## https://github.com/urwid/urwid/blob/master/urwid/widget/edit.py#L581

    def render(
        self,
        size: tuple[int],  # type: ignore[override]
        focus: bool = False,
    ) -> urwid.TextCanvas | urwid.CompositeCanvas:
        """
        Render edit widget and return canvas.  Include cursor when in
        focus.

        >>> edit = Edit("? ","yes")
        >>> c = edit.render((10,), focus=True)
        >>> c.text
        [b'? yes     ']
        >>> c.cursor
        (5, 0)
        """
        self._shift_view_to_cursor = bool(focus)  # noqa: FURB123,RUF100

        #canv: urwid.TextCanvas | urwid.CompositeCanvas = super().render(size, focus)
        canv: urwid.TextCanvas | urwid.CompositeCanvas = self.text_render(size, focus)
        if focus:
            canv = urwid.CompositeCanvas(canv)
            canv.cursor = self.get_cursor_coords(size)

        # .. will need to FIXME if I want highlight to work again
        # if self.highlight:
        #    hstart, hstop = self.highlight_coords()
        #    d.coords['highlight'] = [ hstart, hstop ]
        #d.coords['highlight'] = [ 1, 3 ]

        return canv


    def keypress(self, size, key):
        if key == 'enter':
            command = self.get_edit_text()
            p("commandBar: enter: " )
            p(command)
            urwid.emit_signal(self, "command_exec", command)
            return True
        else:
            return super().keypress(size, key)

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

    #def get_next(self, position: int) -> tuple[urwid.Edit, int] | tuple[None, None]:
    def get_next(self, position: int) -> tuple[UserInput, int] | tuple[None, None]:
        return self._get_at_pos(position + 1)

    #def get_prev(self, position: int) -> tuple[urwid.Edit, int] | tuple[None, None]:
    def get_prev(self, position: int) -> tuple[UserInput, int] | tuple[None, None]:
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

            #edit = urwid.Edit("", expanded, allow_tab=True)
            edit = UserInput(ln, expanded, allow_tab=True)

            ## https://urwid.org/manual/displayattributes.html
            #edit = urwid.AttrMap(urwid.Edit("", expanded, allow_tab=True),"edit")

            #edit = UserInput("", expanded, allow_tab=True)
            edit.edit_pos = 0
            edit.original_text = next_line
            edit_ = urwid.AttrMap(edit,"")
            #edit_ = urwid.AttrMap(edit,"", "focus")
            #edit_ = urwid.AttrMap(edit,"")
            #edit_.set_attr_map({"ABC": "rect"})
            #edit_.set_focus_map({None : "focus"})
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

        #edit = urwid.Edit("", expanded, allow_tab=True)
        edit = UserInput("", expanded, allow_tab=True)
        edit.edit_pos = 0
        edit.original_text = next_line
        edit_ = urwid.AttrMap(edit,"")
        self.lines.append(edit_)

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
        #pos = focus.edit_pos
        pos = focus.original_widget.edit_pos
        #edit = urwid.Edit("", focus.original_widget.edit_text[pos:], allow_tab=True)
        edit = UserInput("", focus.original_widget.edit_text[pos:], allow_tab=True)
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
        #edit = urwid.Edit("", expanded, allow_tab=True)
        edit = UserInput("", expanded, allow_tab=True)
        edit.edit_pos = 0
        edit.original_text = line_str
        edit_ = urwid.AttrMap(edit,"")
        self.lines.insert(self.focus + 1,edit_)
        self._modified()

    def insert_next_line(self) -> None:
        #edit = urwid.Edit("", "", allow_tab=True)
        edit = UserInput("", "", allow_tab=True)
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
            #edit_.focus_map = {None : 'focus'}

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

        text, attr = edit_.get_text()
        text2 = "xyz"
        edit_.set_edit_text(text2)

        line_ = self.lines[2]
        edit_ =line_.original_widget

        text, attr = edit_.get_text()
        text2 = "ABC"
        #edit_.set_text(("select",text2))
        #edit_.set_text(("select","AB"))
        #edit_.set_text(("select","ABC"))
        edit_.set_text([("select","AB"), ("rect","XY")])

        text, attr = edit_.get_text()
        pp(text)
        # ''ABXY'
        pp(attr)
        # [('select', 2), ('rect', 2)]

        edit_ = self.lines[4].original_widget
        edit_.set_text([("code_red","AB"),(None,"ABCDEFG"), ("code_green","XY")])

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
        #self.edit_command = urwid.Edit(":", "", allow_tab=True)
        #self.edit_command = UserInput(":", "", allow_tab=True)
        self.edit_command = CommandBar(":", "", allow_tab=True)
        super().__init__(attrmap, footer=self.footer)
        #super().__init__(attrmap, footer=self.edit_command)
        self.logfile = logfile

        urwid.connect_signal(self.edit_command, 'command_exec', self.command_exec)
        urwid.register_signal(self.__class__, ['split'])

        self.d_key = False  # dd  line-delete
        self.y_key = False  # yy  line-yank
        self.g_key = False  # gg  focus head
        self.yank = False
        self.yank_line = ""
        self.replace = False
        self.command_mode = False
        self.V_mode = False

    def command_exec(self, command):
        p("command_exec: " + command)

        #if command == "reset":
        #   urwid.emit_signal(self, "split", "reset")
        #elif command == "hsplit" or command == "split":
        #   urwid.emit_signal(self, "split", "hsplit")
        #elif command == "vsplit":
        #   urwid.emit_signal(self, "split", "vsplit")

        if command == "reset":
           p("REST")
           urwid.emit_signal(self, "split", Split.NSPLIT)
        elif command == "hsplit" or command == "split":
           urwid.emit_signal(self, "split", Split.HSPLIT)
        elif command == "vsplit":
           urwid.emit_signal(self, "split", Split.VSPLIT)

        self.keypress((0,),"esc")

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
                #size = (82,)
                #self.footer.mouse_event(size, 'mouse press', 1, 2, 0, False)
                #self.footer.mouse_event(size, 'mouse release', 1, 2, 0, True)
                #self.footer.insert_text("oK")
                #
                # https://urwid.org/manual/widgets.html#container-widgets

                p(self.get_focus_path())
                self._old_focus_path = self.get_focus_path()
                self.set_focus_path(['footer'])
                #self.set_focus_path(['body',0])
                p(self.get_focus_path())
                #self.footer.move_cursor_to_coords(size, 5, 0)
                #super().focus(True)mouse_event(size, 'mouse press', 1, 2, 0, True)
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
                if self.command_mode:
                    self.set_focus_path(self._old_focus_path)

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

class Split(Enum):
       NSPLIT = 1
       VSPLIT  = 2
       HSPLIT = 3

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
        ("RGB",  "light green",   "", ""),

        ("code_red",    "dark red",     "", "bold"),
        ("code_green",  "dark green",   "", "bold"),
    ]


    #def __init_S_(self, name: str, log) -> None:  # Single
    def __init__(self, name: str, log) -> None:  # Single
        self.split = Split.NSPLIT
        self.save_name = name
        self.log = log
        self.walker = LineWalker(name)
        self.listbox = urwid.ListBox(self.walker)
        self.view = Container(urwid.AttrMap(self.listbox, "body"), walker=self.walker, logfile=log)
        urwid.connect_signal(self.view, 'split', self.split_exec)


    def __init_V_(self, name: str, log) -> None:   # V split
    #def __init__(self, name: str, log) -> None:   # V split
        self.save_name = name
        self.walker1 = LineWalker(name)
        self.walker2 = LineWalker(name)
        self.walker2.lines = self.walker1.lines

        self.lb1 = urwid.ListBox(self.walker1)
        self.lb2 = urwid.ListBox(self.walker2)
        self.columns = urwid.Columns([self.lb1, self.lb2])
        self.view = Container(urwid.AttrMap(self.columns, "body"), walker=self.walker1, logfile=log)

    def __init_H_(self, name: str, log) -> None:  # H split
    #def __init__(self, name: str, log) -> None:  # H split
        self.save_name = name
        self.walker1 = LineWalker(name)
        self.walker2 = LineWalker(name)
        self.walker2.lines = self.walker1.lines

        self.lb1 = urwid.ListBox(self.walker1)
        self.lb2 = urwid.ListBox(self.walker2)
        self.pile = urwid.Pile([self.lb1, self.lb2])
        self.view = Container(urwid.AttrMap(self.pile, "body"), walker=self.walker1, logfile=log)


    def main(self) -> None:
        self.loop = urwid.MainLoop(self.view, self.palette, unhandled_input=self.unhandled_keypress)
        self.loop.run()

    def split_exec(self, mode):
        p("split_exec:" + str(mode))
        if mode == Split.NSPLIT:
           if self.split == Split.NSPLIT:
               return
           p("split_exec:" + "N")
           self.split = Split.NSPLIT
           self.view = Container(urwid.AttrMap(self.listbox, "body"), walker=self.walker, logfile=self.log)
           urwid.connect_signal(self.view, 'split', self.split_exec)
           self.loop.stop()
           self.loop = urwid.MainLoop(self.view, self.palette, unhandled_input=self.unhandled_keypress)
           self.loop.run()



        elif mode == Split.VSPLIT:
           if self.split != Split.NSPLIT:
               return
           p("split_exec:" + "V")
           self.split = Split.VSPLIT
           self.walker2 = LineWalker(self.save_name)
           self.walker2.lines = self.walker.lines

           #self.lb1 = urwid.ListBox(self.walker1)
           self.lb2 = urwid.ListBox(self.walker2)
           self.columns = urwid.Columns([self.listbox, self.lb2])
           self.view = Container(urwid.AttrMap(self.columns, "body"), walker=self.walker, logfile=self.log)
           urwid.connect_signal(self.view, 'split', self.split_exec)
           self.loop.stop()
           self.loop = urwid.MainLoop(self.view, self.palette, unhandled_input=self.unhandled_keypress)
           self.loop.run()


        elif mode == Split.HSPLIT:
           if self.split != Split.NSPLIT:
               return
           p("split_exec:" + "H")
           self.split = Split.HSPLIT
           self.walker2 = LineWalker(self.save_name)
           self.walker2.lines = self.walker.lines

           #self.lb1 = urwid.ListBox(self.walker1)
           self.lb2 = urwid.ListBox(self.walker2)

           self.pile = urwid.Pile([self.listbox, self.lb2])
           self.view = Container(urwid.AttrMap(self.pile, "body"), walker=self.walker, logfile=self.log)
           urwid.connect_signal(self.view, 'split', self.split_exec)
           self.loop.stop()
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
