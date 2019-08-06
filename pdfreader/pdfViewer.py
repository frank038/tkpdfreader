#!/usr/bin/env python3
# v. 0.1
import sys
import fitz

# version and compilation date of PyMuPDF
fitz_ver = fitz.__doc__
print(fitz_ver)

if not list(map(int, fitz.VersionBind.split("."))) >= [1, 14, 19]:
    raise SystemExit("need PyMuPDF v1.14.19 for this script")

import os
import tkinter as tk
import tkinter.ttk as ttk
from tkinter import font
from operator import itemgetter
from itertools import groupby
from tkfilebrowser import askopendirname, askopenfilename
from tkinter import messagebox
import time


# this program width and height
app_width = 0
app_height = 0

try:
    with open("config.cfg", "r") as f:
        owidth = f.readline().strip()
        if owidth and int(owidth) > 100:
            app_width = int(owidth)
        else:
            app_width = 1300
        oheight = f.readline().strip()
        if oheight and int(oheight) > 100:
            app_height = int(oheight)
        else:
            app_height = 900
except:
    pass

# font size of the application
font_size = 18

##
annot_widg = 0


class Application(ttk.Frame):
    def __init__(self, master=None):
        super().__init__(master)
        self.master = master
        
        self.pack(fill="both", expand=True)
        self.master.update_idletasks()
        
        
        # style
        self.s = ttk.Style()
        self.s.theme_use("clam")

        # font family and size
        self.s.configure('.', font=('', font_size))

        self.rowconfigure(2, weight=1)
        self.columnconfigure(2, weight=1)
        
        # treeview: row height
        ffont = font.Font(family='', size=font_size)
        self.tv_row_height = ffont.metrics("linespace")
        
        self.create_widgets()
        
    def create_widgets(self):
        ###
        # the zoom
        self.zoom = 2
        # canvas object list
        self.canvas_list = []
        # ref to pix
        self.pix = None
        
        ######### TOOLBAR
        self.toolb_frame = ttk.Frame(self)
        self.toolb_frame.grid(column=0, row=1, columnspan=3, sticky="w")
        
        ### BUTTONS
        # show/hide the toc
        self.menu_image = tk.PhotoImage(file="icons/menu2.png")
        self.toc_btn = ttk.Button(self.toolb_frame, image=self.menu_image, width=-1, command=self.fhidetoc)
        self.toc_btn.grid(row=0, column=0, sticky="w")
        # load a new file
        self.open_image = tk.PhotoImage(file="icons/open2.png")
        self.open_btn = ttk.Button(self.toolb_frame, image=self.open_image, width=-1, command=self.chooseFile)
        self.open_btn.grid(column=1, row=0, sticky="w")
        # page-
        self.minus_image = tk.PhotoImage(file="icons/minus.png")
        self.minus_btn = ttk.Button(self.toolb_frame, image=self.minus_image, width=-1, command=self.fminus)
        self.minus_btn.grid(column=2, row=0, sticky="w")
        # label for page
        self.page_lbl = ttk.Label(self.toolb_frame, text="Page: 0", width=-1)#, relief="sunken")
        self.page_lbl.grid(row=0, column=3)
        # page+
        self.plus_image = tk.PhotoImage(file="icons/plus.png")
        self.plus_btn = ttk.Button(self.toolb_frame, image=self.plus_image, width=-1, command=self.fplus)
        self.plus_btn.grid(column=4, row=0, sticky="w")
        # zoom+
        self.zoomp_btn = ttk.Button(self.toolb_frame, image=self.plus_image, width=-1, command=self.fzoomp)
        self.zoomp_btn.grid(column=5, row=0, sticky="w")
        # label for zoom
        self.zoom_lbl = ttk.Label(self.toolb_frame, text="Zoom: 0", width=-1)#, relief="sunken")
        self.zoom_lbl.grid(row=0, column=6)
        # zoom-
        self.zoomm_btn = ttk.Button(self.toolb_frame, image=self.minus_image, width=-1, command=self.fzoomm)
        self.zoomm_btn.grid(column=7, row=0, sticky="w")
        # rotate left
        self.left_image = tk.PhotoImage(file="icons/left.png")
        self.left_btn = ttk.Button(self.toolb_frame, image=self.left_image, width=-1, command=self.fleft)
        self.left_btn.grid(column=8, row=0, sticky="w")
        # rotate right
        self.right_image = tk.PhotoImage(file="icons/right.png")
        self.right_btn = ttk.Button(self.toolb_frame, image=self.right_image, width=-1, command=self.fright)
        self.right_btn.grid(column=9, row=0, sticky="w")
        # search for texts
        self.search_image = tk.PhotoImage(file="icons/search.png")
        self.search_btn = ttk.Button(self.toolb_frame, image=self.search_image, width=-1, command=self.fsearch)
        self.search_btn.grid(column=10, row=0, sticky="w")
        # print/save button
        self.print_image = tk.PhotoImage(file="icons/print.png")
        self.print_btn = ttk.Button(self.toolb_frame, image=self.print_image, width=-1, command=self.fprint)
        self.print_btn.grid(column=11, row=0, sticky="w")
        # metadata
        self.metadata_image = tk.PhotoImage(file="icons/pdf.png")
        self.metadata_btn = ttk.Button(self.toolb_frame, image=self.metadata_image, width=-1, command=self.fmetadata)
        self.metadata_btn.grid(column=12, row=0, sticky="w")
        # annot
        self.annotf_image = tk.PhotoImage(file="icons/annotations.png")
        self.annot_mb = tk.Menubutton(self.toolb_frame, image=self.annotf_image)#, command=self.fannot_menu)#, relief=tk.RAISED)
        self.annot_mb.grid(column=13, row=0, sticky="w")
        self.annot_mb.menu = tk.Menu(self.annot_mb, tearoff=0)
        self.annot_mb["menu"] = self.annot_mb.menu
        # text annot
        self.annot_mb.menu.add_command(label=" Text", font=("", font_size), image=self.annotf_image, compound=tk.LEFT, command=lambda:self.fannot(0))
        # freetext annot
        # highlight annot
        self.annot_mb.menu.add_command(label=" Highlight", font=("", font_size), image=self.annotf_image, compound=tk.LEFT, command=lambda:self.fannot(8))
        # rect annot
        self.annot_mb.menu.add_command(label=" Rectangle", font=("", font_size), image=self.annotf_image, compound=tk.LEFT, command=lambda:self.fannot(4))
        # free text annot
        self.annot_mb.menu.add_command(label=" Free text", font=("", font_size), image=self.annotf_image, compound=tk.LEFT, command=lambda:self.fannot(2))
        # embed files
        self.embed_image = tk.PhotoImage(file="icons/embed.png")
        self.embed_btn = ttk.Button(self.toolb_frame, image=self.embed_image, width=-1, command=self.fembed)
        
        # button quit
        self.quit_image = tk.PhotoImage(file="icons/quit.png")
        quit_btn = ttk.Button(self, image=self.quit_image, width=-1, command=quit)
        quit_btn.grid(row=1, column=3, sticky="w")
        
        ### TOC
        # 0 show - 1 hide
        self.tocHide = 0
        # frame for treeview e scrollbar 
        self.tv_frame = ttk.Frame(self)
        self.tv_frame.grid(column=0, row=2, sticky="nw")
        # fake label needed to properly resize the frame
        self.fake_lbl = ttk.Label(self.tv_frame, text="")
        self.tv = ttk.Treeview(self.tv_frame, selectmode="browse", columns=("Page"), height=60)
        self.tv.pack(side="left", fill="y", expand=True, anchor="nw")
        # column width
        self.tv.column("#0", width=350)
        self.tv.column("Page", width=50)
        # column heading
        self.tv.heading("#0", text="Toc")
        self.tv.heading("Page", text="Page")
        # treeview: each row height - workaround
        self.s.configure('Treeview', rowheight=self.tv_row_height+2)
        #
        # scrollbar 
        self.vscrollbar = ttk.Scrollbar(self.tv_frame, orient="vertical", command=self.tv.yview)
        self.tv.configure(yscrollcommand=self.vscrollbar.set)
        self.vscrollbar.pack(fill="y", expand=True, anchor="nw")
        #
        self.tv.bind("<<TreeviewSelect>>", self.ftv)
        # 
        self.tv.bind("<<TreeviewOpen>>", self.ftvOpen)
        #
        self.tv.bind("<<TreeviewClose>>", self.ftvClose)
        #
        ### canvas gui part
        self.s.configure('new.TFrame', background='gray70')
        self.cframe = ttk.Frame(self, style="new.TFrame")
        self.cframe.grid(column=1, row=2, columnspan=3, sticky="nwes")
        ## canvas
        self.canvas = tk.Canvas(self.cframe, width=0, height=0, scrollregion=(0,0,app_width,app_height), bg='gray70')
        ## scrollbars
        # orizzontal scrollbar
        self.hbar=ttk.Scrollbar(self.cframe, orient=tk.HORIZONTAL)
        self.hbar.pack(side=tk.BOTTOM, fill=tk.X)
        self.hbar.config(command=self.canvas.xview)
        # vertical scrollbar
        self.vbar=ttk.Scrollbar(self.cframe, orient=tk.VERTICAL)
        self.vbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.vbar.config(command=self.canvas.yview)
        #
        self.canvas.pack(side=tk.LEFT, anchor="nw", fill="none")
        self.canvas.config(xscrollcommand=self.hbar.set, yscrollcommand=self.vbar.set)
        ####### canvas rubberband
        self.startx = 0
        self.starty = 0
        self.rubberbandBox = None
        # rubberband coords
        self.x1 = 0
        self.y1 = 0
        self.x2 = 0
        self.y2 = 0
        #
        self.doc = None
        self.page = None
        self.page_count = 0
        # 0 no page - 1 first page - etc.
        self.current_page = 0
        # toc - outline
        self.toc = None
        # degrees of page rotation
        self.rotation = 0
        # the bindings: Ctrl + LMB
        ## for text selection
        self.canvas.bind("<Control-Button-1>", self.mouseDown)
        self.canvas.bind("<Control-Button1-Motion>", self.mouseMotion)
        self.canvas.bind("<Control-Button1-ButtonRelease>", self.mouseUp)
        self.canvas.bind('<Motion>', self.cmotion)
        # the annot info is shown
        self.canvas.bind("<Button-1>", self.cButtonLeft)
        # menu on annotations
        self.canvas.bind("<Button-3>", self.cButtonRight)
        # ancora niente
        self.canvas.bind("<Button1-ButtonRelease>", self.cButtonLeftRelease)
        # mouse wheel canvas scrolling
        self.canvas.bind_all("<Button-4>", self.cmousewheel)
        self.canvas.bind_all("<Button-5>", self.cmousewheel)
        # the canvas scrolls when the mouse moves
        # see also the function cButtonLeft
        self.canvas.bind("<Button1-Motion>", self.cscrolling)
        # next page whith PagDown 
        self.canvas.bind_all("<Next>", lambda event:self.fplus())
        # previous page whith PagUp
        self.canvas.bind_all("<Prior>", lambda event:self.fminus())
        ## scrolling with the four arrow keys
        self.canvas.bind_all("<Down>", self.farrows)
        self.canvas.bind_all("<Up>", self.farrows)
        self.canvas.bind_all("<Left>", self.farrows)
        self.canvas.bind_all("<Right>", self.farrows)
        #
        # a label at bottom that indicates the link info
        self.label_link_var = tk.StringVar()
        self.label_link = ttk.Label(self, textvariable=self.label_link_var, font=("",int(font_size-2)))
        self.label_link.grid(column=1, row=3, columnspan=2, sticky="w")
        ### the size grip
        self.sizegrip = ttk.Sizegrip(self)
        self.sizegrip.grid(column=3, row=3, sticky="nwes")
        self.sizegrip.bind("<Button1-ButtonRelease>", self.fsizegrip)
        #################
        # filename
        self.filename = ""
        # the password if the file is encrypted
        self.password = ""
        
        # filename required
        if len(sys.argv) > 1:
            if sys.argv[1]:
                print("File to open:", sys.argv[1])
                self.filename = sys.argv[1]
        else:
            messagebox.showerror("Error", "File required.")
            sys.exit()
        # list of annots: type, content, rect 
        self.annot_list = []
        # needed when the highlight annot is choose from the menu
        # if 1 the use of the clipboard is disabled
        self.annot_hl = 0
        # the coords of the selected text
        self.selected_coords = None
        # list of point for the polygon annot
        self.annot_points = []
        # list of entries
        self.list_id = []
        # list of list of links info: type, rect, page or uri
        self.rect_link_list = []
        # this variable let user go to the page if the link is selected
        self.link_selected = 0
        #
        # load the file
        self.getDoc(self.filename)
        #
        # fill canvas
        self.fcanvas()
        # hide the outline at loading time
        self.fhidetoc()

    # scrolling in both direction with the arrow keys
    def farrows(self, event):
        if event.keysym == "Down":
            self.canvas.yview_scroll(1, "units")
        elif event.keysym == "Up":
            self.canvas.yview_scroll(-1, "units")
        elif event.keysym == "Left":
            self.canvas.xview_scroll(-1, "units")
        elif event.keysym == "Right":
            self.canvas.xview_scroll(1, "units")   
    
    # page scrolled up or down
    def cmousewheel(self, event):
        #time.sleep(0.01)
        if event.num == 4:
            self.canvas.yview_scroll(-1, "units")
        elif event.num == 5:
            self.canvas.yview_scroll(1, "units")
        
    # the pointer moves inside the canvas
    def cmotion(self, event):
        cx = self.canvas.canvasx(event.x)/self.zoom
        cy = self.canvas.canvasy(event.y)/self.zoom
        # only if the page has not been rotated
        if abs(self.rotation) == 0:
            point = fitz.Point(cx, cy)
            if self.rect_link_list:
                for item in self.rect_link_list:
                    prect = item[1]
                    if point in prect:
                       # if goto type
                       if item[0] == 1:
                           ll = "Go to page: "+str(item[2])
                           self.label_link_var.set(ll)
                           # this variable let user go to the page if the link is selected
                           self.link_selected = item[2]
                           break
                       elif item[0] == 2:
                           ll = "External Link: "+item[2]
                           self.label_link_var.set(ll)
                           break
                    # 
                    else:
                       # reset the variable
                       self.link_selected = 0
                       # reset the label
                       self.label_link_var.set("")
                       continue
               
    
    # set the canvas binds and cursor
    def fannot(self, atype):
        # only if the page has not been rotated
        if abs(self.rotation) == 0:
            # text (pop up style)
            if atype == 0:
                # canvas bind: LMB
                self.canvas.unbind("<Button-1>")
                self.canvas.unbind("<Button1-ButtonRelease>")
                self.canvas.unbind("<Button-3>")
                self.canvas.bind("<Button-1>", lambda event,a=atype: self.fannotf(event, a))
                self.canvas.bind("<Button1-ButtonRelease>", self.fannotff)
                # RMB to invalid the choise
                self.canvas.bind("<Button-3>", self.fannotff)
                # change the cursor
                self.master.config(cursor='clock red red')
            # rect annot
            elif atype == 4 or atype == 2:
                ## unbind functions
                self.canvas.unbind("<Button-1>")
                self.canvas.unbind("<Button1-ButtonRelease>")
                self.canvas.unbind("<Button-3>")
                ## new binds
                # a point is added
                self.canvas.bind("<Button1-ButtonRelease>", lambda event,x=atype:self.fannot_p(event, x))#self.fannotff)
                # RMB to invalid the choise
                self.canvas.bind("<Button-3>", self.fannotff)
                # change the cursor
                self.master.config(cursor='clock red red')
            # highlight annot
            elif atype == 8:
                # if 1 the use of the clipboard is disabled
                # the function getText will not save the selection
                # to clipboard, it will call fannotfe instead
                self.annot_hl = 1
                
        
    # add annot type 0
    def fannotf(self, event, atype):
        if atype == 0:
            cx = self.canvas.canvasx(event.x)/self.zoom
            cy = self.canvas.canvasy(event.y)/self.zoom
            #
            d = MyDialogAnnot(self.master)
            self.master.wait_window(d.top)
            if d.ttext != "-1":
                rect = fitz.Rect(int(cx), int(cy), int(cx)+50, int(cy)+50)
                #
                try:
                    info = {'content': '', 'name': '', 'title': '', 'creationDate': '', 'modDate': '', 'subject': ''}
                    info['name'] = d.ttext[0]
                    info['content'] = d.ttext[1]
                    info['title'] = d.ttext[2]
                    info['creationDate'] = d.ttext[3]
                    info['modDate'] = d.ttext[4]
                    info['subject'] = d.ttext[5]
                    annot = self.page.addTextAnnot(rect.tl, "")

                    annot.setInfo(info)
                    annot.update()
                except Exception as E:
                    messagebox("Error", str(E))
                    return
            else:
                return
        
        ### save and reload the doc
        try:
            #
            self.doc.save(filename=self.filename, incremental=True)
            # empty the list
            self.annot_list = []
            ## document reloaded
            # current page to reload
            current_page = self.current_page
            # empty canvas
            self.fdelete()
            # close the old doc
            if self.doc:
                self.doc.close()
            # reload the doc
            self.getDoc(self.filename)
            #
            self.fcanvas()
            # set the page
            self.page = self.doc.loadPage(current_page-1)
            self.current_page = current_page
        except Exception as E:
            messagebox("Error", str(E))
            return

    # LMB is clicked to collect points
    def fannot_p(self, event, atype):
        
        cx = self.canvas.canvasx(event.x)/self.zoom
        cy = self.canvas.canvasy(event.y)/self.zoom
        #
        # in the list
        self.annot_points.append(cx)
        self.annot_points.append(cy)
        # two points are enough
        if len(self.annot_points) == 4:
            # recalculate the point in the correct coordinates
            # x0 and y0 must always be lesser than x1 and y1
            a0 = self.annot_points[0]
            b0 = self.annot_points[1]
            a1 = self.annot_points[2]
            b1 = self.annot_points[3]
            
            x0 = min(a0,a1)
            y0 = min(b0,b1)
            x1 = max(a0,a1)
            y1 = max(b0,b1)
            
            self.annot_points = []
            self.annot_points.append(x0)
            self.annot_points.append(y0)
            self.annot_points.append(x1)
            self.annot_points.append(y1)
            
            # draw the annot
            self.fannot_d(atype)
    
    # draw the rect annot in the page
    def fannot_d(self, atype):
        # unbind the new bind
        self.canvas.unbind("<Button1-ButtonRelease>")
        self.canvas.unbind("<Button-3>")
        # rebind the old ones
        self.canvas.bind("<Button-1>", self.cButtonLeft)
        self.canvas.bind("<Control-Button1-ButtonRelease>", self.mouseUp)
        self.canvas.bind("<Button-3>", self.cButtonRight)
        # restore the cursor
        self.master.config(cursor='')
        
        # rect type
        if atype == 4:
            # draw the annot rect
            try:
                rect = fitz.Rect(self.annot_points[0],self.annot_points[1],self.annot_points[2],self.annot_points[3])
                annot = self.page.addRectAnnot(rect)
                blue   = (0, 0, 1)
                border = {"width": 4.0, "dashes": [1]}
                annot.setBorder(border)
                colors = {"stroke": blue, "fill": ''}
                annot.setColors(colors)
                annot.setLineEnds(fitz.ANNOT_LE_ClosedArrow, fitz.ANNOT_LE_RClosedArrow)
                # reset the list
                self.annot_points = []
                
                ## the info
                d = MyDialogAnnot(self.master)
                self.master.wait_window(d.top)
                if d.ttext != "-1":
                    #
                    info = {'content': '', 'name': '', 'title': '', 'creationDate': '', 'modDate': '', 'subject': ''}
                    info['name'] = d.ttext[0]
                    info['content'] = d.ttext[1]
                    info['title'] = d.ttext[2]
                    info['creationDate'] = d.ttext[3]
                    info['modDate'] = d.ttext[4]
                    info['subject'] = d.ttext[5]
                    #
                    annot.setInfo(info)
                    #
                    annot.update()
                else:
                    return
            except Exception as E:
                messagebox("Error", str(E))
                return
        # freetext type
        elif atype == 2:
            # draw the annot
            try:
                rect = fitz.Rect(self.annot_points[0],self.annot_points[1],self.annot_points[2],self.annot_points[3])
                
                annot = self.page.addFreetextAnnot(rect, "")
                red    = (1, 0, 0)
                blue   = (0, 0, 1)
                gold   = (1, 1, 0)
                border = {"width": 1.0}
                annot.setBorder(border)

                # reset the list
                self.annot_points = []
                
                ## the info
                d = MyDialogAnnot(self.master)
                self.master.wait_window(d.top)
                if d.ttext != "-1":
                    #
                    info = {'content': '', 'name': '', 'title': '', 'creationDate': '', 'modDate': '', 'subject': ''}
                    info['name'] = d.ttext[0]
                    info['content'] = d.ttext[1]
                    info['title'] = d.ttext[2]
                    info['creationDate'] = d.ttext[3]
                    info['modDate'] = d.ttext[4]
                    info['subject'] = d.ttext[5]
                    #
                    annot.setInfo(info)
                    #
                    annot.update(fontsize = 10, border_color=red, fill_color=gold, text_color=blue)
                else:
                    return
            except Exception as E:
                messagebox("Error", str(E))
                return
        
        ### save and reload the doc
        try:
            #
            self.doc.save(filename=self.filename, incremental=True)
            # empty the lista
            self.annot_list = []
            ## document reloaded
            # current page to reload
            current_page = self.current_page
            # empty canvas
            self.fdelete()
            # close the old doc
            if self.doc:
                self.doc.close()
            # reload the doc
            self.getDoc(self.filename)
            #
            self.fcanvas()
            # set the page
            self.page = self.doc.loadPage(current_page-1)
            self.current_page = current_page
        except Exception as E:
            messagebox("Error", str(E))
            return
   
    # add annot type 8 - CTRL+LMB
    def fannotfe(self):
        
        # get the coords - rect format
        coords = self.selected_coords
        
        # reset
        self.selected_coords = None
        
        try:
            # add the info
            d = MyDialogAnnot(self.master)
            self.master.wait_window(d.top)
            if d.ttext != "-1":
                #
                info = {'content': '', 'name': '', 'title': '', 'creationDate': '', 'modDate': '', 'subject': ''}
                info['name'] = d.ttext[0]
                info['content'] = d.ttext[1]
                info['title'] = d.ttext[2]
                info['creationDate'] = d.ttext[3]
                info['modDate'] = d.ttext[4]
                info['subject'] = d.ttext[5]
                
                annot = self.page.addHighlightAnnot(coords)
                
                annot.setInfo(info)
                annot.update()
            else:
                return
        except Exception as E:
            messagebox("Error", str(E))
            return
        
        ### save and reload the doc
        try:
            #
            self.doc.save(filename=self.filename, incremental=True)
            # empty the lista
            self.annot_list = []
            ## document reloaded
            # current page to reload
            current_page = self.current_page
            # empty canvas
            self.fdelete()
            # close the old doc
            if self.doc:
                self.doc.close()
            # reload the doc
            self.getDoc(self.filename)
            #
            self.fcanvas()
            # set the page
            self.page = self.doc.loadPage(current_page-1)
            self.current_page = current_page
        except Exception as E:
            messagebox("Error", str(E))
            return

    
    # restore the default canvas binds and cursor
    def fannotff(self, event):
        self.canvas.unbind("<Button-1>")
        self.canvas.unbind("<Button-1-ButtonRelease>")
        # bind again
        self.canvas.bind("<Button-1>", self.cButtonLeft)
        self.canvas.bind("<Button-3>", self.cButtonRight)
        # restore the cursor
        self.master.config(cursor='')
        # reset the list of point for the rect and freetext annots
        self.annot_points = []
    
    # LMB released
    def cButtonLeftRelease(self, event):
        pass
    
    # RMB on annotations
    def cButtonRight(self, event):
        # clicked on an annot in the page
        cx = self.canvas.canvasx(event.x)
        cy = self.canvas.canvasy(event.y)
        for item in self.annot_list:
            if item[0][0] in [0,2,3,4,5,6,7,8,9,10,11,12,14]:
                if item[2].x0 < cx/self.zoom < item[2].x1:
                    if item[2].y0 < cy/self.zoom < item[2].y1:
                        # this menu for deleting annot
                        menu = tk.Menu(self.master, tearoff=0, font=("", font_size))
                        menu.add_command(label="Delete", command=lambda :self.fcmd1(cx, cy))
                        menu.tk_popup(event.x_root+5, event.y_root+5)
                        break
            # attachment annot - save the file
            elif item[0][0] == 16:
                # this menu for deleting annot
                menu = tk.Menu(self.master, tearoff=0, font=("", font_size))
                menu.add_command(label="Delete", command=lambda :self.fcmd1(cx, cy))
                menu.add_command(label="Save", command=lambda: self.fsave(item[2]))
                # display the menu
                menu.post(event.x_root+5, event.y_root+5)
                break
              
    # save the attached file
    def fsave(self, item):
        # find the annot
        annot = self.page.firstAnnot
        for iitem in self.annot_list:
            if iitem[2] == item:
                info = annot.info
                try:
                    buff = annot.fileGet()
                    fout = open(info["content"], "wb")
                    fout.write(buff)
                    fout.close()
                except Exception as E:
                    messagebox.showerror("Error", str(E))
                    return
                break
            else:
                annot = annot.next
    
    # delete the selected annotation
    def fcmd1(self, cx, cy):
        if self.annot_list != []:
            i = 0
            # action for any kind of annot in the page
            for item in self.annot_list:
                i += 1
                if item[0][0] in [0,2,3,4,5,6,7,8,9,10,11,12,14,16]:
                    if item[2].x0 < cx/self.zoom < item[2].x1:
                        if item[2].y0 < cy/self.zoom < item[2].y1:
                            annot = self.page.firstAnnot
                            if i == 1:
                                try:
                                    ## delete this annot
                                    self.page.deleteAnnot(annot)
                                    # save the document
                                    self.doc.save(filename=self.filename, incremental=True)
                                except Exception as E:
                                    messagebox("Error", str(E))
                                #########
                            else:
                                # range(i-1) because the first annot is mandatory
                                for ii in range(i-1):
                                    annot = annot.next
                                ###########
                                try:
                                    ## delete this annot
                                    self.page.deleteAnnot(annot)
                                    # save the document
                                    self.doc.save(filename=self.filename, incremental=True)
                                except Exception as E:
                                    messagebox("Error", str(E))
                                #########
        
            ## must reparser the annotations
            # empty the lista
            self.annot_list = []
            
            ### document reloaded
            # current page to reload
            current_page = self.current_page
            # empty canvas
            self.fdelete()
            # close the old doc
            if self.doc:
                self.doc.close()
            # reload the doc
            self.getDoc(self.filename)
            #
            self.fcanvas()
            # set the page
            self.page = self.doc.loadPage(current_page-1)
            self.current_page = current_page
    
    # the canvas scrolls at mouse pointer movement
    def cscrolling(self, event):
        self.canvas.scan_dragto(event.x, event.y, gain=1)
        
    # LMB on annotiations
    def cButtonLeft(self, event):
        # canvas scrolling with LMB
        self.canvas.scan_mark(event.x, event.y)
        
        # only if the page has not been rotated
        if abs(self.rotation) == 0:
            # go to the selected link if type 1
            if self.link_selected != 0:
                new_page = self.link_selected
                # if can be reached
                if new_page < self.page_count:
                    self.fdelete()
                    # 
                    self.current_page = new_page+1
                    self.page = self.doc.loadPage(self.current_page-1)
                    #
                    self.fcanvas()
                    # reset the variable
                    self.link_selected = 0
            
            global annot_widg
            if annot_widg == 0:
                # in term of canvas position
                cx = self.canvas.canvasx(event.x)
                cy = self.canvas.canvasy(event.y)
                # 
                # ANNOT
                # if an annot is found
                if self.annot_list != []:
                    # action for any kind of annot in the page
                    for item in self.annot_list:
                        # if type (0, 'Text') or (2, 'FreeText')
                        if item[0][0] in [0,2,3,4,5,6,7,8,9,10,11,12,14]:
                            if item[2].x0 < cx/self.zoom < item[2].x1:
                                if item[2].y0 < cy/self.zoom < item[2].y1:
                                    ww = annotWindow(self.master, item, [self.master.winfo_pointerx()+20, self.master.winfo_pointery()+20])
                                    #
                                    annot_widg = 1
                                    break
        
    # the outline
    def popToc(self, id):
        # empty the treeview
        self.list_id = []
        self.tv.delete(*self.tv.get_children())
        
        # if there is an outline
        if self.toc:
            #
            for item in self.toc:
                #
                idx = item[0]
                
                if idx == 1:
                    # empty the list
                    self.list_id = []
                    id = self.tv.insert("", "end", text=item[1], values=(item[2]))
                    # add id to the lista
                    self.list_id.append(id)
                elif idx > 1:
                    while len(self.list_id) >= idx:
                        self.list_id.pop()
                    # index of the graiter element
                    if idx > len(self.list_id):
                        id = self.tv.insert(self.list_id[idx-2], "end", text=item[1], values=(item[2]))
                        # add id to the list
                        self.list_id.append(id)
                    # index of the lesser element
                    elif idx < len(self.list_id):
                        # remove the last
                        self.list_id.pop()
                        #
                        id = self.tv.insert(self.list_id[idx-2], "end", text=item[1], values=(item[2]))
                        # add id to the list
                        self.list_id.append(id)
        else:
            # fille the treeview with the refs to the pages
            for n in range(self.page_count):
                self.tv.insert("", "end", text="Page", values=(n+1))
             
    # hide the outline
    def fhidetoc(self):
        
        if self.tocHide == 0:
            # remove the widgets
            self.tv.pack_forget()
            self.vscrollbar.pack_forget()
            # add the fake label
            self.fake_lbl.pack()
            self.tocHide = 1
        else:
            # remove the fake label
            self.fake_lbl.pack_forget()
            # add the widgets
            self.tv.pack(side="left", fill="y", expand=True, anchor="nw")
            self.vscrollbar.pack(fill="y", expand=True, anchor="nw")
            self.tocHide = 0
    
    # printing
    def fprint(self):
        self.doc.save(filename="pdfViewer_file_saved.pdf")
    
    # perform a searching on the whole document
    def fsearch(self):
        
        areas = self.page.searchFor("of", hit_max=4)
        
        for ar in areas:
            self.canvas.create_rectangle(ar[0]*self.zoom, ar[1]*self.zoom, ar[2]*self.zoom, ar[3]*self.zoom)#, fill="red")
        
    
    # element selected in treeview
    def ftv(self, event):
        try:
            item = self.tv.selection()[0]
            # load the page selected
            new_page = int(self.tv.set(item)["Page"])
            # empty canvas
            self.fdelete()
            # set the page 
            self.current_page = new_page
            self.page = self.doc.loadPage(self.current_page-1)
            #
            self.fcanvas()
        except:
            pass
    
    # open the iten in the treeview by clicking on its arrow
    def ftvOpen(self, event):
        # disable the treeview bind temporarily
        self.ftvbind()
    
    # deactivate and reactivate the treeview bind
    def ftvbind(self):
        self.tv.unbind("<<TreeviewSelect>>")
        # after a while it is reactivated
        self.tv.after(100, lambda:self.tv.bind("<<TreeviewSelect>>", self.ftv))
    
    # close the iten in the treeview by clicking on its arrow
    def ftvClose(self, event):
        # disable the treeview bind temporarily
        self.ftvbind()
    
    # empty the treeview
    def ftvempty(self):
        # empty the treeview
        for id in self.tv.get_children():
            for idd in self.tv.get_children(id):
                self.tv.delete(idd)
    
    # load the first page
    def firstPage(self):
        self.current_page = 1
        self.page = self.doc.loadPage(self.current_page-1)
        #
        self.fcanvas()
    
    # load the file
    def getDoc(self, filename):
        # load the file
        try:
            ndoc = fitz.open(filename, filetype="pdf")
        except:
            messagebox.showerror("Error", "Wrong file?")
            #
            if not self.doc:
                sys.exit()
        
        # if a password is required
        if ndoc.isEncrypted:
           d = MyDialog(self.master)
           self.master.wait_window(d.top)
           
           if d.filename != "-1":
               try:
                   ndoc.authenticate(d.filename)
               except Exception as E:
                   messagebox.showerror("Error", str(E))
                   sys.exit()
                   
           else:
               sys.exit()
        
        # the doc
        self.doc = ndoc
        # amount of pages
        self.page_count = len(self.doc)
        
        # get the outline - check if the file is still passworded
        try:
            # toc - outline
            self.toc = self.doc.getToC()
        except:
            self.doc.close()
            messagebox.showerror("Error", "Wrong password")
            self.getDoc(filename)
        
        # load the first page
        self.page = self.doc.loadPage(0)
        self.current_page = 1
        
        # load the outline
        self.popToc("")
        
        ### THE ANNOTATIONS
        # get them
        annot = self.page.firstAnnot
        #
        i = 1
        while annot:
            # get the data
            list = [annot.type, annot.info, annot.rect]
            # fill the list
            self.annot_list.append(list)
            
            annot = annot.next
            i += 1
        # 
        ######## embeded files
        count = self.doc.embeddedFileCount()
        # add the button to the toolbar if any doc embedded
        if count:
            self.embed_btn.grid(column=13, row=0, sticky="w")

        
    # draw a rectangle around each link
    def fshow_links(self):
        # list of list of rectanle and type and page or uri
        self.rect_link_list = []
        for item in self.link_list:
            # if GOTO
            if item["kind"] == 1:
                rect = item["from"]
                
                self.rect_link_list.append([1, rect, item["page"]])
                
                x0 = rect.x0*self.zoom
                y0 = rect.y0*self.zoom
                x1 = rect.x1*self.zoom
                y1 = rect.y1*self.zoom
                
                id = self.canvas.create_rectangle(x0,y0,x1,y1, outline="blue", width=2)
                self.canvas_list.append(id)
            # if URI
            elif item["kind"] == 2:
                
                rect = item["from"]
                
                self.rect_link_list.append([2, rect, item["uri"]])
                
                x0 = rect.x0*self.zoom
                y0 = rect.y0*self.zoom
                x1 = rect.x1*self.zoom
                y1 = rect.y1*self.zoom
                
                id = self.canvas.create_rectangle(x0,y0,x1,y1, outline="red", width=2)
                self.canvas_list.append(id)
    
    # save the embedded file
    def fembed(self):
        # num of embedded files
        count = self.doc.embeddedFileCount()
        
        ## open a new window
        ret = embedWindow(self.master, self.doc)
        
    
    # the canvas
    def fcanvas(self, rot=0):
        # the current page
        self.page_lbl.configure(text="Page: "+str(self.current_page))
        self.zoom_lbl.configure(text="Zoom: "+str(self.zoom))
        
        # zoom - default 2
        self.mat = fitz.Matrix(self.zoom, self.zoom)
        # rotation of 90 degrees to right, -90 to left
        self.mat.preRotate(rot)
        
        # the page to image 
        self.pix = self.page.getPixmap(matrix=self.mat, colorspace=fitz.csRGB, alpha=False)
        self.pix2 = self.pix.getImageData("png")
        
        # get the image
        self.png1 = tk.PhotoImage(data=self.pix2)

        # reconfigure canvas
        self.canvas.configure(width=self.pix.width, height=self.pix.height, scrollregion=(0, 0, self.pix.width, self.pix.height))

        # put the image on canvas
        id = self.canvas.create_image(0, 0, image=self.png1, anchor=tk.NW)
        self.canvas_list.append(id)
        
        # only if the page has not been rotated
        if abs(self.rotation) == 0:
            # get the links in the current page
            link = self.page.getLinks()
            
            if link != []:
                self.link_list = link
                # draw a rectangle around the links
                self.fshow_links()
        
    # choose a file to open
    def chooseFile(self):
        
        filename = askopenfilename(parent=self.master, 
           #initialdir=os.path.expanduser("~"), 
           initialdir="doc",
           initialfile='',
           filetypes=[("PDF", '*.pdf'), ("All files", "*")],
           font_size=font_size)
        
        # if the file
        if filename:
            self.filename = filename
            # close the old doc
            if self.doc:
                self.doc.close()
            self.getDoc(self.filename)
            self.fcanvas()

    # reset canvas
    def fdelete(self):
        for item in self.canvas_list:
            self.canvas.delete(item)
            # empty the list
            self.canvas_list = []

    # load the next page
    def fplus(self):
        # if any
        if self.current_page < self.page_count:
            self.fdelete()
            # next page
            self.current_page += 1
            self.page = self.doc.loadPage(self.current_page-1)
            #
            self.fcanvas()

    # load the previous page
    def fminus(self):
        # if any
        if self.current_page > 1:
            self.fdelete()
            # pagina successiva
            self.current_page -= 1
            self.page = self.doc.loadPage(self.current_page-1)
            #
            self.fcanvas()

    # zoom of +0.5
    def fzoomp(self):
        self.zoom += 0.5
        self.fdelete()
        self.page = self.doc.loadPage(self.current_page-1)
        #
        self.fcanvas()
    
    # zoom of -0.5
    def fzoomm(self):
        if self.zoom > 0.5:
            self.zoom -= 0.5
            self.fdelete()
            self.page = self.doc.loadPage(self.current_page-1)
            #
            self.fcanvas()

    # left page rotation by 90 degrees
    def fleft(self):
        self.rotation -= 90
        self.fdelete()
        self.fcanvas(rot=self.rotation)
    
    # right page rotation by 90 degrees
    def fright(self):
        self.rotation += 90
        self.fdelete()
        self.fcanvas(rot=self.rotation)

    # get the metadata
    def fmetadata(self):
       print("Metadata::", self.doc.metadata)

    # get the text from the selection
    def getText(self, fitz_rect):
        
        rect = fitz_rect
        
        words = self.page.getTextWords()
        
        mywords = [w for w in words if fitz.Rect(w[:4]).intersects(rect)]
        mywords.sort(key=itemgetter(3, 0))
        group = groupby(mywords, key=itemgetter(3))

        selected_text = ""
        for y1, gwords in group:
            selected_text = " ".join(w[4] for w in gwords)
            print(selected_text)

        # if 1 the use of the clipboard is disabled
        if self.annot_hl == 0:
            self.clipboard_clear()
            self.clipboard_append(selected_text)
        # return the text
        elif self.annot_hl == 1:
            # the coords in rect format
            self.selected_coords = rect
            # call the function
            self.fannotfe()
        

    #
    def mouseDown(self, event):
        
        self.x1 = 0
        self.y1 = 0
        self.x2 = 0
        self.y2 = 0
        
        self.startx = self.canvas.canvasx(event.x)
        self.starty = self.canvas.canvasy(event.y)

    #
    def mouseMotion(self, event):
        
        x = self.canvas.canvasx(event.x)
        y = self.canvas.canvasy(event.y)

        if (self.startx != event.x)  and (self.starty != event.y) :
            self.canvas.delete(self.rubberbandBox)
            self.rubberbandBox = self.canvas.create_rectangle(
                self.startx, self.starty, x, y)
            
            self.master.update_idletasks()
        
        ## not lesser than 0 or graiter than the page size
        x1 = min(self.startx,x)
        if x1 < 0:
            x1 = 0
        y1 = min(self.starty,y)
        if y1 < 0:
            y1 = 0
        x2 = max(x,self.startx)
        if x2 > (self.pix.width):
            x2 = (self.pix.width)
        y2 = max(y,self.starty)
        if y2 > self.pix.height:
            y2 = self.pix.height
        
        self.x1 = x1
        self.y1 = y1
        self.x2 = x2
        self.y2 = y2
                
    #
    def mouseUp(self, event):

        self.canvas.delete(self.rubberbandBox)
        # divided by the zoom value
        self.getText(fitz.Rect(self.x1/self.zoom,self.y1/self.zoom,self.x2/self.zoom,self.y2/self.zoom))
        # reset self.annot_hl
        # if 1 the use of the clipboard is disabled
        self.annot_hl = 0

    # store the window size at every user resizing
    def fsizegrip(self, event):
        try:
            f = open("config.cfg", "w")
            f.write(str(self.master.winfo_width())+"\n")
            f.write(str(self.master.winfo_height()))
            f.close()
        except:
            pass

