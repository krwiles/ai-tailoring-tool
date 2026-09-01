import threading
import tkinter as tk
from pathlib import Path
from tkinter import scrolledtext, font, ttk
from typing import Dict

from src.config import AppSettings
from src.io import FileManager
from src.model import JobData, TemplateSelection, resolve_template_choice
from src.workflow import ResumeWorkflow, CoverLetterWorkflow


class AppGUI:
    """
    Tkinter GUI for Resume & Cover Letter Generator
    """

    # (TemplateSelection field, folder relative to project_dir, glob pattern, display label)
    TEMPLATE_CATEGORIES = (
        ("resume_template", Path("data", "resumes"), "*.docx", "Resume Template"),
        ("cover_letter_template", Path("data", "cover_letters"), "*.docx", "Cover Letter Template"),
        ("resume_prompt", Path("prompts", "resume"), "*.txt", "Resume Prompt"),
        ("cover_letter_prompt", Path("prompts", "cover_letter"), "*.txt", "Cover Letter Prompt"),
    )

    def __init__(self,
                 resume_workflow: ResumeWorkflow,
                 cover_letter_workflow: CoverLetterWorkflow,
                 file_manager: FileManager,
                 settings: AppSettings
                 ):
        # Inject dependencies
        self.resume_workflow = resume_workflow
        self.cover_workflow = cover_letter_workflow
        self.file_manager = file_manager
        self.settings = settings

        # Build the UI form
        self.root = tk.Tk()
        self.root.tk.call("tk", "scaling", 1.25)
        self.root.title("Chat BDD: Resume Tailoring")
        icon_path = self.file_manager.project_dir / "bdd.ico"
        try:
            if icon_path.exists():
                self.root.iconbitmap(icon_path)
        except Exception as e:
            print(f"Warning: Could not load icon: {e}")
        default_font = font.nametofont("TkDefaultFont")
        default_font.configure(size=11)
        self.text_font = font.nametofont("TkTextFont")
        self.text_font.configure(size=11)
        self._build_form()

        # Initialize loading spinner variables
        self._loading = False
        self._spinner_chars = "⠁⠂⠄⡀⡈⡐⡠⣀⣁⣂⣄⣌⣔⣤⣥⣦⣮⣶⣷⣿⡿⠿⢟⠟⡛⠛⠫⢋⠋⠍⡉⠉⠑⠡⢁"
        self._spinner_index = 0
        self._spinner_text = "Generating..."

        # Resolve persisted template/prompt selection and populate the dropdowns
        self._load_template_selection()

    def _build_form(self):
        """Build all input fields and buttons with left alignment"""

        pad_opts = {"padx": 5, "pady": 5}

        # Template/prompt selection (a standing preference, populated in _load_template_selection)
        self.template_combos: Dict[str, ttk.Combobox] = {}
        self.template_maps: Dict[str, Dict[str, Path]] = {}

        for row, (field_name, _folder, _pattern, label) in enumerate(self.TEMPLATE_CATEGORIES):
            tk.Label(self.root, text=label, anchor="w").grid(row=row, column=0, sticky="w", **pad_opts)
            combo = ttk.Combobox(self.root, width=37, state="readonly")
            combo.grid(row=row, column=1, sticky="w", **pad_opts)
            combo.bind(
                "<<ComboboxSelected>>",
                lambda e, f=field_name, c=combo: self._on_template_selected(f, c)
            )
            self.template_combos[field_name] = combo
            self.template_maps[field_name] = {}

        self.template_error_label = tk.Label(
            self.root, text="", fg="red", anchor="w", justify="left", wraplength=500
        )
        self.template_error_label.grid(row=4, column=0, columnspan=3, sticky="w", **pad_opts)

        # Company
        tk.Label(self.root, text="Company", anchor="w").grid(row=5, column=0, sticky="w", **pad_opts)
        self.company_entry = tk.Entry(self.root, width=40)
        self.company_entry.grid(row=5, column=1, sticky="w", **pad_opts)
        self.company_err = tk.Label(self.root, text="", fg="red", anchor="w", justify="left")
        self.company_err.grid(row=5, column=2, sticky="w", **pad_opts)
        self.company_entry.bind(
            "<KeyRelease>",
            lambda e: self.company_err.config(text="")
        )

        # Position
        tk.Label(self.root, text="Position", anchor="w").grid(row=6, column=0, sticky="w", **pad_opts)
        self.position_entry = tk.Entry(self.root, width=40)
        self.position_entry.grid(row=6, column=1, sticky="w", **pad_opts)
        self.position_err = tk.Label(self.root, text="", fg="red", anchor="w", justify="left")
        self.position_err.grid(row=6, column=2, sticky="w", **pad_opts)
        self.position_entry.bind(
            "<KeyRelease>",
            lambda e: self.position_err.config(text="")
        )

        # Location
        tk.Label(self.root, text="Location", anchor="w").grid(row=7, column=0, sticky="w", **pad_opts)
        self.location_entry = tk.Entry(self.root, width=40)
        self.location_entry.grid(row=7, column=1, sticky="w", **pad_opts)
        self.location_optional = tk.Label(self.root, text="(optional)", fg="grey", anchor="w", justify="left")
        self.location_optional.grid(row=7, column=2, sticky="w", **pad_opts)
        self.location_entry.bind(
            "<KeyRelease>",
            lambda e: self.location_optional.config(text="")
        )

        # Job Description
        tk.Label(self.root, text="Job Description", anchor="w").grid(row=8, column=0, sticky="nw", **pad_opts)
        self.description_text = scrolledtext.ScrolledText(
            self.root,
            width=60,
            height=15,
            wrap=tk.WORD,
            font=self.text_font
        )
        self.description_text.grid(row=8, column=1, rowspan=2, columnspan=2, sticky="nsew", **pad_opts)
        self.description_err = tk.Label(self.root, text="", fg="red", anchor="w", justify="left")
        self.description_err.grid(row=9, column=0, sticky="nw", **pad_opts)
        self.description_text.bind(
            "<KeyRelease>",
            lambda e: self.description_err.config(text="")
        )

        # Cover Letter checkbox
        self.cover_var = tk.BooleanVar(value=True)  # default ON
        self.cover_cb = tk.Checkbutton(
            self.root,
            text="Cover Letter",
            variable=self.cover_var
        )
        self.cover_cb.grid(row=10, column=0, sticky="w", **pad_opts)

        # Generate button
        self.generate_btn = tk.Button(self.root, text="Generate", command=self._generate)
        self.generate_btn.grid(row=10, column=1, sticky="w", **pad_opts)

        # Status/output label
        self.status_label = tk.Label(self.root, text="Chat BDD IS READY TO COOK  👈(￣▽￣👈)", fg="Black", anchor="w", justify="left")
        self.status_label.grid(row=11, column=0, columnspan=3, sticky="w", **pad_opts)

        # Make job description expand if window resized
        self.root.grid_rowconfigure(9, weight=1)
        self.root.grid_columnconfigure(2, weight=1)

    def _load_template_selection(self):
        """Scan each template/prompt folder, resolve the saved-vs-fallback choice,
        populate the dropdowns, and persist the resolved selection back to settings.ini."""
        saved = self.settings.load_template_selection()
        resolved_fields = {}
        missing_labels = []

        for field_name, folder, pattern, label in self.TEMPLATE_CATEGORIES:
            files = self.file_manager.list_files(folder, pattern)
            saved_path = getattr(saved, field_name)
            selected = resolve_template_choice(files, saved_path)

            name_map = {f.name: f for f in files}
            self.template_maps[field_name] = name_map

            combo = self.template_combos[field_name]
            combo["values"] = list(name_map.keys())
            if selected is not None:
                combo.set(selected.name)
                combo.config(state="readonly")
            else:
                combo.set("")
                combo.config(state="disabled")
                missing_labels.append(label)

            resolved_fields[field_name] = selected

        self.template_selection = TemplateSelection(**resolved_fields)
        self.settings.save_template_selection(self.template_selection)

        self._templates_missing = bool(missing_labels)
        if missing_labels:
            self.template_error_label.config(
                text="No files found for: " + ", ".join(missing_labels)
                + ". Add a file to the matching folder and restart the app."
            )
        else:
            self.template_error_label.config(text="")

        self._set_ui_state(True)

    def _on_template_selected(self, field_name: str, combo: ttk.Combobox):
        chosen_name = combo.get()
        path = self.template_maps[field_name].get(chosen_name)
        if path is None:
            return
        setattr(self.template_selection, field_name, path)
        self.settings.save_template_selection(self.template_selection)

    def _generate(self):
        company = self.company_entry.get()
        position = self.position_entry.get()
        location = self.location_entry.get() or ""
        description = self.description_text.get("1.0", tk.END).strip()

        if not self._input_validation():
            self.status_label.config(text="Please fill in required fields  (╯ ▔皿▔)╯", fg="red")
            return

        job = JobData(
            company=company,
            job_title=position,
            location=location,
            job_description=description
        )
        template_selection = self.template_selection

        # Run workflows in background thread
        thread = threading.Thread(
            target=self._run_workflows,
            args=(job, template_selection),
            daemon=True
        )
        thread.start()

    def _input_validation(self):
        company = self.company_entry.get()
        position = self.position_entry.get()
        description = self.description_text.get("1.0", tk.END).strip()
        valid = True

        if not company:
            self.company_err.config(text="Company Required")
            valid = False
        if not position:
            self.position_err.config(text="Position Required")
            valid = False
        if not description:
            self.description_err.config(text="Required")
            valid = False

        return valid

    def _run_workflows(self, job: JobData, template_selection: TemplateSelection):
        self._set_ui_state(False)
        try:
            self._spinner_text = "Generating Resume  (～￣▽￣)～"
            self._start_spinner()
            self.resume_workflow.run(job, template_selection)

            if self.cover_var.get():
                self._spinner_text = "Generating Cover Letter  (～￣▽￣)～"
                self.cover_workflow.run(job, template_selection)

            self.root.after(0, self._stop_spinner())
            self.root.after(0, self._on_success(job))

        except Exception as e:
            self.root.after(0, self._stop_spinner())
            self.root.after(0, self._on_error(str(e)))

    def _on_success(self, job):
        self.status_label.config(
            text=f"Files generated successfully for {job.company} {job.job_title}  (-￣▽￣-)👍",
            fg="green"
        )

        self._set_ui_state(True)
        self.company_entry.delete(0, tk.END)
        self.position_entry.delete(0, tk.END)
        self.location_optional.config(text="(optional)")
        self.location_entry.delete(0, tk.END)
        self.description_text.delete("1.0", tk.END)


    def _on_error(self, message):
        self.status_label.config(text="Oopsie (￣ー￣* )... "+message, fg="red")
        self._set_ui_state(True)

    def _start_spinner(self):
        self._loading = True
        self._spinner_index = 0
        self._spin()

    def _spin(self):
        if not self._loading:
            return

        char = self._spinner_chars[self._spinner_index]
        self.status_label.config(text=f"{self._spinner_text}{char}", fg="blue")

        self._spinner_index = (self._spinner_index + 1) % len(self._spinner_chars)
        self.root.after(100, self._spin)  # 10 fps

    def _stop_spinner(self):
        self._loading = False

    def _set_ui_state(self, enabled: bool):
        state = "normal" if enabled else "disabled"
        inputs = [
            self.company_entry,
            self.position_entry,
            self.location_entry,
            self.description_text,
            self.cover_cb
        ]
        for inp in inputs:
            inp.config(state=state)

        # Template/prompt dropdowns: a category with no files stays disabled regardless
        # of the normal enable/disable cycle (there's nothing valid to pick).
        for field_name, combo in self.template_combos.items():
            if not self.template_maps[field_name]:
                combo.config(state="disabled")
            else:
                combo.config(state="readonly" if enabled else "disabled")

        # Generate stays disabled whenever any template/prompt category is missing files,
        # independent of the normal enable/disable cycle driven by workflow runs.
        if enabled and not self._templates_missing:
            self.generate_btn.config(state="normal")
        else:
            self.generate_btn.config(state="disabled")

    def run(self):
        """Start the Tkinter main loop"""
        self.root.mainloop()
