# Contributing Guidelines

Thanks for your interest in contributing!

This repository is a compact FastAPI project used for learning and demonstration purposes.  
Contributions are welcome for small improvements, bug fixes, and documentation clarity.

---

## 🧩 How to Contribute

1. **Fork** the repository and create a new branch:
   ```bash
   git checkout -b feature/my-change
   ```

2. **Make your edits** — keep them focused and self-contained.  
   - For code: follow the existing structure and naming style.  
   - For docs: keep explanations concise and factual.

3. **Test locally**  
   Run the app to ensure everything still works:
   ```bash
   uvicorn main:app --reload
   ```

4. **Commit and push**
   ```bash
   git commit -m "feat: describe your change briefly"
   git push origin feature/my-change
   ```

5. **Open a Pull Request**  
   Describe what you changed and why.

---

## 🧱 Coding Style

- Follow **PEP 8** conventions.  
- Keep functions small and readable.  
- Use descriptive docstrings — they appear automatically in the API docs.  
- Group related sections with clear headers (e.g., `# === Auth Utilities ===`).

---

## ⚙️ Environment

```bash
pip install -r requirements.txt
uvicorn main:app --reload
```

Database: SQLite (`data.db`)  
Python: 3.10 + recommended

---

## 📄 License

By contributing, you agree that your work will be licensed under the [MIT License](LICENSE).