########## DIALOGS ############

# dialog for annots
class annotWindow:
    
    def __init__(self, parent, item, coords):
        self.parent = parent
        self.top = tk.Toplevel(self.parent)
        
        self.item = item
        self.coords = coords
        
        self.top.geometry('+{}+{}'.format(int(self.coords[0]), int(self.coords[1])))
        
        self.text = self.item[1]["content"]
        self.name = self.item[1]["name"]
        self.title = self.item[1]["title"]
        self.creationDate = self.item[1]["creationDate"]
        self.modDate = self.item[1]["modDate"]
        self.subject = self.item[1]["subject"]
        
        lbl_1 = ttk.Label(self.top, text="Name: "+self.name).pack()
        lbl_2 = ttk.Label(self.top, text="Title: "+self.title).pack()
        lbl_3 = ttk.Label(self.top, text="Creation date: "+self.creationDate).pack()
        lbl_4 = ttk.Label(self.top, text="Modification date: "+self.modDate).pack()
        lbl_5 = ttk.Label(self.top, text="Subject: "+self.subject).pack()
        
        self.top.protocol('WM_DELETE_WINDOW', self.wdestroy)
        
        self.wentry = tk.Text(self.top, height=5, width=25, font=("", font_size), wrap=tk.WORD, exportselection=True, state=tk.NORMAL)
        self.wentry.pack()
        self.wentry.insert(tk.END, self.text)
        self.wentry.bind("<ButtonRelease-3>", self.fwentry)
        
        b = ttk.Button(self.top, text="OK", command=self.wdestroy)
        b.pack()
        
    # 
    def fwentry(self, event):
        # if there is a selection
        try:
            # manual selection
            if self.wentry.get(tk.SEL_FIRST, tk.SEL_LAST):
                wmenu = tk.Menu(None, tearoff=0, font=("", font_size))#, takefocus=0)
                wmenu.add_command(label="Copy", command=self.cmd)
                wmenu.entryconfigure(0, state = "normal")
                wmenu.tk_popup(event.x_root+5, event.y_root+5)
        
            ## select all 
                wmenu = tk.Menu(None, tearoff=0, font=("", font_size))#, takefocus=0)
                wmenu.add_command(label="Select all", command=self.cmd2)
                wmenu.entryconfigure(0, state = "normal")#'disabled')
                wmenu.tk_popup(event.x_root+5, event.y_root+5)
        except:
            wmenu = tk.Menu(None, tearoff=0, font=("", font_size))#, takefocus=0)
            wmenu.add_command(label="Select all", command=self.cmd2)
            wmenu.entryconfigure(0, state = "normal")#'disabled')
            wmenu.tk_popup(event.x_root+5, event.y_root+5)
    
    def cmd(self):
        try:
            selected_text = self.wentry.get(tk.SEL_FIRST, tk.SEL_LAST)
            if selected_text:
                # to clipboard 
                self.parent.clipboard_clear()
                self.parent.clipboard_append(selected_text)
        except:
            pass
    
    def cmd2(self):
        try:
            selected_text = self.wentry.get(1.0, tk.END)
            if selected_text:
                # to clipboard 
                self.parent.clipboard_clear()
                self.parent.clipboard_append(selected_text)
        except:
            pass
    
    
    def wdestroy(self):
        global annot_widg
        annot_widg = 0
        self.top.destroy()



