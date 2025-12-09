# Python 3.12 Setup and Usage

This project requires Python 3.12. Below are the steps to install it with Homebrew, use it for scripts, manage dependencies, and work with the virtual environment.

## Install Python 3.12 (Homebrew)

```bash
brew install python@3.12
```

After install, use the explicit command:

```bash
python3.12 --version
```

## Running Python Scripts

Use the explicit interpreter:

```bash
python3.12 path/to/script.py
```

## Virtual Environment (`.venv`)

- The `start.sh` script creates/uses `.venv` automatically.
- Dependencies are installed into `.venv` (not system Python).
- To activate manually (optional for interactive use):
  - bash/zsh: `source .venv/bin/activate`
  - fish: `source .venv/bin/activate.fish`
- When activated, `python` and `pip` point to the venv.
- You can also run without activating by calling the venv binaries directly:
  
  ```bash
  .venv/bin/python your_script.py
  .venv/bin/pip install <pkg>
  ```

## Adding Dependencies

1. Append the package to `requirements.txt`, e.g.:
   
   ```text
   requests==2.32.3
   ```
2. Run the rebuild (installs deps into the venv and restarts the container):
   
   ```bash
   ./start.sh rebuild
   ```
   - Data volume is preserved; only containers/images are recreated.
3. Alternatively, to just install without rebuild:
   
   ```bash
   .venv/bin/pip install -r requirements.txt
   ```

## Quick Reference

- Install Python 3.12: `brew install python@3.12`
- Check version: `python3.12 --version`
- Activate venv (bash/zsh): `source .venv/bin/activate`
- Run script with venv Python: `.venv/bin/python script.py`
- Add dep: edit `requirements.txt` → `./start.sh rebuild`
