# -*- coding: utf-8 -*-
import os, sys, math, Image, ImageChops
import numpy as np

path = os.path.realpath(os.path.dirname(sys.argv[0]))
rng = 30

def autocrop(im, bgcolor):
    bg = Image.new(im.mode, im.size, bgcolor)
    diff = ImageChops.difference(im, bg)
    bbox = diff.getbbox()
    print "bbox",bbox
    if bbox: return im.crop(bbox) # cropped
    else: return im # no contents
    
def color_range(color1,color2):
    R1,G1,B1,A1 = color1
    R2,G2,B2,A2 = color2
    return math.sqrt((R1-R2)**2 + (G1-G2)**2 + (B1-B2)**2)

    
for fname in os.listdir(path):
    if fname.lower().endswith(('.bmp','.jpg','.png')):
        outfile = fname[:-4] + "_.png"
        im = Image.open(fname)
        print "Old: %s - %dx%d"%(fname,im.size[0],im.size[1])
        print "pixel:", im.getpixel((0,0))
        im = autocrop(im,im.getpixel((0,0)))
        im.save("outfile.jpg")
        sys.exit(1)
        #convert to png
        im = im.convert('RGBA')
        
        source = im.split()
        colorkey = im.getpixel((0,0))
        size = im.size
        
        mask = Image.new("RGBA", (im.size[0], im.size[1]), (0,0,0,0))
        
        #vp = np.zeros((1000, 1000)) #visited pixels
        vp = np.zeros((im.size[0], im.size[1])) #visited pixels
        # im = np.asarray(im) #image to array
        # mask = np.asarray(mask) #mask image array
        # mask.flags.writeable = True #check off read-only flag
        # colorkey = im[0][0]
        
        # print mask[0][0]
        # print mask[0][0][3]
        
        # mask[0][0][3] = 5
        # print mask[0][0][3]
        # break
        
        stack = [(0,0,0),(size[0]-1,0,0),(size[0]/2,0,0)] # x - y - color range
        while len(stack) > 0:
            point = stack.pop(0)
            for x in [-1,0,1]:
                for y in [-1,0,1]:
                    if x == 0 and y==0: continue
                    _x_ , _y_ = x+point[0],y+point[1]
                    if abs(_x_)>=size[0] or abs(_y_)>=size[1]: continue
                    if _x_ < 0 or _y_ < 0 : continue
                    if vp[_x_][_y_] == 0:
                        try:
                            r = color_range(colorkey,im.getpixel((_x_,_y_)))
                        except IndexError:
                            print point[0],point[1],_x_,_y_
                            exit(1)
                        if r < rng:
                            stack.append((_x_,_y_,r))
                            vp[_x_][_y_] = 1 #pixel visited
                        else:
                            vp[_x_][_y_] = 1 #this pixel - probably image
            # print len(stack)
            # clr = im[x,y]
            clr = im.getpixel((point[0],point[1]))
            diff = int((rng-(rng-point[2]))*(255/rng))
            R = clr[0]*clr[3] + 255*(255-clr[3])
            G = clr[1]*clr[3] + 255*(255-clr[3])
            B = clr[2]*clr[3] + 255*(255-clr[3])
            mask.putpixel((point[0],point[1]),(R,G,B,255-diff))
            # for index,value in enumerate([R,G,B,255-diff]): mask[point[0],point[1],index] = value 
        
          
        # for x in xrange(size[1]):
            # for y in xrange(size[0]):
                # r = color_range(im[x][y],im[0][0])
                # if r < rng:
                    # for index,value in enumerate([0,0,0,254]): mask[x,y,index] = value   
                # else:
                    # for index,value in enumerate([254,254,254,0]): mask[x,y,index] = value   
        
        # for x in xrange(im.size[0]):
            # for y in xrange(im.size[1]):
                # r = color_range(im.getpixel((x,y)),colorkey)
                # if r <= rng:
                    # clr = im.getpixel((x,y))
                    # diff = int((rng-(rng-r))*(255/rng))
                    # R = clr[0]*clr[3] + 255*(255-clr[3])
                    # G = clr[1]*clr[3] + 255*(255-clr[3])
                    # B = clr[2]*clr[3] + 255*(255-clr[3])
                    # mask.putpixel((x,y),(R,G,B,255-diff))
                # else:
                    # mask.putpixel((x,y),(255,255,255,0))
        
        # mask = Image.fromarray(mask) 
        # im = Image.fromarray(im)
        mask.save("mask.png")
        sys.exit(1)
        # process the alpha band fully transparent
        out = source[3].point(lambda i: i * 0.0)
        # paste the processed band back, but only to selected pixels
        source[3].paste(out, None, mask)
        # build a new multiband image
        im = Image.merge(im.mode, source)
        
        # path = os.path.split(os.path.realpath(outfile))
        # outfile = os.path.join(path[0],"converted",path[1])
        
        # if os.path.exists(os.path.join(path[0],"converted")):
            # im.save(outfile)
        # else:
            # #get dir name
            # path = os.path.realpath(outfile)
            # dir = os.path.split(path)[0]
            # if not os.path.exists(dir):
                # os.makedirs(dir)
            # im.save(outfile)
        # print "New: %s - %dx%d"%(fname,im.size[0],im.size[1])
        im.save(outfile)
print "Done"    