# dialog for embedded files
class embedWindow:
    
    def __init__(self, parent, doc):
        self.top = tk.Toplevel(parent)  
        sw = root.winfo_screenwidth()
        sh = root.winfo_screenheight()
        x = (sw / 2) - (app_width / 2)  
        y = (sh / 2) - (app_height / 2)
        self.top.geometry('+{}+{}'.format(int(x), int(y)))
        
        
        self.parent = parent
        self.doc = doc
        
        # num of embedded files
        count = self.doc.embeddedFileCount()
        
        label = ttk.Label(self.top, text="File embedded", font=("", font_size))
        label.pack(padx=5)
        
        ##
        self.frame = ttk.Frame(self.top)
        self.frame.pack(padx=5)
        #
        self.embed_var = tk.StringVar()
        self.cb = ttk.Combobox(self.frame, textvariable=self.embed_var, font=("", font_size), width=50, state="readonly")
        self.cb.grid(row=0, column=0, columnspan=2)
        self.cb.bind("<<ComboboxSelected>>", self.fcb)
        #
        name_lbl1 = ttk.Label(self.frame, text="Name:", font=("", font_size))
        name_lbl1.grid(row=1, column=0, sticky="w")
        self.name_lbl = ttk.Label(self.frame, text="", font=("", font_size))
        self.name_lbl.grid(row=1, column=1, sticky="w")
        
        #
        filename_lbl1 = ttk.Label(self.frame, text="File name:", font=("", font_size))
        filename_lbl1.grid(row=2, column=0, sticky="w")
        self.filename_lbl = ttk.Label(self.frame, text="", font=("", font_size))
        self.filename_lbl.grid(row=2, column=1, sticky="w")
        
        #
        size_lbl1 = ttk.Label(self.frame, text="Size:", font=("", font_size))
        size_lbl1.grid(row=3, column=0, sticky="w")
        self.size_lbl = ttk.Label(self.frame, text="", font=("", font_size))
        self.size_lbl.grid(row=3, column=1, sticky="w")
        
        # 
        self.frame_btn = ttk.Frame(self.top)
        self.frame_btn.pack(expand=True, fill="x")
        
        self.save_btn = ttk.Button(self.frame_btn, text="Save", command=self.fsave)
        self.save_btn.pack(side="left", expand=True, fill="x")
        
        self.exit_btn = ttk.Button(self.frame_btn, text="Exit", command=self.top.destroy)
        self.exit_btn.pack(side="right", expand=True, fill="x")
        
        ## info about the embedded files
        # only filename
        embed_files = []
        self.embed_info = []
        for i in range(count):
            info = self.doc.embeddedFileInfo(i)
            # name file into list
            embed_files.append(info["filename"])
            self.embed_info.append(info)
        
        self.cb['values'] = embed_files
        self.cb.current(0)
        #
        self.name_lbl.configure(text=info["name"])
        self.filename_lbl.configure(text=info["filename"])
        self.size_lbl.configure(text=str(info["length"]))
        
    # 
    def fcb(self, event):
        # index of the item
        curr_item = self.cb.current()
        #
        name = self.embed_info[curr_item]["name"]
        filename = self.embed_info[curr_item]["filename"]
        size = self.embed_info[curr_item]["length"]
        
        # set the labels
        self.name_lbl.configure(text=name)
        self.filename_lbl.configure(text=filename)
        self.size_lbl.configure(text=str(size))
    
    #
    def fsave(self):
        curr_item = self.cb.current()
        filename = self.embed_info[curr_item]["filename"]
        #
        dirname = askopendirname(parent=self.parent, 
                         initialdir=os.path.expanduser("~"),
                         initialfile='', font_size=font_size)
        
        ## save the selected embedded file
        buff = self.doc.embeddedFileGet(filename)
        fout = open(os.path.join(dirname, filename), "wb")
        fout.write(buff)
        fout.close()


