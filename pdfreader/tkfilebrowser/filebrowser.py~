# -*- coding: utf-8 -*-
"""
tkfilebrowser - Alternative to filedialog for Tkinter
Copyright 2017 Juliette Monsel <j_4321@protonmail.com>

tkfilebrowser is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

tkfilebrowser is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.


Main class
"""

from os import walk, mkdir
from os.path import exists, join, getmtime, realpath, split, expanduser, abspath
from os.path import isabs, splitext, dirname, getsize, isdir, isfile, islink
import traceback
import tkfilebrowser.constants as cst
from tkfilebrowser.autoscrollbar import AutoScrollbar
from tkfilebrowser.path_button import PathButton
from tkinter import font

_ = cst._
unquote = cst.unquote
tk = cst.tk
ttk = cst.ttk

class FileBrowser(tk.Toplevel):
    """Filebrowser dialog class."""
    def __init__(self, parent, initialdir="", initialfile="", mode="openfile",
                 multiple_selection=False, defaultext="", title="Filebrowser",
                 filetypes=[], okbuttontext=None, cancelbuttontext=_("Cancel"),
                 foldercreation=False, font_size=0):
        """
        Create a filebrowser dialog.

        Arguments:
            * initialdir: initial folder whose content is displayed
            * initialfile: initial selected item (just the name, not the full path)
            * mode: openfile, opendir or save
            * multiple_selection (open modes only): boolean, allow to select multiple files,
            * defaultext (save mode only): extension added to filename if none is given
            * filetypes: [('name', '*.ext1|*.ext2|..'), ...]
              show only files of given filetype ("*" for all files)
            * okbuttontext: text displayed on the validate button, if None, the
              default text corresponding to the mode is used (either Open or Save)
            * cancelbuttontext: text displayed on the button that cancels the
              selection.
            * foldercreation: enable the user to create new folders if True (default)
        """
        tk.Toplevel.__init__(self, parent)

        self.font_size = font_size
        
        # keep track of folders to be able to move backward/foreward in history
        if initialdir:
            self.history = [initialdir]
        else:
            self.history = [expanduser("~")]
        self._hist_index = -1

        self.transient(parent)
        self.grab_set()
        self.protocol("WM_DELETE_WINDOW", self.quit)
        self.title(title)

        self.rowconfigure(2, weight=1)
        self.columnconfigure(0, weight=1)

        self.mode = mode
        self.result = ""
        self.foldercreation = foldercreation

        # hidden files/folders visibility
        self.hide = False
        # hidden items
        self.hidden = ()

        # ---  style
        style = ttk.Style(self)
        bg = style.lookup("TFrame", "background")
        style.layout("right.tkfilebrowser.Treeview.Item",
                     [('Treeitem.padding',
                       {'children':
                           [('Treeitem.image', {'side': 'left', 'sticky': ''}),
                            ('Treeitem.focus',
                             {'children':
                                 [('Treeitem.text',
                                   {'side': 'left', 'sticky': ''})],
                              'side': 'left',
                              'sticky': ''})],
                        'sticky': 'nswe'})])
        style.layout("left.tkfilebrowser.Treeview.Item",
                     [('Treeitem.padding',
                       {'children':
                           [('Treeitem.image', {'side': 'left', 'sticky': ''}),
                            ('Treeitem.focus',
                             {'children':
                                 [('Treeitem.text', {'side': 'left', 'sticky': ''})],
                              'side': 'left',
                              'sticky': ''})],
                        'sticky': 'nswe'})])
        
        # treeview: row height
        ffont = font.Font(family='', size=self.font_size)
        self.tv_row_height = ffont.metrics("linespace")
        
        style.configure("right.tkfilebrowser.Treeview", rowheight=self.tv_row_height+2)
        style.configure("right.tkfilebrowser.Treeview.Item", padding=2)
        style.configure("right.tkfilebrowser.Treeview.Heading",
                        font="TkDefaultFont")
        style.configure("left.tkfilebrowser.Treeview.Heading",
                        font="TkDefaultFont")
        style.configure("left.tkfilebrowser.Treeview.Item", padding=2)
        style.configure("listbox.TFrame", background="white", relief="sunken")
        field_bg = style.lookup("TEntry", "fieldbackground", default='white')
        tree_field_bg = style.lookup("ttk.Treeview", "fieldbackground",
                                     default='white')
        fg = style.lookup('TLabel', 'foreground', default='black')
        active_bg = style.lookup('TButton', 'background', ('active',))
        active_fg = style.lookup('TButton', 'foreground', ('active',))
        disabled_fg = style.lookup('TButton', 'foreground', ('disabled',))
        sel_bg = style.lookup('Treeview', 'background', ('selected',))
        sel_fg = style.lookup('Treeview', 'foreground', ('selected',))
        style.configure("left.tkfilebrowser.Treeview", background=active_bg,
                        font=("", self.font_size),
                        fieldbackground=active_bg)
        style.configure("left.tkfilebrowser.Treeview", rowheight=self.tv_row_height+2)
        self.configure(background=bg)
        # path button style
        style.configure("path.TButton", padding=2)
        selected_bg = style.lookup("TButton", "background", ("pressed",))
        map_bg = style.map("TButton", "background")
        map_bg.append(("selected", selected_bg))
        style.map("path.TButton",
                  background=map_bg,
                  font=[("selected", "TkDefaultFont" +str(self.font_size)+ "bold")])

        # ---  images
        self.im_file = tk.PhotoImage(file=cst.IM_FILE, master=self)
        self.im_folder = tk.PhotoImage(file=cst.IM_FOLDER, master=self)
        self.im_file_link = tk.PhotoImage(file=cst.IM_FILE_LINK, master=self)
        self.im_folder_link = tk.PhotoImage(file=cst.IM_FOLDER_LINK, master=self)
        self.im_new = tk.PhotoImage(file=cst.IM_NEW, master=self)
        self.im_drive = tk.PhotoImage(file=cst.IM_DRIVE, master=self)
        self.im_home = tk.PhotoImage(file=cst.IM_HOME, master=self)
        self.im_recent = tk.PhotoImage(file=cst.IM_RECENT, master=self)
        self.im_recent_24 = tk.PhotoImage(file=cst.IM_RECENT_24, master=self)

        # ---  filetypes
        self.filetype = tk.StringVar(self)
        self.filetypes = {}
        if filetypes:
            b_filetype = ttk.Menubutton(self, textvariable=self.filetype)
            self.menu = tk.Menu(self, tearoff=False, foreground=fg, background=field_bg,
                                disabledforeground=disabled_fg,
                                activeforeground=active_fg,
                                selectcolor=fg,
                                activeborderwidth=0,
                                borderwidth=0,
                                activebackground=active_bg)
            for name, exts in filetypes:
                self.filetypes[name] = [ext.split("*")[-1].strip() for ext in exts.split("|")]
                self.menu.add_radiobutton(label=name, value=name,
                                          command=self._change_filetype,
                                          variable=self.filetype)
            b_filetype.configure(menu=self.menu)
            b_filetype.grid(row=3, sticky="e", padx=10, pady=4)
            self.filetype.set(filetypes[0][0])
        else:
            self.filetypes[""] = [""]
            self.menu = None

        # ---  path completion
        self.listbox_var = tk.StringVar(self)
        self.listbox_frame = ttk.Frame(self, style="listbox.TFrame", borderwidth=1)
        self.listbox = tk.Listbox(self.listbox_frame,
                                  listvariable=self.listbox_var,
                                  highlightthickness=0,
                                  borderwidth=0,
                                  background=field_bg,
                                  foreground=fg,
                                  selectforeground=sel_fg,
                                  selectbackground=sel_bg)
        self.listbox.pack(expand=True, fill="x")

        # ---  file name
        self.multiple_selection = multiple_selection

        # ---  path bar
        self.path_var = tk.StringVar(self)
        frame_bar = ttk.Frame(self)
        frame_bar.columnconfigure(0, weight=1)
        frame_bar.grid(row=1, sticky="ew", pady=10, padx=10)
        frame_recent = ttk.Frame(frame_bar)
        frame_recent.grid(row=0, column=0, sticky="w")
        ttk.Label(frame_recent, image=self.im_recent_24).pack(side="left")
        ttk.Label(frame_recent, text=_("Recently used"),
                  font="TkDefaultFont 9 bold").pack(side="left", padx=4)
        self.path_bar = ttk.Frame(frame_bar)
        self.path_bar.grid(row=0, column=0, sticky="ew")
        self.path_bar_buttons = []

        paned = ttk.PanedWindow(self, orient="horizontal")
        paned.grid(row=2, sticky="eswn", padx=10)

        # ---  left pane
        left_pane = ttk.Frame(paned)
        left_pane.columnconfigure(0, weight=1)
        left_pane.rowconfigure(0, weight=1)

        paned.add(left_pane, weight=0)
        self.left_tree = ttk.Treeview(left_pane, selectmode="browse",
                                      style="left.tkfilebrowser.Treeview")

        self.left_tree.column("#0", width=150)
        self.left_tree.heading("#0", text=_("Shortcuts"), anchor="w")
        self.left_tree.grid(row=0, column=0, sticky="sewn")

        scroll_left = AutoScrollbar(left_pane, command=self.left_tree.yview)
        scroll_left.grid(row=0, column=1, sticky="ns")
        self.left_tree.configure(yscrollcommand=scroll_left.set)

        
        self.left_tree.insert("", "end", iid="/", text="Root",
                                  image=self.im_drive)
        home = expanduser("~")
        self.left_tree.insert("", "end", iid=home, image=self.im_home,
                              text=split(home)[-1])

        # ---  right pane
        right_pane = ttk.Frame(paned)
        right_pane.columnconfigure(0, weight=1)
        right_pane.rowconfigure(0, weight=1)
        paned.add(right_pane, weight=1)

        selectmode = "browse"

        self.right_tree = ttk.Treeview(right_pane, selectmode=selectmode,
                                       style="right.tkfilebrowser.Treeview",
                                       columns=("location", "size", "date"),
                                       displaycolumns=("size", "date"))
        # headings
        self.right_tree.heading("#0", text=_("Name"), anchor="w",
                                command=lambda: self._sort_files_by_name(True))
        self.right_tree.heading("location", text=_("Location"), anchor="w",
                                command=lambda: self._sort_by_location(False))
        self.right_tree.heading("size", text=_("Size"), anchor="w",
                                command=lambda: self._sort_by_size(False))
        self.right_tree.heading("date", text=_("Modified"), anchor="w",
                                command=lambda: self._sort_by_date(False))
        # columns
        self.right_tree.column("#0", width=250)
        self.right_tree.column("location", width=100)
        self.right_tree.column("size", stretch=False, width=85)
        self.right_tree.column("date", width=120)
        # tags
        self.right_tree.tag_configure("0", background=tree_field_bg)
        self.right_tree.tag_configure("1", background=active_bg)
        self.right_tree.tag_configure("folder", image=self.im_folder)
        self.right_tree.tag_configure("file", image=self.im_file)
        self.right_tree.tag_configure("folder_link", image=self.im_folder_link)
        self.right_tree.tag_configure("file_link", image=self.im_file_link)
        if mode == "opendir":
            self.right_tree.tag_configure("file", foreground="gray")
            self.right_tree.tag_configure("file_link", foreground="gray")

        self.right_tree.grid(row=0, column=0, sticky="eswn")
        # scrollbar
        self._scroll_h = AutoScrollbar(right_pane, orient='horizontal',
                                       command=self.right_tree.xview)
        self._scroll_h.grid(row=1, column=0, sticky='ew')
        scroll_right = AutoScrollbar(right_pane, command=self.right_tree.yview)
        scroll_right.grid(row=0, column=1, sticky="ns")
        self.right_tree.configure(yscrollcommand=scroll_right.set,
                                  xscrollcommand=self._scroll_h.set)

        # ---  buttons
        frame_buttons = ttk.Frame(self)
        frame_buttons.grid(row=4, sticky="ew", pady=10, padx=10)
        if okbuttontext is None:
            okbuttontext = _("Open")
        ttk.Button(frame_buttons, text=okbuttontext,
                   command=self.validate).pack(side="right")
        ttk.Button(frame_buttons, text=cancelbuttontext,
                   command=self.quit).pack(side="right", padx=4)

        # ---  key browsing entry
        self.key_browse_var = tk.StringVar(self)
        self.key_browse_entry = ttk.Entry(self, textvariable=self.key_browse_var,
                                          width=10)
        # list of folders/files beginning by the letters inserted in self.key_browse_entry
        self.paths_beginning_by = []
        self.paths_beginning_by_index = 0  # current index in the list

        # ---  initialization
        if not initialdir:
            initialdir = expanduser("~")

        self.display_folder(initialdir)
        initialpath = join(initialdir, initialfile)
        if initialpath in self.right_tree.get_children(""):
            self.right_tree.selection_add(initialpath)

        # ---  bindings
        # left tree
        self.left_tree.bind("<<TreeviewSelect>>", self._shortcut_select)
        # right tree
        self.right_tree.bind("<Double-1>", self._select)
        self.right_tree.bind("<Return>", self._select)

        if mode == "opendir":
            self.right_tree.bind("<<TreeviewSelect>>",
                                 self._file_selection_opendir)
        elif mode == "openfile":
            self.right_tree.bind("<<TreeviewSelect>>",
                                 self._file_selection_openfile)
        # listbox
        self.listbox.bind("<FocusOut>",
                          lambda e: self.listbox_frame.place_forget())
        
        # main bindings
        self.bind("<Control-h>", self.toggle_hidden)
        self.bind_all("<Button-1>", self._unpost, add=True)

        self.update_idletasks()
        self.lift()

    def _key_browse(self, *args):
        """Use keyboard to browse tree."""
        self.key_browse_entry.unbind("<Up>")
        self.key_browse_entry.unbind("<Down>")
        deb = self.key_browse_entry.get().lower()
        if deb:
            if self.mode == 'opendir':
                children = list(self.right_tree.tag_has("folder"))
                children.extend(self.right_tree.tag_has("folder_link"))
            else:
                children = self.right_tree.get_children("")
            self.paths_beginning_by = [i for i in children if split(i)[-1][:len(deb)].lower() == deb]
            sel = self.right_tree.selection()
            if sel:
                self.right_tree.selection_remove(*sel)
            if self.paths_beginning_by:
                self.paths_beginning_by_index = 0
                self._browse_list(0)
                self.key_browse_entry.bind("<Up>",
                                           lambda e: self._browse_list(-1))
                self.key_browse_entry.bind("<Down>",
                                           lambda e: self._browse_list(1))

    def _browse_list(self, delta):
        """
        Navigate between folders/files with Up/Down keys.

        Navigation between folders/files beginning by the letters in
        self.key_browse_entry.
        """
        self.paths_beginning_by_index += delta
        self.paths_beginning_by_index %= len(self.paths_beginning_by)
        sel = self.right_tree.selection()
        if sel:
            self.right_tree.selection_remove(*sel)
        path = abspath(join(self.history[self._hist_index],
                            self.paths_beginning_by[self.paths_beginning_by_index]))
        self.right_tree.see(path)
        self.right_tree.selection_add(path)

    # ---  column sorting
    def _sort_files_by_name(self, reverse):
        """Sort files and folders by (reversed) alphabetical order."""
        files = list(self.right_tree.tag_has("file"))
        files.extend(list(self.right_tree.tag_has("file_link")))
        folders = list(self.right_tree.tag_has("folder"))
        folders.extend(list(self.right_tree.tag_has("folder_link")))
        files.sort(reverse=reverse)
        folders.sort(reverse=reverse)

        for index, item in enumerate(folders):
            self.move_item(item, index)
        l = len(folders)

        for index, item in enumerate(files):
            self.move_item(item, index + l)
        self.right_tree.heading("#0",
                                command=lambda: self._sort_files_by_name(not reverse))

    def _sort_by_location(self, reverse):
        """Sort files by location."""
        l = [(self.right_tree.set(k, "location"), k) for k in self.right_tree.get_children('')]
        l.sort(reverse=reverse)
        for index, (val, k) in enumerate(l):
            self.move_item(k, index)
        self.right_tree.heading("location",
                                command=lambda: self._sort_by_location(not reverse))

    def _sort_by_size(self, reverse):
        """Sort files by size."""
        files = list(self.right_tree.tag_has("file"))
        files.extend(list(self.right_tree.tag_has("file_link")))
        nb_folders = len(self.right_tree.tag_has("folder"))
        nb_folders += len(list(self.right_tree.tag_has("folder_link")))
        files.sort(reverse=reverse, key=getsize)

        for index, item in enumerate(files):
            self.move_item(item, index + nb_folders)

        self.right_tree.heading("size",
                                command=lambda: self._sort_by_size(not reverse))

    def _sort_by_date(self, reverse):
        """Sort files and folders by modification date."""
        files = list(self.right_tree.tag_has("file"))
        files.extend(list(self.right_tree.tag_has("file_link")))
        folders = list(self.right_tree.tag_has("folder"))
        folders.extend(list(self.right_tree.tag_has("folder_link")))
        l = len(folders)
        folders.sort(reverse=reverse, key=getmtime)
        files.sort(reverse=reverse, key=getmtime)

        for index, item in enumerate(folders):
            self.move_item(item, index)
        for index, item in enumerate(files):
            self.move_item(item, index + l)

        self.right_tree.heading("date",
                                command=lambda: self._sort_by_date(not reverse))

    def _file_selection_openfile(self, event):
        """Put selected file name in path_entry if visible."""
        sel = self.right_tree.selection()

    def _file_selection_opendir(self, event):
        """
        Prevent selection of files in opendir mode and put selected folder
        name in path_entry if visible.
        """
        sel = self.right_tree.selection()
        if sel:
            for s in sel:
                tags = self.right_tree.item(s, "tags")
                if ("file" in tags) or ("file_link" in tags):
                    self.right_tree.selection_remove(s)
            sel = self.right_tree.selection()

    def _shortcut_select(self, event):
        """Selection of a shortcut (left pane)."""
        sel = self.left_tree.selection()
        sel = sel[0]
        self.display_folder(sel)

    def _select(self, event):
        """display folder content on double click / Enter, validate if file."""
        sel = self.right_tree.selection()
        if sel:
            sel = sel[0]
            tags = self.right_tree.item(sel, "tags")
            if ("folder" in tags) or ("folder_link" in tags):
                self.display_folder(sel)
            elif self.mode != "opendir":
                self.validate(event)
        elif self.mode == "opendir":
            self.validate(event)

    def _unpost(self, event):
        """Unpost the filetype selection menu on click and hide self.key_browse_entry."""
        if self.menu:
            w, h = self.menu.winfo_width(), self.menu.winfo_height()
            dx = event.x_root - self.menu.winfo_x()
            dy = event.y_root - self.menu.winfo_y()
            if dx < 0 or dx > w or dy < 0 or dy > h:
                self.menu.unpost()

    def _change_filetype(self):
        """Update view on filetype change."""
        if self.path_bar.winfo_ismapped():
            self.display_folder(self.history[self._hist_index])

    def _select_enter(self, event, d):
        """Change entry content on Return key press in listbox."""
        self.entry.delete(0, "end")
        self.entry.insert(0, join(d, self.listbox.selection_get()))
        self.entry.selection_clear()
        self.entry.focus_set()
        self.entry.icursor("end")

    def _select_mouse(self, event, d):
        """Change entry content on click in listbox."""
        self.entry.delete(0, "end")
        self.entry.insert(0, join(d, self.listbox.get("@%i,%i" % (event.x, event.y))))
        self.entry.selection_clear()
        self.entry.focus_set()
        self.entry.icursor("end")

    def _update_path_bar(self, path):
        """Update the buttons in path bar."""
        for b in self.path_bar_buttons:
            b.destroy()
        self.path_bar_buttons = []
        if path == "/":
            folders = [""]
        else:
            folders = path.split("/")
        b = PathButton(self.path_bar, self.path_var, "/", image=self.im_drive,
                       command=lambda: self.display_folder("/"))
        self.path_bar_buttons.append(b)
        b.grid(row=0, column=1, sticky="ns")
        p = "/"
        for i, folder in enumerate(folders[1:]):
            p = join(p, folder)
            b = PathButton(self.path_bar, self.path_var, p, text=folder,
                           width=len(folder) + 1,
                           command=lambda f=p: self.display_folder(f),
                           style="path.TButton")
            self.path_bar_buttons.append(b)
            b.grid(row=0, column=i + 2, sticky="ns")

    def display_folder(self, folder, reset=True, update_bar=True):
        """
        Display the content of folder in self.right_tree.

        Arguments:
            * reset (boolean): forget all the part of the history right of self._hist_index
            * update_bar (boolean): update the buttons in path bar
        """
        folder = abspath(folder)  # remove trailing / if any
        if not self.path_bar.winfo_ismapped():
            self.path_bar.grid()
            self.right_tree.configure(displaycolumns=("size", "date"))
            w = self.right_tree.winfo_width() - 205
            if w < 0:
                w = 250
            self.right_tree.column("#0", width=w)
            self.right_tree.column("size", stretch=False, width=85)
            self.right_tree.column("date", width=120)

        if reset:  # reset history
            if not self._hist_index == -1:
                self.history = self.history[:self._hist_index + 1]
                self._hist_index = -1
            self.history.append(folder)
        if update_bar:  # update path bar
            self._update_path_bar(folder)
        self.path_var.set(folder)
        self.right_tree.delete(*self.right_tree.get_children(""))  # clear self.right_tree
        try:
            root, dirs, files = walk(folder).send(None)
            # display folders first
            dirs.sort(key=lambda n: n.lower())
            i = 0
            for i, d in enumerate(dirs):
                p = join(root, d)
                if islink(p):
                    tags = ("folder_link", str(i % 2))
                else:
                    tags = ("folder", str(i % 2))
                if d[0] == ".":
                    tags = tags + ("hidden",)

                self.right_tree.insert("", "end", p, text=d, tags=tags,
                                       values=("", "", cst.get_modification_date(p)))
            # display files
            i += 1
            files.sort(key=lambda n: n.lower())
            extension = self.filetypes[self.filetype.get()]
            if extension == [""]:
                for j, f in enumerate(files):
                    p = join(root, f)
                    if islink(p):
                        tags = ("file_link", str((i + j) % 2))
                    else:
                        tags = ("file", str((i + j) % 2))
                    if f[0] == ".":
                        tags = tags + ("hidden",)

                    self.right_tree.insert("", "end", p, text=f, tags=tags,
                                           values=("", cst.get_size(p),
                                                   cst.get_modification_date(p)))
            else:
                for f in files:
                    ext = splitext(f)[-1]
                    if ext in extension:
                        p = join(root, f)
                        if islink(p):
                            tags = ("file_link", str(i % 2))
                        else:
                            tags = ("file", str(i % 2))
                        if f[0] == ".":
                            tags = tags + ("hidden",)
                        i += 1

                        self.right_tree.insert("", "end", p, text=f, tags=tags,
                                               values=("", cst.get_size(p),
                                                       cst.get_modification_date(p)))
            items = self.right_tree.get_children("")
            if items:
                self.right_tree.focus_set()
                self.right_tree.focus(items[0])
        except StopIteration:
            #print("err")
            pass

    def move_item(self, item, index):
        """Move item to index and update dark/light line alternance."""
        self.right_tree.move(item, "", index)
        tags = [t for t in self.right_tree.item(item, 'tags')
                if t not in ['1', '0']]
        tags.append(str(index % 2))
        self.right_tree.item(item, tags=tags)

    def toggle_hidden(self, event=None):
        """Toggle the visibility of hidden files/folders."""
        if self.hide:
            self.hide = False
            for item in reversed(self.hidden):
                self.right_tree.move(item, "", 0)
            self.hidden = ()
        else:
            self.hide = True
            self.hidden = self.right_tree.tag_has("hidden")
            self.right_tree.detach(*self.right_tree.tag_has("hidden"))

    def get_result(self):
        """Return selection."""
        return self.result

    def quit(self):
        """Destroy dialog."""
        self.unbind_all("<FocusIn>")
        self.unbind_all("<Button-1>")
        self.destroy()

    def _validate_single_sel(self):
        """Validate selection in open mode without multiple selection."""
        sel = self.right_tree.selection()
        if self.mode is "openfile":
            if len(sel) == 1:
                sel = sel[0]
                tags = self.right_tree.item(sel, "tags")
                if ("folder" in tags) or ("folder_link" in tags):
                    self.display_folder(sel)
                else:
                    self.result = realpath(sel)
                    self.quit()
        else:  # mode is "opendir"
            if len(sel) == 1:
                self.result = realpath(sel[0])
            else:
                self.result = realpath(self.history[self._hist_index])
            self.quit()

    def validate(self, event=None):
        self._validate_single_sel()
