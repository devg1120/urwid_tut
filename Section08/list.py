#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# list.py
#
import urwid

import application  
import detail
from listwalker import ListWalker
from mywidget import *
from common import Common

class List(application.Application):  
    def __init__(self, common):
        self.common = common

    def next_page(self, ignored=None):
        if not self.last_page():
            self.common.from_rec += self.rows
            self.main_loop.widget = self.doformat()

    def prior_page(self, ignored=None):
        if self.common.from_rec > self.rows:
            self.common.from_rec -= self.rows
            self.main_loop.widget = self.doformat()

    def first_page(self):
        return self.common.from_rec == 1

    def last_page(self):
        return self.is_last
    
    def unhandled_keypress(self, k):
        if self.main_loop.widget.focus_position == 'header' and k == 'down':
            self.main_loop.widget.focus_position = 'body'
        elif self.main_loop.widget.focus_position == 'body' and k == 'up':
            self.main_loop.widget.focus_position = 'header'

        if k in ('q', 'Q'):
            self.exit()        
        elif k in ('n', 'N'):
            self.next_page()
        elif k in ('p', 'P'):
            self.prior_page()
        elif k == 'enter':
            self.start_detail()
        else:
            return
        return True
    def get_start_record(self, item):
        if self.common.from_rec >= self.common.selected_item:
            return self.common.from_rec
        if int(item/self.rows)*self.rows == item:
            return (int(item/self.rows) - 1)*self.rows+1
        else:
            return (int(item/self.rows))*self.rows+1
    def doformat(self):
        self.cols, self.rows = self.get_cols_rows()
        self.common.from_rec =  self.get_start_record(self.common.selected_item)

        walker = ListWalker(get_items(self.common.table_name), self.common.from_rec, self.rows)
        self.is_last = walker.last_page()
        self.listbox = urwid.ListBox(walker)

        if self.last_page():
            btn_next = urwid.Divider()
        else:
            btn_next = create_mybutton("N", self.next_page)
        if self.first_page():            
            btn_prior = urwid.Divider()
        else:
            btn_prior = create_mybutton("P", self.prior_page)

        btn_q = create_mybutton("Q", self.exit)
        header = urwid.GridFlow([btn_next, btn_prior, btn_q], 6, 1, 1, 'left')

        self.footer_text = urwid.Text(u"これはフッター")
        footer = urwid.AttrWrap(self.footer_text, "foot")

        frame = MyFrame(urwid.AttrWrap(self.listbox, 'body'), header=header, footer=footer)
        frame.double_click = self.start_detail

        if self.common.from_rec <= self.common.selected_item < self.common.from_rec+self.rows:
            self.listbox.focus_position = self.common.selected_item - self.common.from_rec
            self.common.selected_item = 0
            frame.focus_position = 'body'
        else:
            frame.focus_position = 'header'
        return frame 

    def start_detail(self):
        self.common.selected_item = self.listbox.focus_position + self.common.from_rec
        self.start(detail.Detail, self.common)

def main():
    common = Common()
    List(common).run()

if __name__=="__main__":
    main()
