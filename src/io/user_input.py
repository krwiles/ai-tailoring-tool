import tkinter as tk
from tkinter import scrolledtext

from src.model import JobData
from src.workflow import ResumeWorkflow, CoverLetterWorkflow


class AppGUI:
    """
    Tkinter GUI for Resume & Cover Letter Generator
    """

    def __init__(self,
                 resume_workflow: ResumeWorkflow,
                 cover_letter_workflow: CoverLetterWorkflow
                 ):
        self.resume_workflow = resume_workflow
        self.cover_workflow = cover_letter_workflow

        self.root = tk.Tk()
        self.root.title("Resume & Cover Letter Generator")
        self._build_form()

    def _build_form(self):
        """Build all input fields and buttons with left alignment"""

        pad_opts = {"padx": 5, "pady": 5}

        # Company
        tk.Label(self.root, text="Company", anchor="w").grid(row=0, column=0, sticky="w", **pad_opts)
        self.company_entry = tk.Entry(self.root, width=60)
        self.company_entry.grid(row=0, column=1, sticky="w", **pad_opts)

        # Position
        tk.Label(self.root, text="Position", anchor="w").grid(row=1, column=0, sticky="w", **pad_opts)
        self.position_entry = tk.Entry(self.root, width=60)
        self.position_entry.grid(row=1, column=1, sticky="w", **pad_opts)

        # Location
        tk.Label(self.root, text="Location", anchor="w").grid(row=2, column=0, sticky="w", **pad_opts)
        self.location_entry = tk.Entry(self.root, width=60)
        self.location_entry.grid(row=2, column=1, sticky="w", **pad_opts)

        # Job Description label and ScrolledText
        tk.Label(self.root, text="Job Description", anchor="w").grid(row=3, column=0, sticky="nw", **pad_opts)
        self.description_text = scrolledtext.ScrolledText(self.root, width=60, height=15, wrap=tk.WORD)
        self.description_text.grid(row=3, column=1, sticky="nsew", **pad_opts)

        # Cover Letter checkbox
        self.cover_var = tk.BooleanVar(value=True)  # default ON
        cover_cb = tk.Checkbutton(
            self.root,
            text="Cover Letter",
            variable=self.cover_var
        )
        cover_cb.grid(row=4, column=0, sticky="w", **pad_opts)

        # Generate button, left-aligned
        generate_btn = tk.Button(self.root, text="Generate", command=self._generate)
        generate_btn.grid(row=4, column=1, sticky="w", **pad_opts)

        # Status/output label, left-aligned
        self.status_label = tk.Label(self.root, text="", fg="green", anchor="w", justify="left")
        self.status_label.grid(row=5, column=1, columnspan=2, sticky="w", **pad_opts)

        # Make job description expand if window resized
        self.root.grid_rowconfigure(3, weight=1)
        self.root.grid_columnconfigure(1, weight=1)

    def _generate(self):
        """Called when user clicks 'Generate'"""

        company = self.company_entry.get()
        position = self.position_entry.get()
        location = self.location_entry.get()
        description = self.description_text.get("1.0", tk.END).strip()

        if not company or not position or not location or not description:
            self.status_label.config(text="Please fill in all fields.", fg="red")
            return

        job = JobData(
            company=company,
            job_title=position,
            location=location,
            job_description=description
        )

        self.resume_workflow.run(job)
        if self.cover_var.get():
            self.cover_workflow.run(job)

        self.status_label.config(
            text=f"Files generated successfully for {job.company} {job.job_title}",
            fg="green"
        )

        self.company_entry.delete(0, tk.END)
        self.position_entry.delete(0, tk.END)
        self.location_entry.delete(0, tk.END)
        self.description_text.delete("1.0", tk.END)

    def run(self):
        """Start the Tkinter main loop"""
        self.root.mainloop()
