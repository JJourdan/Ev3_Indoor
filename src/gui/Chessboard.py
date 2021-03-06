from gui.Area import Area
from gui.Box import Box


class Chessboard:
    '''this class represent the grid display on the GUI and all the box and area'''
    area_id = 0

    def __init__(self, canvas, zoom, width, height, database, interface):
        self.width = width
        self.height = height
        self.canvas = canvas
        self.zoom = zoom
        self.database = database

        self.xpas = 10
        self.ypas = 5
        self.areas_list = self.load_area_list()
        self.boxes = []
        self.load_id_on_connect()
        self.selected_box = None
        self.selected_area = None
        self.area_flag = False
        self.interface = interface
        self.originx = 0
        self.originy = 0
        self.fill_box_list(canvas)
        self.load_cases_list()

    def fill_box_list(self, canvas):
        '''fill the boxes list (@self.boxes) with the width, the height and the step(@self.xpas, self.ypas) '''
        for i in range(0, int(self.width / self.xpas)):
            for j in range(0, int(self.height / self.ypas)):
                self.boxes.append(
                    Box(self.xpas * i, self.ypas * j, self.xpas * i + self.xpas, self.ypas * j + self.ypas, canvas,
                        self))

    def draw_boxes(self):
        '''draw all boxes by calling their own drawing method'''
        for i in self.boxes:
            i.draw_box(self.zoom, self.originx, self.originy, "LightSkyBlue1")

    def show_hide_area(self):
        '''draw the grid if the flag is false, else undraw'''
        if self.area_flag is False:
            self.area_flag = True
            for area in self.areas_list:
                self.areas_list[area].draw_area(self.zoom, self.originx, self.originy)
                self.areas_list[area].draw_boxes(self.zoom, self.originx, self.originy)

        else:
            self.area_flag = False
            if not self.interface.chessboard_flag:
                self.interface.draw_map()
                return
            for area in self.areas_list:
                self.areas_list[area].undraw_boxes(self.zoom, self.originx, self.originy)

    def clear_areas(self):
        '''clear areas on GUI by calling their own undraw method'''
        for area in self.areas_list:
            self.areas_list[area].clear_area()
            self.areas_list[area].undraw_boxes(self.zoom, self.originx, self.originy)
        self.selected_area = None
        self.areas_list = {}


    def draw_all_area(self):
        '''draw all area with with their own drawing method'''
        for area in self.areas_list:
            self.areas_list[area].draw_area(self.zoom, self.originx, self.originy)

    def get_box(self, x, y):
        '''return the box coordinate from the x and y coordinate (in pixel)'''
        nb_cols = int(self.height / self.ypas)
        cols = int((y / self.ypas) / self.zoom)
        rows = int((x / self.xpas) / self.zoom)
        box_number = int(rows * nb_cols + cols)
        return self.boxes[box_number]

    def select_box(self, x, y):
        '''select the box which correspond to x and y and put it on @self.selected_box'''
        ox = x + self.originx
        oy = y + self.originy
        x += self.originx % (self.zoom * self.xpas)
        y += self.originy % (self.zoom * self.ypas)

        if self.selected_box and self.selected_box.get_area() is None:
            self.selected_box.draw_box(self.zoom, self.originx, self.originy, "LightSkyBlue1")
        if self.selected_area is not None and self.area_flag is False:
            self.areas_list[self.selected_area].undraw_boxes(self.zoom, self.originx, self.originy)

        nb_cols = int(self.height / self.ypas)
        cols = int((oy / self.ypas) / self.zoom)
        rows = int((ox / self.xpas) / self.zoom)
        print("case : ", rows, cols)
        box_number = int(rows * nb_cols + cols)
        box = self.boxes[box_number]
        self.selected_box = box
        box.draw_box(self.zoom, self.originx, self.originy, "red")
        area = box.get_area()
        if area is not None:
            self.areas_list[area].draw_boxes(self.zoom, self.originx, self.originy)
            self.selected_area = box.get_area()

    def create_area(self):
        ''' create an area and stock it on @self.areas_list'''
        area = Area(self.canvas)
        box = self.selected_box
        if box is None:
            return
        if box.get_area() is not None:
            return
        area.add_box(box)
        box.asign_area(Chessboard.area_id)
        self.areas_list[Chessboard.area_id] = area
        area.draw_boxes(self.zoom, self.originx, self.originy)
        coord_x, coord_y = self.get_box_coord()
        self.database.add_new_box(coord_x, coord_y, Chessboard.area_id)
        self.selected_area = Chessboard.area_id
        Chessboard.area_id += 1

    def select_area(self, x, y):
        '''select an area and put it on @self.selected_area'''
        box = self.selected_box(x, y)
        return box.get_area()

    def add_box_to_area(self):
        '''add a box on the boxes_list of an area'''
        box = self.selected_box
        if self.selected_area is None:
            return
        if box.get_area() is not None:
            return
        box.asign_area(self.selected_area)
        self.areas_list[self.selected_area].add_box(box)
        self.areas_list[self.selected_area].draw_boxes(self.zoom, self.originx, self.originy)
        coord_x, coord_y = self.get_box_coord()
        self.database.add_new_box(coord_x, coord_y, self.selected_area)

    def remove_box_from_area(self):
        '''remove a box from the boxes_list of an area'''
        box = self.selected_box
        if box.get_area() is None:
            return
        box.asign_area(None)
        self.areas_list[self.selected_area].remove_box(box)
        box.draw_box(self.zoom, self.originx, self.originy, "LightSkyBlue1")
        self.areas_list[self.selected_area].draw_boxes(self.zoom, self.originx, self.originy)
        coord_x, coord_y = self.get_box_coord()
        self.database.delete_area_from_case(coord_x, coord_y)

    def get_box_coord(self):
        '''get pixel coordinate from boxes coordinate'''
        rows = int(self.selected_box.x1/self.xpas)
        cols = int(self.selected_box.y1/self.ypas)
        print("avant insert : ", rows, cols, "x1 et y1 : ", self.selected_box.x1, self.selected_box.y1)
        return rows, cols

    def load_id_on_connect(self):
        '''load the area id from the database when the program is launch'''
        Chessboard.area_id = self.database.load_id_area()
        if Chessboard.area_id is None:
            Chessboard.area_id = 0
        else:
            Chessboard.area_id = Chessboard.area_id + 1

    def load_cases_list(self):
        '''load boxes_list from the database when the program is launch'''
        cmd = self.database.load_cases()
        for i in cmd:
            x1 = i[0] * self.zoom * self.xpas
            y1 = i[1] * self.zoom * self.ypas
            nb_cols = int(self.height / self.ypas)
            print("numb : ", i[0], i[1], i[0] * nb_cols + i[1])
            box = self.boxes[i[0] * nb_cols + i[1]]
            if i[2] != -1:
                box.asign_area(i[2])
                self.areas_list[i[2]].add_box(box)

    def load_area_list(self):
        '''load the area list from the database when the program is launch'''
        lst = self.database.load_areas()
        dico = {}
        for l in lst:
            a = Area(self.canvas)
            dico[int(l)] = a
        return dico



