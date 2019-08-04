#!/usr/bin/env python3

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


#
app_width = 1100
app_height = 800

# font size of the application
font_size = 18


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
        # the zoom
        self.zoom = 2
        # canvas objects
        self.canvas_list = []
        # ref to pix
        self.pix = None
        
        ######### TOOLBAR
        self.toolb_frame = ttk.Frame(self)
        self.toolb_frame.grid(column=0, row=1, columnspan=3, sticky="w")
        
        ### BUTTONS
        self.menu_image = tk.PhotoImage(file="icons/menu2.png")
        self.toc_btn = ttk.Button(self.toolb_frame, image=self.menu_image, width=-1, command=self.fhidetoc)
        self.toc_btn.grid(row=0, column=0, sticky="w")

        self.open_image = tk.PhotoImage(file="icons/open2.png")
        self.open_btn = ttk.Button(self.toolb_frame, image=self.open_image, width=-1, command=self.chooseFile)
        self.open_btn.grid(column=1, row=0, sticky="w")

        self.minus_image = tk.PhotoImage(file="icons/minus.png")
        self.minus_btn = ttk.Button(self.toolb_frame, image=self.minus_image, width=-1, command=self.fminus)
        self.minus_btn.grid(column=2, row=0, sticky="w")

        self.page_lbl = ttk.Label(self.toolb_frame, text="Page: 0", width=-1)
        self.page_lbl.grid(row=0, column=3)

        self.plus_image = tk.PhotoImage(file="icons/plus.png")
        self.plus_btn = ttk.Button(self.toolb_frame, image=self.plus_image, width=-1, command=self.fplus)
        self.plus_btn.grid(column=4, row=0, sticky="w")

        self.zoomp_btn = ttk.Button(self.toolb_frame, image=self.plus_image, width=-1, command=self.fzoomp)
        self.zoomp_btn.grid(column=5, row=0, sticky="w")

        self.zoom_lbl = ttk.Label(self.toolb_frame, text="Zoom: 0", width=-1)
        self.zoom_lbl.grid(row=0, column=6)

        self.zoomm_btn = ttk.Button(self.toolb_frame, image=self.minus_image, width=-1, command=self.fzoomm)
        self.zoomm_btn.grid(column=7, row=0, sticky="w")

        self.left_image = tk.PhotoImage(file="icons/left.png")
        self.left_btn = ttk.Button(self.toolb_frame, image=self.left_image, width=-1, command=self.fleft)
        self.left_btn.grid(column=8, row=0, sticky="w")

        self.right_image = tk.PhotoImage(file="icons/right.png")
        self.right_btn = ttk.Button(self.toolb_frame, image=self.right_image, width=-1, command=self.fright)
        self.right_btn.grid(column=9, row=0, sticky="w")

        self.search_image = tk.PhotoImage(file="icons/search.png")
        self.search_btn = ttk.Button(self.toolb_frame, image=self.search_image, width=-1, command=self.fsearch)
        self.search_btn.grid(column=10, row=0, sticky="w")

        self.print_image = tk.PhotoImage(file="icons/print.png")
        self.print_btn = ttk.Button(self.toolb_frame, image=self.print_image, width=-1, command=self.fprint)
        self.print_btn.grid(column=11, row=0, sticky="w")

        self.metadata_image = tk.PhotoImage(file="icons/pdf.png")
        self.metadata_btn = ttk.Button(self.toolb_frame, image=self.metadata_image, width=-1, command=self.fmetadata)
        self.metadata_btn.grid(column=12, row=0, sticky="w")
        #
        # button quit
        self.quit_image = tk.PhotoImage(file="icons/quit.png")
        quit_btn = ttk.Button(self, image=self.quit_image, width=-1, command=quit)
        quit_btn.grid(row=1, column=3, sticky="w")
        
        ### TOC
        # 0 show - 1 hide
        self.tocHide = 0
        # frame for treeview e scrollbar - , rowspan=20
        self.tv_frame = ttk.Frame(self)
        self.tv_frame.grid(column=0, row=2, sticky="nw")
        # fake label needed to properly resize the frame
        self.fake_lbl = ttk.Label(self.tv_frame, text="")
        self.tv = ttk.Treeview(self.tv_frame, selectmode="browse", columns=("Page"), height=20)
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

        self.tv.bind("<<TreeviewSelect>>", self.ftv)

        self.tv.bind("<<TreeviewOpen>>", self.ftvOpen)

        self.tv.bind("<<TreeviewClose>>", self.ftvClose)
        #
        self.s.configure('new.TFrame', background='green')
        self.cframe = ttk.Frame(self, style="new.TFrame")
        self.cframe.grid(column=1, row=2, columnspan=3, sticky="nwes")
        ## canvas

        self.canvas = tk.Canvas(self.cframe, width=0, height=0, scrollregion=(0,0,app_width,app_height), bg='red')
        ## scrollbars
        self.hbar=ttk.Scrollbar(self.cframe, orient=tk.HORIZONTAL)
        self.hbar.pack(side=tk.BOTTOM, fill=tk.X)
        self.hbar.config(command=self.canvas.xview)

        self.vbar=ttk.Scrollbar(self.cframe, orient=tk.VERTICAL)
        self.vbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.vbar.config(command=self.canvas.yview)

        self.canvas.pack(side=tk.LEFT, anchor="nw", fill="none")
        self.canvas.config(xscrollcommand=self.hbar.set, yscrollcommand=self.vbar.set)
        ####### canvas rubberband
        self.startx = 0
        self.starty = 0
        self.rubberbandBox = None

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
        self.canvas.bind("<Control-Button-1>", self.mouseDown)
        self.canvas.bind("<Control-Button1-Motion>", self.mouseMotion)
        self.canvas.bind("<Control-Button1-ButtonRelease>", self.mouseUp)
        
        
        # filename
        self.filename = ""
        # the password if the file is encrypted
        self.password = ""
        
        # filename required
        if len(sys.argv) > 1:
            if sys.argv[1]:
                self.filename = sys.argv[1]
        else:
            messagebox.showerror("Error", "File required.")
            sys.exit()
        
        # load the file
        self.getDoc(self.filename)
        # list of entries
        self.list_id = []
        self.fcanvas()
    
    # the outline
    def popToc(self, id):
        # empty the treeview
        self.list_id = []
        self.tv.delete(*self.tv.get_children())
        #
        for item in self.toc:
            #
            idx = item[0]

            if idx == 1:

                self.list_id = []
                id = self.tv.insert("", 0, text=item[1], values=(item[2]))

                self.list_id.append(id)
            elif idx > 1:
                while len(self.list_id) >= idx:
                    self.list_id.pop()
                
                if idx > len(self.list_id):
                    id = self.tv.insert(self.list_id[idx-2], 0, text=item[1], values=(item[2]))

                    self.list_id.append(id)

                elif idx < len(self.list_id):
                    self.list_id.pop()
                    #
                    id = self.tv.insert(self.list_id[idx-2], 0, text=item[1], values=(item[2]))
                    self.list_id.append(id)
                
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
        self.doc.save(filename="doc_saved.pdf")
    
    # perform a searching on the whole document
    def fsearch(self):
        pass
    

    def ftv(self, event):
        try:
            item = self.tv.selection()[0]
            new_page = int(self.tv.set(item)["Page"])
            self.fdelete()
            self.current_page = new_page
            self.page = self.doc.loadPage(self.current_page-1)
            #
            self.fcanvas()
        except:
            pass
    
    def ftvOpen(self, event):
        self.ftvbind()
    
    def ftvbind(self):
        self.tv.unbind("<<TreeviewSelect>>")
        self.tv.after(100, lambda:self.tv.bind("<<TreeviewSelect>>", self.ftv))
    
    def ftvClose(self, event):
        self.ftvbind()
    
    # empty the treeview
    def ftvempty(self):
        # empty the treeview
        for id in self.tv.get_children():
            for idd in self.tv.get_children(id):
                self.tv.delete(idd)
    
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
            # do not exit if a previous file has been opened
            if not self.doc:
                sys.exit()
        
        # if a password is required
        if ndoc.isEncrypted:
           d = MyDialog(self.master)
           self.master.wait_window(d.top)
           
           if d.filename != "-1":
               try:
                   ndoc.authenticate(d.filename)
               except:
                   messagebox.showerror("Error", "Wrong password")
                   sys.exit()
           else:
               # if no doc has been loaded already
               if not self.doc:
                   sys.exit()
               else:
                   return 0
        
        # close the old file
        if self.doc:
            self.doc.close()
        
        # the doc
        self.doc = ndoc
        
        # amount of pages
        self.page_count = len(self.doc)
        
        # toc - outline
        self.toc = self.doc.getToC()
        
        # load the first page
        self.page = self.doc.loadPage(0)
        self.current_page = 1
        
        # load the outline
        self.popToc("")
    
    # the canvas
    def fcanvas(self, rot=0):
        
        self.page_lbl.configure(text="Page: "+str(self.current_page))
        self.zoom_lbl.configure(text="Zoom: "+str(self.zoom))
        
        self.mat = fitz.Matrix(self.zoom, self.zoom)
        # rotate of 90 gradi to right - -90 to left
        self.mat.preRotate(rot)
        
        # the page to image 
        self.pix = self.page.getPixmap(matrix=self.mat, colorspace=fitz.csRGB, alpha=False)
        self.pix2 = self.pix.getImageData("png")
        
        # get the image
        self.png1 = tk.PhotoImage(data=self.pix2)

        # reconfigure canvas
        self.canvas.configure(width=self.pix.width, height=self.pix.height, scrollregion=(0, 0, self.pix.width, self.pix.height))

        # put gif image on canvas
        id = self.canvas.create_image(0, 0, image=self.png1, anchor=tk.NW)
        self.canvas_list.append(id)
    
    # choose a file to open
    def chooseFile(self):
        
        self.filename = askopenfilename(parent=self.master, 
           initialdir="doc",
           initialfile='',
           filetypes=[("PDF", '*.pdf'), ("All files", "*")],
           font_size=font_size)
        
        # load the file
        self.getDoc(self.filename)
        # fill canvas
        self.fcanvas()

    def fdelete(self):
        for item in self.canvas_list:
            self.canvas.delete(item)
            self.canvas_list = []

    def fplus(self):
        
        if self.current_page < self.page_count:
            self.fdelete()
            self.current_page += 1
            self.page = self.doc.loadPage(self.current_page-1)
            #
            self.fcanvas()

    def fminus(self):
        
        if self.current_page > 1:
            self.fdelete()

            self.current_page -= 1
            self.page = self.doc.loadPage(self.current_page-1)
            #
            self.fcanvas()

    def fzoomp(self):
        self.zoom += 0.5
        self.page = self.doc.loadPage(self.current_page-1)
        #
        self.fcanvas()
    
    def fzoomm(self):
        if self.zoom > 0.5:
            self.zoom -= 0.5
            self.page = self.doc.loadPage(self.current_page-1)
            #
            self.fcanvas()

    def fleft(self):
        self.rotation -= 90
        self.fcanvas(rot=self.rotation)
    
    def fright(self):
        self.rotation += 90
        self.fcanvas(rot=self.rotation)

    # get the metadata
    def fmetadata(self):
       print("Metadata::", self.doc.metadata)

    def getText(self, fitz_rect):

        rect = fitz_rect

        words = self.page.getTextWords()
 
        # Case 2: select the words which at least intersect the rect
        # ------------------------------------------------------------------------------
        mywords = [w for w in words if fitz.Rect(w[:4]).intersects(rect)]
        mywords.sort(key=itemgetter(3, 0))
        group = groupby(mywords, key=itemgetter(3))
        print("\nSelect the words intersecting the rectangle")
        print("--------------- INIZIO ---------------")
        selected_text = ""
        for y1, gwords in group:
            selected_text = " ".join(w[4] for w in gwords)
            print(selected_text)
        print("---------------- FINE ----------------")
        # to clipboard
        self.clipboard_clear()
        self.clipboard_append(selected_text)
        #"""


    def mouseDown(self, event):
        
        self.x1 = 0
        self.y1 = 0
        self.x2 = 0
        self.y2 = 0
        
        self.startx = self.canvas.canvasx(event.x)
        self.starty = self.canvas.canvasy(event.y)

    def mouseMotion(self, event):
        
        x = self.canvas.canvasx(event.x)
        y = self.canvas.canvasy(event.y)

        if (self.startx != event.x)  and (self.starty != event.y) :
            self.canvas.delete(self.rubberbandBox)
            self.rubberbandBox = self.canvas.create_rectangle(
                self.startx, self.starty, x, y)
            
            self.master.update_idletasks()
        
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
                
    def mouseUp(self, event):
        self.canvas.delete(self.rubberbandBox)
        self.getText(fitz.Rect(self.x1/self.zoom,self.y1/self.zoom,self.x2/self.zoom,self.y2/self.zoom))

# sustom dialog
class MyDialog:
    
    def __init__(self, parent):
        self.top = tk.Toplevel(parent)
        
        # this dialod is centered
        sw = root.winfo_screenwidth()
        sh = root.winfo_screenheight()
        x = (sw / 2) - (width / 2)  
        y = (sh / 2) - (height / 2)
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
        self.filename = self.e.get() or "-1"
        self.top.destroy()

    def cancel(self):
        self.filename = "-1"
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

