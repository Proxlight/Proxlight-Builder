import tkinter as tk
from tkinter import ttk, filedialog, colorchooser, simpledialog
import sv_ttk

class PropertyDialog(tk.Toplevel):
    def __init__(self, master, widget):
        super().__init__(master)
        self.widget = widget
        self.title("Edit Widget Properties")

        self.create_widgets()
        self.populate_properties()
    
    def create_widgets(self):
        self.text_area = tk.Text(self, wrap='word', height=10, width=50)
        self.text_area.pack(padx=10, pady=10)

        self.apply_button = ttk.Button(self, text="Apply", command=self.apply_properties)
        self.apply_button.pack(pady=5)

    def populate_properties(self):
        properties = self.get_widget_properties()
        for prop, value in properties.items():
            self.text_area.insert(tk.END, f"{prop}: {value}\n")

    def get_widget_properties(self):
        properties = {}
        if isinstance(self.widget, (ttk.Button, ttk.Label, ttk.Entry, ttk.Checkbutton, ttk.Radiobutton)):
            properties["text"] = self.widget.cget("text")

        if isinstance(self.widget, (ttk.Label, ttk.Entry)):
            properties["foreground"] = self.widget.cget("foreground")
            properties["font"] = self.widget.cget("font")

        return properties

    def apply_properties(self):
        properties = self.text_area.get("1.0", tk.END).strip().split('\n')
        for prop in properties:
            if ":" in prop:
                prop_split = prop.split(": ", 1)
                key = prop_split[0]
                value = prop_split[1] if len(prop_split) > 1 else ""
                if key == "font":
                    value = tuple(value.split())
                self.widget.configure(**{key: value})

