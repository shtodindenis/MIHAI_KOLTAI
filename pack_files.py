import os
import shutil
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import re
import json
import threading

# --- CONSTANTS & CONFIG ---
CONFIG_FILE = "exporter_config_v3.json"
DEFAULT_IGNORES = [
    ".git", "node_modules", "dist", "build", "target", 
    ".vscode", ".idea", "coverage", "__pycache__", 
    "package-lock.json", "yarn.lock", "pnpm-lock.yaml", 
    ".DS_Store", ".env", ".env.local"
]

# Default extension map: extension -> add .txt (bool)
DEFAULT_EXT_MAP = {
    ".ts": True, ".js": True, ".tsx": True, ".jsx": True, 
    ".vue": True, ".py": True, ".rs": True, ".java": True, 
    ".c": True, ".cpp": True, ".h": True, ".json": False, 
    ".css": False, ".html": False, ".md": False, ".txt": False
}

class UltimateExporter:
    def __init__(self, root):
        self.root = root
        self.root.title("ZOV LAB // ULTIMATE CONTEXT EXPORTER v3")
        self.root.geometry("1000x850")
        
        self.style = ttk.Style()
        self.style.theme_use('clam')
        self.configure_styles()
        self.root.configure(bg="#1e1e1e")

        self.base_path = os.path.dirname(os.path.abspath(__file__))
        self.export_path = os.path.join(self.base_path, "ai_context_export")
        
        # State
        self.check_vars = {} 
        self.folder_config_map = {} # path -> {ext_map: {".ts": True...}}
        self.config = self.load_config()
        
        # Specific File Overrides
        self.forced_includes = self.config.get("forced_includes", []) 
        self.forced_excludes = self.config.get("forced_excludes", [])

        self.setup_ui()
        self.refresh_tree()

    def configure_styles(self):
        bg_dark = "#1e1e1e"
        fg_light = "#e0e0e0"
        accent = "#06b6d4"
        accent_hover = "#0891b2"
        panel_bg = "#2d2d2d"

        self.style.configure("TFrame", background=bg_dark)
        self.style.configure("TLabel", background=bg_dark, foreground=fg_light, font=("Segoe UI", 10))
        self.style.configure("Header.TLabel", font=("Segoe UI", 14, "bold"), foreground=accent)
        self.style.configure("SubHeader.TLabel", font=("Segoe UI", 11, "bold"), foreground="#a5f3fc")
        
        self.style.configure("TButton", font=("Segoe UI", 9, "bold"), background=panel_bg, foreground="white", borderwidth=1)
        self.style.map("TButton", background=[("active", accent), ("pressed", accent_hover)])
        
        self.style.configure("Accent.TButton", background=accent, foreground="white")
        self.style.map("Accent.TButton", background=[("active", accent_hover)])
        
        self.style.configure("TCheckbutton", background=bg_dark, foreground=fg_light, font=("Segoe UI", 10))
        self.style.map("TCheckbutton", background=[("active", bg_dark)])
        
        self.style.configure("TNotebook", background=bg_dark, borderwidth=0)
        self.style.configure("TNotebook.Tab", background=panel_bg, foreground="lightgray", padding=[12, 8])
        self.style.map("TNotebook.Tab", background=[("selected", accent)], foreground=[("selected", "white")])

        self.style.configure("Treeview", background="#252526", foreground="white", fieldbackground="#252526", rowheight=25)
        self.style.map("Treeview", background=[("selected", accent)])

    # --- UI SETUP ---
    def setup_ui(self):
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill="both", expand=True, padx=10, pady=10)

        # Header
        header_frame = ttk.Frame(main_frame)
        header_frame.pack(fill="x", pady=(0, 10))
        ttk.Label(header_frame, text="ULTIMATE CONTEXT EXPORTER", style="Header.TLabel").pack(side="left")
        
        # Scan Mode Selector
        self.mode_var = tk.StringVar(value=self.config.get("mode", "Monorepo"))
        modes = ["Monorepo", "Project (src only)", "Folder (Root)"]
        mode_cb = ttk.Combobox(header_frame, textvariable=self.mode_var, values=modes, state="readonly", width=20)
        mode_cb.pack(side="left", padx=20)
        mode_cb.bind("<<ComboboxSelected>>", lambda e: self.refresh_tree())
        
        ttk.Label(header_frame, text=f"Root: {self.base_path}", foreground="gray", font=("Consolas", 8)).pack(side="right", anchor="e")

        # Tabs
        self.notebook = ttk.Notebook(main_frame)
        self.notebook.pack(fill="both", expand=True)

        self.tab_explorer = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_explorer, text="📂 Structure & Extensions")
        self.setup_explorer_tab()

        self.tab_excludes = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_excludes, text="⛔ Excludes & Includes")
        self.setup_excludes_tab()

        self.tab_settings = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_settings, text="⚙️ General Settings")
        self.setup_settings_tab()

        self.tab_processing = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_processing, text="🧠 AI Optimization")
        self.setup_processing_tab()

        # Footer
        action_frame = ttk.Frame(main_frame)
        action_frame.pack(fill="x", pady=10)
        
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(action_frame, variable=self.progress_var, maximum=100)
        self.progress_bar.pack(fill="x", pady=(0, 10))

        btn_grid = ttk.Frame(action_frame)
        btn_grid.pack(fill="x")
        
        ttk.Button(btn_grid, text="Rescan Directory", command=self.refresh_tree).pack(side="left", padx=(0, 5))
        self.export_btn = ttk.Button(btn_grid, text="🚀 EXPORT CONTEXT", style="Accent.TButton", command=self.start_export_thread)
        self.export_btn.pack(side="right", fill="x", expand=True)

    def setup_explorer_tab(self):
        container = ttk.Frame(self.tab_explorer)
        container.pack(fill="both", expand=True, padx=10, pady=10)

        # LEFT: Tree
        left_panel = ttk.Frame(container)
        left_panel.pack(side="left", fill="both", expand=True, padx=(0, 10))
        
        ttk.Label(left_panel, text="Folder Structure", style="SubHeader.TLabel").pack(anchor="w", pady=(0, 5))
        
        canvas_frame = ttk.Frame(left_panel)
        canvas_frame.pack(fill="both", expand=True)

        self.canvas = tk.Canvas(canvas_frame, bg="#252526", highlightthickness=0)
        scrollbar = ttk.Scrollbar(canvas_frame, orient="vertical", command=self.canvas.yview)
        self.tree_frame = ttk.Frame(self.canvas)
        self.tree_frame.bind("<Configure>", lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))
        self.canvas.create_window((0, 0), window=self.tree_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=scrollbar.set)
        self.canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        btn_frame = ttk.Frame(left_panel)
        btn_frame.pack(fill="x", pady=5)
        ttk.Button(btn_frame, text="All", width=6, command=self.select_all).pack(side="left", padx=2)
        ttk.Button(btn_frame, text="None", width=6, command=self.deselect_all).pack(side="left", padx=2)

        # RIGHT: Extension Config
        right_panel = ttk.Frame(container, width=380)
        right_panel.pack(side="right", fill="y", padx=10)
        
        ttk.Label(right_panel, text="Extension Settings", style="SubHeader.TLabel").pack(anchor="w", pady=(0, 10))
        self.lbl_selected_folder = ttk.Label(right_panel, text="Editing: GLOBAL DEFAULTS", foreground="#06b6d4", wraplength=280)
        self.lbl_selected_folder.pack(anchor="w", pady=(0, 5))
        
        # Extensions Table
        cols = ("Ext", "Export?", "Add .txt?")
        self.ext_tree = ttk.Treeview(right_panel, columns=cols, show="headings", height=15)
        self.ext_tree.heading("Ext", text="Ext")
        self.ext_tree.heading("Export?", text="Export?")
        self.ext_tree.heading("Add .txt?", text="Add .txt?")
        self.ext_tree.column("Ext", width=60)
        self.ext_tree.column("Export?", width=60)
        self.ext_tree.column("Add .txt?", width=80)
        self.ext_tree.pack(fill="x", expand=True, pady=5)
        self.ext_tree.bind("<Double-1>", self.on_ext_tree_double_click)

        # Buttons
        ttk.Button(right_panel, text="Add New Extension", command=self.add_extension_dialog).pack(fill="x", pady=2)
        ttk.Button(right_panel, text="Remove Selected", command=self.remove_extension).pack(fill="x", pady=2)
        ttk.Separator(right_panel, orient="horizontal").pack(fill="x", pady=10)
        ttk.Button(right_panel, text="Save to Selected Folder", command=self.save_folder_config).pack(fill="x", pady=5)
        ttk.Button(right_panel, text="Apply to ALL Folders", command=self.apply_global_ext_config).pack(fill="x", pady=5)

        # Init global config in editor
        self.current_folder_editing = None 
        self.load_ext_table(DEFAULT_EXT_MAP)

    def setup_excludes_tab(self):
        container = ttk.Frame(self.tab_excludes)
        container.pack(fill="both", expand=True, padx=20, pady=20)

        # Excludes
        ttk.Label(container, text="⛔ Persistent Excludes (Files will NEVER be exported)", style="SubHeader.TLabel").pack(anchor="w")
        ex_btn_frame = ttk.Frame(container)
        ex_btn_frame.pack(fill="x", pady=5)
        ttk.Button(ex_btn_frame, text="Add File...", command=self.add_exclude_dialog).pack(side="left")
        ttk.Button(ex_btn_frame, text="Remove Selected", command=self.remove_exclude_item).pack(side="left", padx=5)

        self.list_excludes = tk.Listbox(container, bg="#252526", fg="#ff6b6b", height=8)
        self.list_excludes.pack(fill="x", expand=True, pady=5)
        for path in self.forced_excludes: self.list_excludes.insert(tk.END, path)

        # Includes
        ttk.Label(container, text="✅ Forced Includes (Specific files added regardless of settings)", style="SubHeader.TLabel").pack(anchor="w", pady=(20, 0))
        in_btn_frame = ttk.Frame(container)
        in_btn_frame.pack(fill="x", pady=5)
        ttk.Button(in_btn_frame, text="Add Extra File...", command=self.add_include_dialog).pack(side="left")
        ttk.Button(in_btn_frame, text="Edit Selected", command=self.edit_include_item).pack(side="left", padx=5)
        ttk.Button(in_btn_frame, text="Remove Selected", command=self.remove_include_item).pack(side="left", padx=5)

        cols = ("Path", "Txt Ext", "Full Path", "Merge")
        self.tree_includes = ttk.Treeview(container, columns=cols, show="headings", height=8)
        self.tree_includes.heading("Path", text="File Path")
        self.tree_includes.heading("Txt Ext", text="+ .txt")
        self.tree_includes.heading("Full Path", text="Full Path")
        self.tree_includes.heading("Merge", text="Merge")
        self.tree_includes.column("Path", width=400)
        self.tree_includes.pack(fill="both", expand=True, pady=5)
        self.refresh_includes_list()

    def setup_settings_tab(self):
        f = ttk.Frame(self.tab_settings)
        f.pack(fill="both", expand=True, padx=20, pady=20)
        
        self.conf_merge = tk.BooleanVar(value=self.config.get("merge_mode", False))
        self.conf_flatten = tk.BooleanVar(value=self.config.get("flatten_paths", True))
        
        ttk.Label(f, text="Export Mode", style="SubHeader.TLabel").grid(row=0, column=0, sticky="w", pady=(0, 10))
        ttk.Checkbutton(f, text="Merge ALL code into one file (code.txt)", variable=self.conf_merge).grid(row=1, column=0, sticky="w", pady=5)
        ttk.Label(f, text="*Note: .txt extensions are NOT appended inside the merged file.", foreground="gray").grid(row=2, column=0, sticky="w", padx=20)

        ttk.Label(f, text="Folder Structure (Individual Files Mode)", style="SubHeader.TLabel").grid(row=3, column=0, sticky="w", pady=(20, 10))
        ttk.Checkbutton(f, text="Flatten Paths (apps/web/main.ts -> apps_web_main.ts)", variable=self.conf_flatten).grid(row=4, column=0, sticky="w", pady=5)
        
        ttk.Label(f, text="Global Ignore Patterns (folders/files)", style="SubHeader.TLabel").grid(row=5, column=0, sticky="w", pady=(20, 5))
        self.ignore_entry = ttk.Entry(f, width=60)
        self.ignore_entry.insert(0, ", ".join(self.config.get("ignore_list", DEFAULT_IGNORES)))
        self.ignore_entry.grid(row=6, column=0, sticky="we", pady=5)

    def setup_processing_tab(self):
        f = ttk.Frame(self.tab_processing)
        f.pack(fill="both", expand=True, padx=20, pady=20)
        self.proc_comments = tk.BooleanVar(value=self.config.get("remove_comments", False))
        self.proc_empty = tk.BooleanVar(value=self.config.get("remove_empty_lines", False))
        self.proc_indent = tk.BooleanVar(value=self.config.get("fix_indent", False))
        
        ttk.Label(f, text="Code Cleaning", style="SubHeader.TLabel").pack(anchor="w", pady=(0, 10))
        ttk.Checkbutton(f, text="Remove Comments (Safe Mode)", variable=self.proc_comments).pack(anchor="w", pady=5)
        ttk.Checkbutton(f, text="Remove Empty Lines", variable=self.proc_empty).pack(anchor="w", pady=5)
        ttk.Checkbutton(f, text="Normalize Indentation", variable=self.proc_indent).pack(anchor="w", pady=5)

    # --- LOGIC: EXPLORER & TREE ---
    def refresh_tree(self):
        for widget in self.tree_frame.winfo_children(): widget.destroy()
        self.check_vars.clear()
        
        mode = self.mode_var.get()
        row = 0
        
        if mode == "Monorepo":
            # Scan specific categories
            categories = ['apps', 'packages', 'crates', 'libs', 'tools', 'services']
            found = False
            for cat in categories:
                cat_path = os.path.join(self.base_path, cat)
                if os.path.isdir(cat_path):
                    subdirs = [d for d in os.listdir(cat_path) if os.path.isdir(os.path.join(cat_path, d))]
                    if subdirs:
                        found = True
                        ttk.Label(self.tree_frame, text=f"📂 {cat.upper()}", foreground="#06b6d4", font=("Segoe UI", 10, "bold")).grid(row=row, column=0, sticky="w", pady=(10, 5))
                        row += 1
                        for sub in subdirs:
                            rel_path = os.path.join(cat, sub)
                            self.add_tree_item(sub, rel_path, row)
                            row += 1
            if not found:
                ttk.Label(self.tree_frame, text="No monorepo folders found.", foreground="red").pack()

        elif mode == "Project (src only)":
            # Scan for src and src-tauri in root
            targets = ['src', 'src-tauri']
            found = False
            for t in targets:
                if os.path.isdir(os.path.join(self.base_path, t)):
                    self.add_tree_item(f"📂 {t}", t, row)
                    row += 1
                    found = True
            if not found:
                ttk.Label(self.tree_frame, text="No 'src' or 'src-tauri' found in root.", foreground="red").pack()

        elif mode == "Folder (Root)":
            # Scan everything in root
            ignores = self.get_global_ignores()
            for item in os.listdir(self.base_path):
                if item in ignores or item.startswith('.'): continue
                if os.path.isdir(os.path.join(self.base_path, item)):
                    self.add_tree_item(f"📁 {item}", item, row)
                    row += 1

    def add_tree_item(self, label, path, row):
        var = tk.BooleanVar(value=True)
        self.check_vars[path] = var
        f = ttk.Frame(self.tree_frame)
        f.grid(row=row, column=0, sticky="w", padx=20, pady=2)
        ttk.Checkbutton(f, text=label, variable=var).pack(side="left")
        ttk.Button(f, text="⚙️", width=3, command=lambda: self.load_folder_config(path)).pack(side="left", padx=10)
        
        # Init default config if missing
        if path not in self.folder_config_map:
            self.folder_config_map[path] = {"ext_map": DEFAULT_EXT_MAP.copy()}

    # --- LOGIC: EXTENSION MANAGER ---
    def load_ext_table(self, ext_map):
        # Clear
        for i in self.ext_tree.get_children(): self.ext_tree.delete(i)
        
        # Sort keys
        for ext in sorted(ext_map.keys()):
            val = ext_map[ext]
            # Handle if val is simple bool (legacy) or dict
            is_active = True # We assume if it's in map it's potentially active, but we can manage list
            add_txt = val if isinstance(val, bool) else val.get("add_txt", False)
            
            self.ext_tree.insert("", "end", values=(ext, "Yes", "Yes" if add_txt else "No"))

    def load_folder_config(self, path):
        self.current_folder_editing = path
        self.lbl_selected_folder.config(text=f"Editing: {path}", foreground="#06b6d4")
        cfg = self.folder_config_map.get(path, {})
        self.load_ext_table(cfg.get("ext_map", DEFAULT_EXT_MAP))

    def on_ext_tree_double_click(self, event):
        item = self.ext_tree.identify_row(event.y)
        col = self.ext_tree.identify_column(event.x)
        if not item: return
        
        vals = list(self.ext_tree.item(item, "values"))
        
        if col == "#2": # Export toggle
            vals[1] = "No" if vals[1] == "Yes" else "Yes"
        elif col == "#3": # Add .txt toggle
            vals[2] = "No" if vals[2] == "Yes" else "Yes"
            
        self.ext_tree.item(item, values=vals)

    def get_current_ext_map_from_ui(self):
        m = {}
        for item in self.ext_tree.get_children():
            v = self.ext_tree.item(item, "values")
            # If "Export?" is Yes, include in map. The value is whether to add .txt
            if v[1] == "Yes":
                m[v[0]] = (v[2] == "Yes")
        return m

    def save_folder_config(self):
        if not self.current_folder_editing:
            messagebox.showwarning("Warning", "Select a folder via ⚙️ first")
            return
        new_map = self.get_current_ext_map_from_ui()
        self.folder_config_map[self.current_folder_editing]["ext_map"] = new_map
        messagebox.showinfo("Saved", f"Updated extensions for {self.current_folder_editing}")

    def apply_global_ext_config(self):
        new_map = self.get_current_ext_map_from_ui()
        for k in self.folder_config_map:
            self.folder_config_map[k]["ext_map"] = new_map.copy()
        messagebox.showinfo("Saved", "Applied configuration to ALL folders")

    def add_extension_dialog(self):
        ans = tk.simpledialog.askstring("New Extension", "Enter extension (e.g. .yaml):")
        if ans:
            if not ans.startswith("."): ans = "." + ans
            self.ext_tree.insert("", "end", values=(ans, "Yes", "No"))

    def remove_extension(self):
        sel = self.ext_tree.selection()
        if sel: self.ext_tree.delete(sel[0])

    # --- LOGIC: EXCLUDES/INCLUDES ---
    def add_exclude_dialog(self):
        f = filedialog.askopenfilename(initialdir=self.base_path)
        if f:
            try: rel = os.path.relpath(f, self.base_path)
            except: rel = f
            if rel not in self.forced_excludes:
                self.forced_excludes.append(rel)
                self.list_excludes.insert(tk.END, rel)

    def remove_exclude_item(self):
        s = self.list_excludes.curselection()
        if s:
            val = self.list_excludes.get(s[0])
            self.forced_excludes.remove(val)
            self.list_excludes.delete(s[0])

    def add_include_dialog(self):
        f = filedialog.askopenfilename(initialdir=self.base_path)
        if f: self.open_include_modal(f)

    def edit_include_item(self):
        s = self.tree_includes.selection()
        if s:
            path = self.tree_includes.item(s[0])['values'][0]
            cfg = next((x for x in self.forced_includes if x['path'] == path), None)
            if cfg: self.open_include_modal(path, cfg)

    def remove_include_item(self):
        s = self.tree_includes.selection()
        if s:
            path = self.tree_includes.item(s[0])['values'][0]
            self.forced_includes = [x for x in self.forced_includes if x['path'] != path]
            self.refresh_includes_list()

    def open_include_modal(self, path, existing=None):
        win = tk.Toplevel(self.root)
        win.title("File Settings")
        win.geometry("400x350")
        win.configure(bg="#2d2d2d")
        
        tk.Label(win, text=f"File: {os.path.basename(path)}", bg="#2d2d2d", fg="white").pack(pady=10)
        
        v_txt = tk.BooleanVar(value=existing['add_txt'] if existing else True)
        v_full = tk.BooleanVar(value=existing['use_full_path'] if existing else False)
        v_merge = tk.BooleanVar(value=existing['allow_merge'] if existing else True)
        
        tk.Checkbutton(win, text="Add .txt extension", variable=v_txt, bg="#2d2d2d", fg="white", selectcolor="#2d2d2d").pack(anchor="w", padx=20, pady=5)
        tk.Checkbutton(win, text="Use Full Absolute Path", variable=v_full, bg="#2d2d2d", fg="white", selectcolor="#2d2d2d").pack(anchor="w", padx=20, pady=5)
        tk.Checkbutton(win, text="Include in Merge (code.txt)", variable=v_merge, bg="#2d2d2d", fg="white", selectcolor="#2d2d2d").pack(anchor="w", padx=20, pady=5)
        
        def save():
            entry = {"path": path, "add_txt": v_txt.get(), "use_full_path": v_full.get(), "allow_merge": v_merge.get()}
            self.forced_includes = [x for x in self.forced_includes if x['path'] != path]
            self.forced_includes.append(entry)
            self.refresh_includes_list()
            win.destroy()
            
        tk.Button(win, text="Save", command=save, bg="#06b6d4", fg="white").pack(pady=20)

    def refresh_includes_list(self):
        for i in self.tree_includes.get_children(): self.tree_includes.delete(i)
        for i in self.forced_includes:
            self.tree_includes.insert("", "end", values=(i['path'], "Yes" if i['add_txt'] else "No", "Yes" if i['use_full_path'] else "No", "Yes" if i['allow_merge'] else "No"))

    # --- UTILS & CORE ---
    def select_all(self):
        for v in self.check_vars.values(): v.set(True)
    def deselect_all(self):
        for v in self.check_vars.values(): v.set(False)
    def get_global_ignores(self):
        return [x.strip() for x in self.ignore_entry.get().split(",") if x.strip()]

    def load_config(self):
        if os.path.exists(CONFIG_FILE):
            try:
                with open(CONFIG_FILE, 'r') as f: return json.load(f)
            except: pass
        return {}

    def save_config(self):
        cfg = {
            "mode": self.mode_var.get(),
            "merge_mode": self.conf_merge.get(),
            "flatten_paths": self.conf_flatten.get(),
            "ignore_list": self.get_global_ignores(),
            "remove_comments": self.proc_comments.get(),
            "remove_empty_lines": self.proc_empty.get(),
            "fix_indent": self.proc_indent.get(),
            "forced_includes": self.forced_includes,
            "forced_excludes": self.forced_excludes,
            "folder_configs": self.folder_config_map
        }
        with open(CONFIG_FILE, 'w') as f: json.dump(cfg, f, indent=2)

    def clean_code(self, content, ext):
        if self.proc_comments.get() and ext in ['.ts', '.js', '.rs', '.py', '.java', '.c', '.cpp', '.vue']:
            pattern = re.compile(r'//.*?$|/\*.*?\*/|\'(?:\\.|[^\\\'])*\'|"(?:\\.|[^\\"])*"', re.DOTALL | re.MULTILINE)
            content = re.sub(pattern, lambda m: " " if m.group(0).startswith('/') else m.group(0), content)
        if self.proc_empty.get():
            content = "\n".join([line for line in content.splitlines() if line.strip()])
        if self.proc_indent.get():
            content = "\n".join([line.rstrip() for line in content.splitlines()])
        return content

    def start_export_thread(self):
        self.save_config()
        self.export_btn.config(state="disabled", text="Processing...")
        self.progress_var.set(0)
        threading.Thread(target=self.run_export).start()

    def run_export(self):
        try:
            if os.path.exists(self.export_path): shutil.rmtree(self.export_path)
            os.makedirs(self.export_path)
            
            merge_mode = self.conf_merge.get()
            merge_file = open(os.path.join(self.export_path, "code.txt"), "w", encoding="utf-8") if merge_mode else None
            
            active_paths = [p for p, v in self.check_vars.items() if v.get()]
            processed = 0
            global_ignores = self.get_global_ignores()
            
            total_tasks = len(active_paths) + len(self.forced_includes)
            
            # 1. Standard Folder Scan
            for i, rel_folder in enumerate(active_paths):
                self.root.after(0, lambda v=(i/total_tasks)*80: self.progress_var.set(v))
                
                abs_root = os.path.join(self.base_path, rel_folder)
                f_cfg = self.folder_config_map.get(rel_folder, {})
                ext_map = f_cfg.get("ext_map", DEFAULT_EXT_MAP)
                
                # Normalize ext map: ensure boolean values
                normalized_map = {}
                for k, v in ext_map.items():
                    normalized_map[k] = v if isinstance(v, bool) else v.get("add_txt", False)

                for root, dirs, files in os.walk(abs_root):
                    dirs[:] = [d for d in dirs if d not in global_ignores]
                    
                    for file in files:
                        if file in global_ignores: continue
                        _, ext = os.path.splitext(file)
                        if ext not in normalized_map: continue
                        
                        f_path = os.path.join(root, file)
                        rel_f = os.path.relpath(f_path, self.base_path)
                        
                        # Check Excludes
                        if any(os.path.normpath(e) in [os.path.normpath(f_path), os.path.normpath(rel_f)] for e in self.forced_excludes):
                            continue
                            
                        should_add_txt = normalized_map[ext]
                        self.process_file(f_path, rel_f, merge_mode, merge_file, should_add_txt)
                        processed += 1

            # 2. Forced Includes
            for item in self.forced_includes:
                if not os.path.exists(item['path']): continue
                rel_f = item['path'] if item['use_full_path'] else os.path.relpath(item['path'], self.base_path)
                
                allow_merge = merge_mode and item['allow_merge']
                target_handle = merge_file if allow_merge else None
                
                # If merging is ON, but this file opts OUT of merge, it exports individually
                # If merging is OFF, it exports individually
                
                self.process_file(item['path'], rel_f, allow_merge, target_handle, item['add_txt'])
                processed += 1

            if merge_file: merge_file.close()
            self.root.after(0, lambda: self.finish(processed))

        except Exception as e:
            if merge_file: merge_file.close()
            self.root.after(0, lambda: messagebox.showerror("Error", str(e)))
            self.root.after(0, lambda: self.export_btn.config(state="normal", text="🚀 EXPORT CONTEXT"))

    def process_file(self, path, display_name, is_merge, handle, add_txt):
        try:
            with open(path, 'r', encoding='utf-8', errors='ignore') as f: c = f.read()
            c = self.clean_code(c, os.path.splitext(path)[1])
            
            if is_merge and handle:
                # NO .txt needed for merged file headers, just display name
                sep = "-" * 60
                handle.write(f"{sep}\nFILE: {display_name}\n{sep}\n{c}\n{sep}\n\n")
            else:
                # Individual Export
                header = f"// FILE: {display_name}\n// ------------------------\n"
                
                if self.conf_flatten.get():
                    clean_name = display_name.replace(os.sep, "_").replace(":", "")
                    while clean_name.startswith("_"): clean_name = clean_name[1:]
                else:
                    clean_name = display_name
                    os.makedirs(os.path.join(self.export_path, os.path.dirname(clean_name)), exist_ok=True)

                if add_txt and not clean_name.endswith(".txt"): clean_name += ".txt"
                
                dest = os.path.join(self.export_path, clean_name)
                with open(dest, 'w', encoding='utf-8') as out: out.write(header + c)
                
        except Exception as e: print(f"Error {path}: {e}")

    def finish(self, count):
        self.export_btn.config(state="normal", text="🚀 EXPORT CONTEXT")
        self.progress_var.set(100)
        msg = f"Done! {count} files processed.\nPath: {self.export_path}"
        messagebox.showinfo("Success", msg)
        try: os.startfile(self.export_path)
        except: pass

if __name__ == "__main__":
    root = tk.Tk()
    app = UltimateExporter(root)
    root.mainloop()