# CP-129 2026 PDF Source Set

Put the new CP-129 drawing PDFs here without renaming them.

Expected filename examples:

```text
TYPE-01_D-1.pdf
TYPE-56_D-67.pdf
TYPE-56_D-67A.pdf
TYPE-A_M-11.pdf
UnknownType_M-42.pdf
```

After copying PDFs into this folder, rebuild the drawing index:

```powershell
.\.venv_gui\Scripts\python.exe python_app\tools\build_drawing_index.py
```

The generated index is:

```text
python_app/configs/drawing_index.json
```

The Type overview UI checks this source set first, then falls back to the
legacy PDFs in `python_app/assets/Type`.
