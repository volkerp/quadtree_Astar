""" quadtree on 2D image

    (c) Volker Poplawski 2018
"""
from mapgen import IMPASSABLE, PASSABLE


##############
## UL ## UR ##
##############
## LL ## LR ##
##############
UL = 0
UR = 1
LL = 2
LR = 3


class BoundingBox:
    """
    Simple bounding box implementation
    """
    def __init__(self, x, y, w, h):
        self.x = x
        self.y = y
        self.w = w
        self.h = h
            
    def intersects(self, o):
        return (self.x < o.x + o.w and self.y < o.y + o.h and
               self.x + self.w > o.x and self.y + self.h > o.y)
    
    
    def contains(self, x, y):
        return (self.x < x < self.x + self.w and
               self.y < y < self.y + self.h)


    def center(self):
        return self.x + self.w//2, self.y + self.h//2





class Tile:
    """
    QuadTree on 2D image map
    
    Recursive data structure. Class serves as the root quadtree, subtrees and leaf Tiles.
    A Tile has either exactly four child Tiles or no child Tiles.
    Tiles with no child Tiles are leaf Tiles and have a uniform color.
    """
    def __init__(self, image, pos = UL, level = 0, x = 0, y = 0, limit = None):
        self.level = level
        self.bb = BoundingBox(x, y, image.width, image.height)
        self.childs = None      # either a tile has four child tiles
        self.color = None       # or a final color value
        
        self._setimage(image, limit)


    def center(self):
        return self.bb.center()


    def depth(self):
        """
        Depth of quadtree/subtree
        """
        if not self.childs:
            return self.level
        else:
            return max((child.depth() for child in self.childs))
        
        
    def count(self, cnt = 0):
        """
        Number of tiles in quadtree/subtree
        """
        if not self.childs:
            return 1
        else:
            return 1 + sum((child.count() for child in self.childs))
        

    def get(self, x, y):
        """
        Get leaf Tile containing position x,y from quadtree/subtree
        """
        if not self.childs:
            return self
        else:
            s = self.bb.w // 2
            if x < self.bb.x + s:
                if y < self.bb.y + s:
                    return self.childs[UL].get(x, y)
                else:
                    return self.childs[LL].get(x, y)
            else:
                if y < self.bb.y + s:
                    return self.childs[UR].get(x, y)
                else:
                    return self.childs[LR].get(x, y)
                

    def intersect(self, bbox, retlist):
        """
        Intersect quadtree/subtree with BoundingBox
        return list of intersecting i.e. overlapping leaf Tiles
        """ 
        if not self.bb.intersects(bbox):
            return retlist
        
        if not self.childs:
            return retlist.append(self)
        else:
            self.childs[UL].intersect(bbox, retlist)
            self.childs[UR].intersect(bbox, retlist)
            self.childs[LL].intersect(bbox, retlist)
            self.childs[LR].intersect(bbox, retlist)
                
        
    def _setimage(self, image, limit):
        if len(image.getcolors()) == 1:
            # image is uniformly colored
            # Tile is a leaf Tile i.e. no childs 
            # recursion ends here. color is the uniform color of the image
            self.color = image.getcolors()[0][1]
        else:            
            # image is not uniformly colored i.e. has more than one color 
            if limit and self.level >= limit:
                # depth limit is given and Tile is at limit
                # forces a leaf Tile
                # end recursion here and (arbitrary) set color of Tile
                self.color = PASSABLE
            else:
                # not a leaf Tile
                # split Tile and do recursion on childs
                self._split(image, limit)


    
    def _split(self, image, limit):
        # split Tile into four child tiles
        self.childs = [None, None, None, None]
        # split image at half height and width to create four subimages
        # create four quadtrees as childs
        s = image.height // 2
        self.childs[UL] = Tile(image.crop((0, 0, 0+s, 0+s)), UL, self.level+1, self.bb.x + 0, self.bb.y + 0, limit)
        self.childs[UR] = Tile(image.crop((s, 0, s+s, 0+s)), UR, self.level+1, self.bb.x + s, self.bb.y + 0, limit)
        self.childs[LL] = Tile(image.crop((0, s, 0+s, s+s)), LL, self.level+1, self.bb.x + 0, self.bb.y + s, limit)
        self.childs[LR] = Tile(image.crop((s, s, s+s, s+s)), LR, self.level+1, self.bb.x + s, self.bb.y + s, limit)


    def __repr__(self):
        return "l:{} {},{} {}:{}".format(self.level, self.bb.x, self.bb.y, self.bb.w, self.bb.h)