class ApplicationBuilder:
    def __init__(self, root):
        self.root = root
        self.root.title("Proxlight Builder")

        # Apply Sun Valley theme
        sv_ttk.set_theme("light")

        # Main canvas for adding and moving widgets with dark background
        self.canvas = tk.Canvas(root, width=800, height=600)
        self.canvas.pack(fill=tk.BOTH, expand=True)

        # Control frame for widget selection
        self.control_frame = ttk.Frame(root, padding="10")
        self.control_frame.pack(fill=tk.X)

        self.widget_var = tk.StringVar()
        self.widget_var.set("Button")
        self.widgets = ["Button", "Label", "Entry", "Checkbutton", "Radiobutton", "Combobox", "Spinbox", "Listbox", "Text"]

        self.widget_menu = ttk.OptionMenu(self.control_frame, self.widget_var, *self.widgets)
        self.widget_menu.pack(side=tk.LEFT)

        self.add_button = ttk.Button(self.control_frame, text="Add Widget", command=self.add_widget)
        self.add_button.pack(side=tk.LEFT)

        self.export_button = ttk.Button(self.control_frame, text="Export to Python", command=self.export_to_python)
        self.export_button.pack(side=tk.LEFT)

        # Edit actions
        self.cut_button = ttk.Button(self.control_frame, text="Cut", command=self.cut_widget)
        self.cut_button.pack(side=tk.LEFT)

        self.copy_button = ttk.Button(self.control_frame, text="Copy", command=self.copy_widget)
        self.copy_button.pack(side=tk.LEFT)

        self.paste_button = ttk.Button(self.control_frame, text="Paste", command=self.paste_widget)
        self.paste_button.pack(side=tk.LEFT)

        self.delete_button = ttk.Button(self.control_frame, text="Delete", command=self.delete_widget)
        self.delete_button.pack(side=tk.LEFT)

        self.widgets_added = []

        # Variables to track the dragged widget and clipboard
        self.drag_data = {"x": 0, "y": 0, "item": None}
        self.clipboard = None

    def add_widget(self):
        
        widget_type = self.widget_var.get()

        if widget_type == "Button":
            widget = ttk.Button(self.canvas, text="Button")

        elif widget_type == "Checkbutton":
            widget = ttk.Checkbutton(self.canvas, text="Checkbutton")
            
        elif widget_type == "Label":
            widget = ttk.Label(self.canvas, text="Label")
        elif widget_type == "Entry":
            widget = ttk.Entry(self.canvas)
        
        elif widget_type == "Radiobutton":
            widget = ttk.Radiobutton(self.canvas, text="Radiobutton")
        elif widget_type == "Combobox":
            widget = ttk.Combobox(self.canvas, values=["Option 1", "Option 2", "Option 3"])
        elif widget_type == "Spinbox":
            widget = ttk.Spinbox(self.canvas, from_=0, to=10)
        elif widget_type == "Listbox":
            widget = tk.Listbox(self.canvas)
            for item in ["Item 1", "Item 2", "Item 3"]:
                widget.insert(tk.END, item)
        elif widget_type == "Text":
            widget = tk.Text(self.canvas, height=4, width=20)


        # Place the widget on the canvas
        canvas_id = self.canvas.create_window(50, 50, window=widget, anchor='nw')

        self.widgets_added.append((widget_type, canvas_id, widget))

        # Bind events to enable dragging and right-click context menu
        widget.bind("<ButtonPress-1>", self.on_widget_press)
        widget.bind("<B1-Motion>", self.on_widget_move)
        widget.bind("<Button-3>", self.show_context_menu)
        widget.bind("<Double-Button-1>", lambda event, w=widget: self.edit_properties(w))

    def on_widget_press(self, event):
        # Record the item and its location
        self.drag_data["item"] = self.canvas.find_closest(event.x, event.y)[0]
        self.drag_data["x"] = event.x
        self.drag_data["y"] = event.y

    def on_widget_move(self, event):
        # Compute the distance moved
        delta_x = event.x - self.drag_data["x"]
        delta_y = event.y - self.drag_data["y"]

        # Move the widget
        self.canvas.move(self.drag_data["item"], delta_x, delta_y)

        # Record the new position
        self.drag_data["x"] = event.x
        self.drag_data["y"] = event.y

    def show_context_menu(self, event):
        # Create a context menu
        context_menu = tk.Menu(self.root, tearoff=0)
        context_menu.add_command(label="Cut", command=self.cut_widget)
        context_menu.add_command(label="Copy", command=self.copy_widget)
        context_menu.add_command(label="Paste", command=self.paste_widget)
        context_menu.add_command(label="Delete", command=self.delete_widget)
        context_menu.post(event.x_root, event.y_root)

    def cut_widget(self):
        if self.drag_data["item"]:
            self.clipboard = self.drag_data["item"]
            self.canvas.delete(self.drag_data["item"])
            self.drag_data["item"] = None

    def copy_widget(self):
        if self.drag_data["item"]:
            self.clipboard = self.drag_data["item"]

    def paste_widget(self):
        if self.clipboard:
            widget_type, canvas_id, widget = next((w for w in self.widgets_added if w[1] == self.clipboard), (None, None, None))
            if widget_type:
                self.add_widget_of_type(widget_type)
                self.canvas.coords(self.clipboard, self.drag_data["x"], self.drag_data["y"])

    def add_widget_of_type(self, widget_type):
        if widget_type == "Button":
            widget = ttk.Button(self.canvas, text="Button")
        elif widget_type == "Label":
            widget = ttk.Label(self.canvas, text="Label")
        elif widget_type == "Entry":
            widget = ttk.Entry(self.canvas)
        elif widget_type == "Checkbutton":
            widget = ttk.Checkbutton(self.canvas, text="Checkbutton")
        elif widget_type == "Radiobutton":
            widget = ttk.Radiobutton(self.canvas, text="Radiobutton")
        elif widget_type == "Combobox":
            widget = ttk.Combobox(self.canvas, values=["Option 1", "Option 2", "Option 3"])
        elif widget_type == "Spinbox":
            widget = ttk.Spinbox(self.canvas, from_=0, to=10)
        elif widget_type == "Listbox":
            widget = tk.Listbox(self.canvas)
            for item in ["Item 1", "Item 2", "Item 3"]:
                widget.insert(tk.END, item)
        elif widget_type == "Text":
            widget = tk.Text(self.canvas, height=4, width=20)
        
        canvas_id = self.canvas.create_window(50, 50, window=widget, anchor='nw')

        self.widgets_added.append((widget_type, canvas_id, widget))

        # Bind events to enable dragging and right-click context menu
        widget.bind("<ButtonPress-1>", self.on_widget_press)
        widget.bind("<B1-Motion>", self.on_widget_move)
        widget.bind("<Button-3>", self.show_context_menu)
        widget.bind("<Double-Button-1>", lambda event, w=widget: self.edit_properties(w))

    def edit_properties(self, widget):
        dialog = PropertyDialog(self.root, widget)

    def delete_widget(self):
        if self.drag_data["item"]:
            self.canvas.delete(self.drag_data["item"])
            self.drag_data["item"] = None

    def export_to_python(self):
        file_path = filedialog.asksaveasfilename(defaultextension=".py",
                                                 filetypes=[("Python files", "*.py"), ("All files", "*.*")])
        if file_path:
            with open(file_path, 'w') as file:
                file.write(self.generate_python_code())

    def generate_python_code(self):
        code = [
            "import tkinter as tk",
            "from tkinter import ttk",
            "import sv_ttk",
            "",
            "root = tk.Tk()",
            "root.title('Generated Application')",
            "",
            "# Apply Sun Valley theme",
            "sv_ttk.set_theme('light')",
            "",
            "canvas = tk.Canvas(root, bg='white', width=800, height=600)",
            "canvas.pack(fill=tk.BOTH, expand=True)",
            ""
        ]

        for widget_type, canvas_id, widget in self.widgets_added:
            try:
                x, y = self.canvas.coords(canvas_id)
            except ValueError:
                # Skip if canvas_id is invalid
                continue

            if widget_type == "Button":
                code.append(f"button = ttk.Button(canvas, text='{widget.cget('text')}')")
                code.append(f"canvas.create_window({x}, {y}, window=button, anchor='nw')")
            elif widget_type == "Label":
                code.append(f"label = ttk.Label(canvas, text='{widget.cget('text')}')")
                code.append(f"canvas.create_window({x}, {y}, window=label, anchor='nw')")
            elif widget_type == "Entry":
                code.append("entry = ttk.Entry(canvas)")
                code.append(f"canvas.create_window({x}, {y}, window=entry, anchor='nw')")
            elif widget_type == "Checkbutton":
                code.append(f"checkbutton = ttk.Checkbutton(canvas, text='{widget.cget('text')}')")
                code.append(f"canvas.create_window({x}, {y}, window=checkbutton, anchor='nw')")
            elif widget_type == "Radiobutton":
                code.append(f"radiobutton = ttk.Radiobutton(canvas, text='{widget.cget('text')}')")
                code.append(f"canvas.create_window({x}, {y}, window=radiobutton, anchor='nw')")
            elif widget_type == "Combobox":
                values = widget.cget('values')
                code.append(f"combobox = ttk.Combobox(canvas, values={values})")
                code.append(f"canvas.create_window({x}, {y}, window=combobox, anchor='nw')")
            elif widget_type == "Spinbox":
                from_, to = widget.cget('from'), widget.cget('to')
                code.append(f"spinbox = ttk.Spinbox(canvas, from_={from_}, to={to})")
                code.append(f"canvas.create_window({x}, {y}, window=spinbox, anchor='nw')")
            elif widget_type == "Listbox":
                code.append("listbox = tk.Listbox(canvas)")
                for item in widget.get(0, tk.END):
                    code.append(f"listbox.insert(tk.END, '{item}')")
                code.append(f"canvas.create_window({x}, {y}, window=listbox, anchor='nw')")
            elif widget_type == "Text":
                code.append("text = tk.Text(canvas)")
                text_content = widget.get("1.0", tk.END).strip()
                lines = text_content.split('\n')
                for line in lines:
                    code.append(f"text.insert(tk.END, '{line}')")
                code.append(f"canvas.create_window({x}, {y}, window=text, anchor='nw')")
        
        code.append("")
        code.append("root.mainloop()")
        
        return "\n".join(code)

if __name__ == "__main__":
    root = tk.Tk()
    app = ApplicationBuilder(root)
    root.mainloop()
