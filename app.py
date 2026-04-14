import os
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from PIL import Image, ImageTk

from label_generator import generate_label

HERE = os.path.dirname(os.path.abspath(__file__))
DEFAULT_LOGO = os.path.join(HERE, "assets", "logo.png")
OUTPUT_DIR = os.path.join(HERE, "output")


class LabelApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("QR Label Generator")
        self.geometry("900x500")
        self.resizable(True, True)

        self.logo_path = tk.StringVar(value=DEFAULT_LOGO if os.path.exists(DEFAULT_LOGO) else "")
        self.part_no = tk.StringVar(value="ADD-0001")
        self.part_name = tk.StringVar(value="Name of the Part")
        self.preview_img = None

        self._build_ui()

    def _build_ui(self):
        form = ttk.Frame(self, padding=12)
        form.pack(side="left", fill="y")

        ttk.Label(form, text="Part No").grid(row=0, column=0, sticky="w")
        ttk.Entry(form, textvariable=self.part_no, width=32).grid(row=1, column=0, columnspan=2, pady=(0, 8))

        ttk.Label(form, text="Part Name").grid(row=2, column=0, sticky="w")
        ttk.Entry(form, textvariable=self.part_name, width=32).grid(row=3, column=0, columnspan=2, pady=(0, 8))

        ttk.Label(form, text="Logo").grid(row=4, column=0, sticky="w")
        ttk.Entry(form, textvariable=self.logo_path, width=24).grid(row=5, column=0, pady=(0, 8))
        ttk.Button(form, text="Browse", command=self._pick_logo).grid(row=5, column=1, padx=(6, 0))

        ttk.Button(form, text="Generate Preview", command=self._generate).grid(row=6, column=0, columnspan=2, sticky="ew", pady=(8, 4))
        ttk.Button(form, text="Save As...", command=self._save_as).grid(row=7, column=0, columnspan=2, sticky="ew")

        self.status = ttk.Label(form, text="", foreground="gray")
        self.status.grid(row=8, column=0, columnspan=2, sticky="w", pady=(10, 0))

        preview = ttk.Frame(self, padding=12, relief="groove")
        preview.pack(side="right", fill="both", expand=True)
        self.preview_label = ttk.Label(preview, text="Preview will appear here", anchor="center")
        self.preview_label.pack(fill="both", expand=True)

    def _pick_logo(self):
        path = filedialog.askopenfilename(
            title="Select logo",
            filetypes=[("Images", "*.png *.jpg *.jpeg *.bmp"), ("All files", "*.*")],
        )
        if path:
            self.logo_path.set(path)

    def _generate(self, save_path=None):
        pn = self.part_no.get().strip()
        nm = self.part_name.get().strip()
        if not pn or not nm:
            messagebox.showwarning("Missing input", "Enter both Part No and Part Name.")
            return None

        os.makedirs(OUTPUT_DIR, exist_ok=True)
        out = save_path or os.path.join(OUTPUT_DIR, f"{pn.replace('/', '_')}.png")
        logo = self.logo_path.get() or None

        try:
            path, w, h = generate_label(pn, nm, logo, out)
        except Exception as e:
            messagebox.showerror("Error", str(e))
            return None

        self._show_preview(path)
        self.status.config(text=f"Saved: {os.path.basename(path)}  ({w}x{h}px @ 300 DPI)")
        return path

    def _save_as(self):
        path = filedialog.asksaveasfilename(
            defaultextension=".png",
            filetypes=[("PNG", "*.png")],
            initialdir=OUTPUT_DIR,
            initialfile=f"{self.part_no.get().strip() or 'label'}.png",
        )
        if path:
            self._generate(save_path=path)

    def _show_preview(self, path):
        img = Image.open(path)
        max_w = max(400, self.preview_label.winfo_width() - 20)
        max_h = max(200, self.preview_label.winfo_height() - 20)
        ratio = min(max_w / img.width, max_h / img.height, 1.0)
        if ratio < 1.0:
            img = img.resize((int(img.width * ratio), int(img.height * ratio)), Image.LANCZOS)
        self.preview_img = ImageTk.PhotoImage(img)
        self.preview_label.config(image=self.preview_img, text="")


if __name__ == "__main__":
    LabelApp().mainloop()