# custom dialog for password request
class MyDialog:
    
    def __init__(self, parent):
        self.top = tk.Toplevel(parent)
        
        sw = root.winfo_screenwidth()
        sh = root.winfo_screenheight()
        x = (sw / 2) - (app_width / 2)  
        y = (sh / 2) - (app_height / 2)
        self.top.geometry('+{}+{}'.format(int(x), int(y)))
        
        self.lbl = ttk.Label(self.top, text="Password:")
        self.lbl.pack()
        
        self.e_var = tk.StringVar()
        self.e = ttk.Entry(self.top, textvariable=self.e_var, font=("",font_size+2))
        self.e.pack(padx=5)
        
        b = ttk.Button(self.top, text="OK", command=self.ok)
        b.pack()
        
        cancel = ttk.Button(self.top, text="Cancel", command=self.cancel)
        cancel.pack()

    def ok(self):
        # the filename to pass
        self.filename = self.e.get()
        self.top.destroy()

    def cancel(self):
        self.filename = "-1"
        self.top.destroy()

# custom dialog for annot
class MyDialogAnnot:
    
    def __init__(self, parent):
        self.top = tk.Toplevel(parent)
        
        sw = root.winfo_screenwidth()
        sh = root.winfo_screenheight()
        x = (sw / 2) - (app_width / 2)  
        y = (sh / 2) - (app_height / 2)
        self.top.geometry('+{}+{}'.format(int(x), int(y)))
        
        # name
        self.lbl = ttk.Label(self.top, text="Name")
        self.lbl.pack()
        self.ename_var = tk.StringVar()
        self.ename = ttk.Entry(self.top, textvariable=self.ename_var, font=("",font_size))
        self.ename.pack(padx=5, fill="x")
        # content
        self.lbl = ttk.Label(self.top, text="Content")
        self.lbl.pack()
        self.t = tk.Text(self.top, height=5, width=25, font=("", font_size), wrap=tk.WORD, exportselection=True, state=tk.NORMAL)
        self.t.pack(padx=5)
        # title
        self.lbl = ttk.Label(self.top, text="Title")
        self.lbl.pack()
        self.etitle_var = tk.StringVar()
        self.etitle = ttk.Entry(self.top, textvariable=self.etitle_var, font=("",font_size))
        self.etitle.pack(padx=5, fill="x")
        # subject
        self.lbl = ttk.Label(self.top, text="Subject")
        self.lbl.pack()
        self.esubj_var = tk.StringVar()
        self.esubj = ttk.Entry(self.top, textvariable=self.esubj_var, font=("",font_size))
        self.esubj.pack(padx=5, fill="x")
        
        
        b = ttk.Button(self.top, text="OK", command=self.ok)
        b.pack()
        
        cancel = ttk.Button(self.top, text="Cancel", command=self.cancel)
        cancel.pack()

    def ok(self):
        name = self.ename.get()
        content = self.t.get(1.0, "end-1c")
        title = self.etitle.get()
        subject = self.esubj.get()
        
        self.ttext = [name, content, title, "", "", subject]
        
        self.top.destroy()

    def cancel(self):
        self.ttext = "-1"
        self.top.destroy()

###
root = tk.Tk()
root.title("Pdf Reader")
root.update_idletasks()

width = app_width
height = app_height

root.geometry('{}x{}'.format(width, height))

app = Application(master=root)
app.mainloop()

#####################
