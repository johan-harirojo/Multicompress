from __future__ import annotations

import os
import sys
import tkinter as tk
from pathlib import Path
from tkinter import filedialog, ttk

from .engines.bzip2_engine import BZip2Engine
from .engines.lzma_engine import LZMAEngine
from .engines.sevenzip_engine import SevenZipEngine


class MultiCompressGUI:
    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title("MultiCompress")
        self.root.geometry("720x540")
        self.root.minsize(640, 480)

        self.format_var = tk.StringVar(value="bzip2")
        self.operation_var = tk.StringVar(value="compress")
        self.level_var = tk.StringVar(value="9")
        self.preset_var = tk.StringVar(value="6")
        self.method_var = tk.StringVar(value="LZMA2")

        self.source_var = tk.StringVar()
        self.output_var = tk.StringVar()

        main = ttk.Frame(self.root, padding=12)
        main.pack(fill="both", expand=True)

        ttk.Label(main, text="Format").grid(row=0, column=0, sticky="w")
        ttk.Combobox(
            main,
            textvariable=self.format_var,
            values=["bzip2", "lzma", "7z"],
            state="readonly",
            width=20,
        ).grid(row=0, column=1, sticky="ew", padx=(0, 10))

        ttk.Label(main, text="Opération").grid(row=0, column=2, sticky="w")
        ttk.Combobox(
            main,
            textvariable=self.operation_var,
            values=["compress", "decompress", "test", "list", "create", "extract"],
            state="readonly",
            width=20,
        ).grid(row=0, column=3, sticky="ew")

        ttk.Button(main, text="Choisir un fichier", command=self.select_source).grid(row=1, column=0, sticky="ew", pady=(10, 0))
        ttk.Entry(main, textvariable=self.source_var).grid(row=1, column=1, columnspan=3, sticky="ew", pady=(10, 0))

        ttk.Label(main, text="Sortie").grid(row=2, column=0, sticky="w", pady=(10, 0))
        ttk.Entry(main, textvariable=self.output_var).grid(row=2, column=1, columnspan=3, sticky="ew", pady=(10, 0))
        ttk.Button(main, text="Choisir la sortie", command=self.select_output).grid(row=2, column=4, sticky="ew", pady=(10, 0), padx=(8, 0))

        ttk.Label(main, text="Niveau / preset").grid(row=3, column=0, sticky="w", pady=(10, 0))
        ttk.Entry(main, textvariable=self.level_var).grid(row=3, column=1, sticky="ew", pady=(10, 0))

        ttk.Label(main, text="Preset LZMA").grid(row=3, column=2, sticky="w", pady=(10, 0))
        ttk.Entry(main, textvariable=self.preset_var).grid(row=3, column=3, sticky="ew", pady=(10, 0))

        ttk.Label(main, text="Méthode 7z").grid(row=4, column=0, sticky="w", pady=(10, 0))
        ttk.Combobox(
            main,
            textvariable=self.method_var,
            values=["LZMA", "LZMA2"],
            state="readonly",
            width=12,
        ).grid(row=4, column=1, sticky="w", pady=(10, 0))

        ttk.Button(main, text="Exécuter", command=self.run_action).grid(row=5, column=0, columnspan=5, sticky="ew", pady=(18, 10))

        self.log = tk.Text(main, height=16, wrap="word")
        self.log.grid(row=6, column=0, columnspan=5, sticky="nsew")

        self.status = tk.StringVar(value="Prêt")
        ttk.Label(main, textvariable=self.status, anchor="w").grid(row=7, column=0, columnspan=5, sticky="ew")

        main.columnconfigure(1, weight=1)
        main.columnconfigure(3, weight=1)
        main.rowconfigure(6, weight=1)

    def log_message(self, text: str) -> None:
        self.log.insert(tk.END, text + "\n")
        self.log.see(tk.END)

    def select_source(self) -> None:
        if self.format_var.get() == "7z" and self.operation_var.get() in {"create", "extract"}:
            path = filedialog.askdirectory(title="Choisir un dossier ou archive")
        else:
            path = filedialog.askopenfilename(title="Choisir un fichier source")
        if path:
            self.source_var.set(path)

    def select_output(self) -> None:
        if self.format_var.get() == "7z" and self.operation_var.get() == "extract":
            path = filedialog.askdirectory(title="Choisir le dossier de destination")
        else:
            path = filedialog.asksaveasfilename(title="Choisir le fichier de sortie")
        if path:
            self.output_var.set(path)

    def run_action(self) -> None:
        self.log.delete(1.0, tk.END)
        self.status.set("Exécution...")
        try:
            fmt = self.format_var.get()
            op = self.operation_var.get()
            source = Path(self.source_var.get())
            output = self.output_var.get() or None

            if not source.exists():
                raise FileNotFoundError(f"Fichier introuvable : {source}")

            if fmt == "bzip2":
                engine = BZip2Engine()
                if op == "compress":
                    result = engine.compress_file(source, output, level=int(self.level_var.get()))
                    self.log_message(f"Compression OK : {result}")
                elif op == "decompress":
                    result = engine.decompress_file(source, output)
                    self.log_message(f"Décompression OK : {result}")
                elif op == "test":
                    ok = engine.test_file(source)
                    self.log_message("Archive valide" if ok else "Archive invalide")
                else:
                    raise ValueError("L’opération demandée n’est pas prise en charge pour BZip2.")
            elif fmt == "lzma":
                engine = LZMAEngine()
                if op == "compress":
                    mode = self.output_var.get() and self.output_var.get().lower().endswith(".xz") and "xz" or "lzma"
                    result = engine.compress_file(source, output, format_name=mode, preset=int(self.preset_var.get()))
                    self.log_message(f"Compression LZMA OK : {result}")
                elif op == "decompress":
                    result = engine.decompress_file(source, output)
                    self.log_message(f"Décompression LZMA OK : {result}")
                elif op == "test":
                    ok = engine.test_file(source)
                    self.log_message("Flux valide" if ok else "Flux invalide")
                else:
                    raise ValueError("L’opération demandée n’est pas prise en charge pour LZMA.")
            elif fmt == "7z":
                engine = SevenZipEngine()
                if op == "create":
                    destination = output or str(Path(source.parent) / (source.name + ".7z"))
                    result = engine.create_archive(source, destination, method=self.method_var.get())
                    self.log_message(f"Archive créée : {result}")
                elif op == "extract":
                    destination = output or str(Path(source).with_suffix(""))
                    result = engine.extract_archive(source, destination)
                    self.log_message(f"Archive extraite : {result}")
                elif op == "list":
                    content = engine.list_archive(source)
                    self.log_message(content)
                elif op == "test":
                    ok = engine.test_archive(source)
                    self.log_message("Archive valide" if ok else "Archive invalide")
                else:
                    raise ValueError("L’opération demandée n’est pas prise en charge pour 7z.")
            else:
                raise ValueError("Format inconnu.")

            self.status.set("Succès")
        except Exception as exc:  # pragma: no cover - GUI branch
            self.log_message(f"Erreur : {exc}")
            self.status.set("Erreur")


def main() -> int:
    try:
        root = tk.Tk()
    except tk.TclError as exc:
        print("La GUI nécessite un environnement graphique disponible (DISPLAY/X11).", file=sys.stderr)
        print(str(exc), file=sys.stderr)
        return 1

    app = MultiCompressGUI(root)
    root.mainloop()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
