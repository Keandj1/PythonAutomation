#!/usr/bin/env python3
"""
File Organizer GUI - Simple graphical interface for the file organizer
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import threading
from pathlib import Path
from file_organizer import FileOrganizer, FILE_CATEGORIES

class FileOrganizerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("File Organizer")
        self.root.geometry("600x500")

        # Variables
        self.source_dir = tk.StringVar(value=str(Path.home() / "Downloads"))
        self.dest_dir = tk.StringVar(value="")
        self.use_same_dir = tk.BooleanVar(value=True)

        self.setup_ui()

    def setup_ui(self):
        # Main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # Title
        title_label = ttk.Label(main_frame, text="File Organizer", font=("Arial", 16, "bold"))
        title_label.grid(row=0, column=0, columnspan=3, pady=10)

        # Source Directory
        ttk.Label(main_frame, text="Source Directory:").grid(row=1, column=0, sticky=tk.W, pady=5)
        ttk.Entry(main_frame, textvariable=self.source_dir, width=50).grid(row=1, column=1, padx=5)
        ttk.Button(main_frame, text="Browse", command=self.browse_source).grid(row=1, column=2)

        # Destination Directory
        self.same_dir_check = ttk.Checkbutton(
            main_frame,
            text="Organize in same directory",
            variable=self.use_same_dir,
            command=self.toggle_dest_dir
        )
        self.same_dir_check.grid(row=2, column=0, columnspan=3, sticky=tk.W, pady=10)

        self.dest_label = ttk.Label(main_frame, text="Destination Directory:")
        self.dest_label.grid(row=3, column=0, sticky=tk.W, pady=5)
        self.dest_entry = ttk.Entry(main_frame, textvariable=self.dest_dir, width=50)
        self.dest_entry.grid(row=3, column=1, padx=5)
        self.dest_button = ttk.Button(main_frame, text="Browse", command=self.browse_dest)
        self.dest_button.grid(row=3, column=2)

        # Initially disable destination controls
        self.toggle_dest_dir()

        # File Categories Display
        categories_frame = ttk.LabelFrame(main_frame, text="File Categories", padding="10")
        categories_frame.grid(row=4, column=0, columnspan=3, pady=10, sticky=(tk.W, tk.E))

        # Create scrollable text widget for categories
        categories_text = tk.Text(categories_frame, height=8, width=60, wrap=tk.WORD)
        categories_text.grid(row=0, column=0)

        # Add scrollbar
        scrollbar = ttk.Scrollbar(categories_frame, command=categories_text.yview)
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        categories_text.config(yscrollcommand=scrollbar.set)

        # Display categories
        for category, extensions in FILE_CATEGORIES.items():
            categories_text.insert(tk.END, f"{category}: {', '.join(extensions)}\n")
        categories_text.config(state=tk.DISABLED)

        # Action Buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=5, column=0, columnspan=3, pady=20)

        ttk.Button(
            button_frame,
            text="Preview (Dry Run)",
            command=lambda: self.organize_files(dry_run=True)
        ).grid(row=0, column=0, padx=5)

        ttk.Button(
            button_frame,
            text="Organize Files",
            command=lambda: self.organize_files(dry_run=False),
            style="Accent.TButton"
        ).grid(row=0, column=1, padx=5)

        # Output Display
        output_frame = ttk.LabelFrame(main_frame, text="Output", padding="5")
        output_frame.grid(row=6, column=0, columnspan=3, pady=10, sticky=(tk.W, tk.E, tk.N, tk.S))

        self.output_text = tk.Text(output_frame, height=10, width=70)
        self.output_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        output_scrollbar = ttk.Scrollbar(output_frame, command=self.output_text.yview)
        output_scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        self.output_text.config(yscrollcommand=output_scrollbar.set)

        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(6, weight=1)
        output_frame.columnconfigure(0, weight=1)
        output_frame.rowconfigure(0, weight=1)

    def toggle_dest_dir(self):
        """Enable/disable destination directory controls"""
        if self.use_same_dir.get():
            self.dest_label.config(state=tk.DISABLED)
            self.dest_entry.config(state=tk.DISABLED)
            self.dest_button.config(state=tk.DISABLED)
            self.dest_dir.set("")
        else:
            self.dest_label.config(state=tk.NORMAL)
            self.dest_entry.config(state=tk.NORMAL)
            self.dest_button.config(state=tk.NORMAL)

    def browse_source(self):
        """Browse for source directory"""
        directory = filedialog.askdirectory(initialdir=self.source_dir.get())
        if directory:
            self.source_dir.set(directory)

    def browse_dest(self):
        """Browse for destination directory"""
        directory = filedialog.askdirectory(initialdir=self.dest_dir.get() or self.source_dir.get())
        if directory:
            self.dest_dir.set(directory)

    def organize_files(self, dry_run=False):
        """Run file organization in a separate thread"""
        source = self.source_dir.get()
        dest = self.dest_dir.get() if not self.use_same_dir.get() else None

        if not source:
            messagebox.showerror("Error", "Please select a source directory!")
            return

        # Clear output
        self.output_text.delete(1.0, tk.END)

        # Run organizer in separate thread to prevent UI freezing
        def run_organizer():
            try:
                self.output_text.insert(tk.END, f"{'[DRY RUN] ' if dry_run else ''}Starting file organization...\n\n")

                organizer = FileOrganizer(source, dest)

                # Redirect output to GUI
                import sys
                from io import StringIO

                old_stdout = sys.stdout
                sys.stdout = StringIO()

                organizer.organize_files(dry_run=dry_run)

                output = sys.stdout.getvalue()
                sys.stdout = old_stdout

                self.output_text.insert(tk.END, output)
                self.output_text.see(tk.END)

                if not dry_run and organizer.moved_files:
                    messagebox.showinfo("Success", f"Successfully organized {len(organizer.moved_files)} files!")

            except Exception as e:
                messagebox.showerror("Error", f"An error occurred: {str(e)}")
                self.output_text.insert(tk.END, f"\nError: {str(e)}")

        thread = threading.Thread(target=run_organizer)
        thread.daemon = True
        thread.start()

def main():
    root = tk.Tk()
    app = FileOrganizerGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()