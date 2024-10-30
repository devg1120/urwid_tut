import urwid as u

class ListItem(u.WidgetWrap):
    
    def __init__ (self, country):
                
        self.content = country
        
        name = country["name"]
        
        t = u.AttrWrap(u.Text(name), "country", "country_selected")

        u.WidgetWrap.__init__(self, t)

    def selectable (self):
        return True
    
    def keypress(self, size, key):
        return key

class ListView(u.WidgetWrap):

    def __init__(self):

        u.register_signal(self.__class__, ['show_details'])

        self.walker = u.SimpleFocusListWalker([])

        lb = u.ListBox(self.walker)
        
        u.WidgetWrap.__init__(self, lb)

    def modified(self):
    
        focus_w, _ = self.walker.get_focus()

        u.emit_signal(self, 'show_details', focus_w.content)

    def set_data(self, countries):
        
        countries_widgets = [ListItem(c) for c in countries]

        u.disconnect_signal(self.walker, 'modified', self.modified)

        while len(self.walker) > 0:
            self.walker.pop()
        
        self.walker.extend(countries_widgets)

        u.connect_signal(self.walker, "modified", self.modified)

        self.walker.set_focus(0)

class DetailView(u.WidgetWrap):
    
    def __init__ (self):
        t = u.Text("")
        u.WidgetWrap.__init__(self, t)
        
    def set_country(self, c):
        s = f'Name: {c["name"]}\nPop:  {c["pop"]}\nGDP:  {c["gdp"]}'
        self._w.set_text(s)

class App(object):
    
    def unhandled_input(self, key):
        if key in ('q',):
            raise u.ExitMainLoop()

    def show_details(self, country):
        self.detail_view.set_country(country)
        
    def __init__(self):

        self.palette = {
            ("bg",               "black",       "white"),
            ("country",          "black",       "white"),
            ("country_selected", "black",       "yellow"),
            ("footer",           "white, bold", "dark red")
        }

        self.list_view = ListView()
        self.detail_view = DetailView()

        u.connect_signal(self.list_view, 'show_details', self.show_details)

        footer = u.AttrWrap(u.Text(" Q to exit"), "footer") 
        
        col_rows = u.raw_display.Screen().get_cols_rows()
        h = col_rows[0] - 2
                
        f1 = u.Filler(self.list_view, valign='top', height=h)
        f2 = u.Filler(self.detail_view, valign='top')

        c_list = u.LineBox(f1, title="Countries")
        c_details = u.LineBox(f2, title="Country Details")
        
        columns = u.Columns([('weight', 30, c_list), ('weight', 70, c_details)])            

        frame = u.AttrMap(u.Frame(body=columns, footer=footer), 'bg')
        
        self.loop = u.MainLoop(frame, self.palette, unhandled_input=self.unhandled_input)

    def update_data(self):
        
        l = [] # https://databank.worldbank.org/embed/Population-and-GDP-by-Country/id/29c4df41
        l.append({"name":"USA",     "pop":"325,084,756",   "gdp":"$ 19.485 trillion"})
        l.append({"name":"China",   "pop":"1,421,021,791", "gdp":"$ 12.238 trillion"})
        l.append({"name":"Japan",   "pop":"127,502,725",   "gdp":"$ 4.872 trillion"})
        l.append({"name":"Germany", "pop":"82,658,409",    "gdp":"$ 3.693 trillion"})
        l.append({"name":"India",   "pop":"1,338,676,785", "gdp":"$ 2.651 trillion"})
        
        self.list_view.set_data(l)

    def start(self):

        self.update_data()
        self.loop.run()

if __name__ == '__main__':

    app = App()
    app.start()

