""" demonstration of A* routing on a quadtree representation of a 2D map

    (c) Volker Poplawski 2018
"""
from tkinter import *
from PIL import ImageTk, ImageDraw
import mapgen
import quadtree
import astar
import graph


# square map height and width. power of 2. e.g 256, 512, 1024
MAPSIZE = 512


class MainObject:
    def run(self):
        self.mapimage = None
        self.quadtree = None
        self.startpoint = None
        self.drag_startp = False
        
        self._setupgui()
        
        self.root.mainloop()    


    def _setupgui(self):
        self.root = Tk()
        self.root.title("QuadTree A*")

        self.canvas = Canvas(self.root, bg='gray', width=MAPSIZE, height=MAPSIZE)
        self.canvas.pack(side=LEFT)

        self.image_item = self.canvas.create_image((0, 0), anchor=NW)

        rightframe = Frame(self.root)
        rightframe.pack(side=LEFT, fill=Y)

        mapframe = Frame(rightframe, relief=SUNKEN, borderwidth=2)
        mapframe.pack(padx=5, pady=5)
        
        label = Label(mapframe, text="Map", font=("Helvetica", 13))
        label.pack()

        frame1 = Frame(mapframe)
        frame1.pack(fill=X, padx=4)

        kernellbl = Label(frame1, text="Kernel Size")
        kernellbl.pack(side=LEFT, pady=4)

        self.kernelsizevar = StringVar(self.root)
        self.kernelsizevar.set("7*7")
        kernelmenu = OptionMenu(frame1, self.kernelsizevar, "13*13", "11*11", "9*9", "7*7", "5*5", "3*3")
        kernelmenu.pack(fill=X, expand=True)

        frame2 = Frame(mapframe)
        frame2.pack(fill=X, padx=4)
        
        iterslbl = Label(frame2, text="Num Iterations")
        iterslbl.pack(side=LEFT, pady=4)

        var = StringVar(self.root)
        var.set("40")
        self.iterspin = Spinbox(frame2, from_=0, to=100, textvariable=var)
        self.iterspin.pack(expand=True)

        genbtn = Button(mapframe, text="Generate Map", command=self.onButtonGeneratePress)
        genbtn.pack(pady=2)

        qtframe = Frame(rightframe, relief=SUNKEN, borderwidth=2)
        qtframe.pack(fill=X, padx=5, pady=5)
        
        label = Label(qtframe, text="QuadTree", font=("Helvetica", 13))
        label.pack()

        frame1 = Frame(qtframe)
        frame1.pack(fill=X, padx=4)

        label = Label(frame1, text="Depth Limit")
        label.pack(side=LEFT, pady=4)

        var = StringVar(self.root)
        var.set("100")        
        self.limitspin = Spinbox(frame1, from_=2, to=100, textvariable=var)
        self.limitspin.pack(expand=True)
        
        self.qtlabelvar = StringVar()
        label = Label(qtframe, fg='#FF8080', textvariable=self.qtlabelvar)
        label.pack()

        quadtreebtn = Button(qtframe, text="Generate QuadTree", command=self.onButtonQuadTreePress)
        quadtreebtn.pack(pady=2)
        
        astarframe = Frame(rightframe, relief=SUNKEN, borderwidth=2)
        astarframe.pack(fill=X, padx=5, pady=5)
                
        label = Label(astarframe, text="Path", font=("Helvetica", 13))
        label.pack()

        self.pathlabelvar = StringVar()
        label = Label(astarframe, fg='#0000FF', textvariable=self.pathlabelvar)
        label.pack()

        self.astarlabelvar = StringVar()
        label = Label(astarframe, fg='#8080FF', textvariable=self.astarlabelvar)
        label.pack()

        label = Label(rightframe, text="Instructions", font=("Helvetica", 13))
        label.pack()
        label = Label(rightframe, justify=LEFT, text=
        "Generate a random map.\n"
        "Black regions are impassable.\n"
        "Generate QuadTree on map.\n"
        "Set start position by dragging blue circle.\n"
        "Click anywhere on map to find a path.")
        label.pack(padx=14)

        self.canvas.bind('<ButtonPress-1>', self.onMouseButton1Press)
        self.canvas.bind('<ButtonRelease-1>', self.onMouseButton1Release)
        self.canvas.bind('<B1-Motion>', self.onMouseMove)


    def onMouseButton1Press(self, event):
        if not self.quadtree:
            return

        if self.startpoint in self.canvas.find_overlapping(event.x, event.y, event.x, event.y):
            self.drag_startp = True
            return
        
        startx, starty, _, _ = self.canvas.coords(self.startpoint)
        start = self.quadtree.get(startx + 6, starty + 6)
        goal = self.quadtree.get(event.x, event.y)

        adjacent = graph.make_adjacent_function(self.quadtree)
        path, distances, considered = astar.astar(adjacent, graph.euclidian, graph.euclidian, start, goal)

        im = self.qtmapimage.copy()
        draw = ImageDraw.Draw(im)

        self.astarlabelvar.set("Nodes visited: {} considered: {}".format(len(distances), considered))
        for tile in distances:
            fill_tile(draw, tile, color=(0xC0, 0xC0, 0xFF))

        if path:
            self.pathlabelvar.set("Path Cost: {}  Nodes: {}".format(round(distances[goal], 1), len(path)))
            for tile in path:
                fill_tile(draw, tile, color=(0, 0, 255))
        else:
            self.pathlabelvar.set("No Path found.")

        self._updateimage(im)

    
    def onMouseButton1Release(self, event):
        self.drag_startp = False
        
    
    def onMouseMove(self, event):
        if self.drag_startp:
            self.canvas.coords(self.startpoint, event.x-6, event.y-6, event.x+6, event.y+6)
            

    def onButtonGeneratePress(self):
        ksize = int(self.kernelsizevar.get().split('*')[0])
        numiter = int(self.iterspin.get())

        self.root.config(cursor="watch")
        self.root.update()
        self.mapimage = mapgen.generate_map(MAPSIZE, kernelsize=ksize, numiterations=numiter)
        self._updateimage(self.mapimage)
        self.quadtree = None
        self.qtlabelvar.set("") 
        self.canvas.delete(self.startpoint)
        self.startpoint = None
        self.astarlabelvar.set("")
        self.pathlabelvar.set("")
        self.root.config(cursor="")        
        

    def onButtonQuadTreePress(self):
        if not self.mapimage:
            return
        
        depthlimit = int(self.limitspin.get())
        self.quadtree = quadtree.Tile(self.mapimage, limit=depthlimit)
        self.qtmapimage = self.mapimage.copy()
        draw = ImageDraw.Draw(self.qtmapimage)
        draw_quadtree(draw, self.quadtree, 8)
        self._updateimage(self.qtmapimage)
        
        self.qtlabelvar.set("Depth: {}  Nodes: {}".format(self.quadtree.depth(), self.quadtree.count()))
        self.astarlabelvar.set("")
        self.pathlabelvar.set("")
        
        if not self.startpoint:
            pos = MAPSIZE//2
            self.startpoint = self.canvas.create_oval(pos-6, pos-6, pos+6, pos+6, fill='#2028FF', width=2)
        

    def _updateimage(self, image):
        self.imagetk = ImageTk.PhotoImage(image)
        self.canvas.itemconfig(self.image_item, image=self.imagetk)




def draw_quadtree(draw, tile, maxdepth):
    if tile.level == maxdepth:
        draw_tile(draw, tile, color=(255, 110, 110))
        return
    
    if tile.childs:
        for child in tile.childs:
            draw_quadtree(draw, child, maxdepth)
    else:
        draw_tile(draw, tile, color=(255, 110, 110))

    
def draw_tile(draw, tile, color):
    draw.rectangle([tile.bb.x, tile.bb.y, tile.bb.x+tile.bb.w, tile.bb.y+tile.bb.h], outline=color)


def fill_tile(draw, tile, color):
    draw.rectangle([tile.bb.x+1, tile.bb.y+1, tile.bb.x+tile.bb.w-1, tile.bb.y+tile.bb.h-1], outline=None, fill=color)



if __name__ == '__main__':
    o = MainObject()
    o.run()
