# Running the Campus Resource Hub

## Quick Start

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Run the application:**
   ```bash
   python app.py
   ```

3. **Access the app:**
   - Open your browser to: http://127.0.0.1:5000
   - Default admin credentials:
     - Username: `admin` or `admin@campushub.local`
     - Password: `Password1`

## Troubleshooting

If you encounter errors when running `python app.py`, please:

1. **Check Python version:** Requires Python 3.10+
   ```bash
   python --version
   ```

2. **Verify all dependencies are installed:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Test app creation:**
   ```bash
   python test_app_start.py
   ```

4. **Test routes:**
   ```bash
   python test_run.py
   ```

5. **Check for specific errors:**
   - Database errors: Ensure you have write permissions in the project directory (for `site.db`)
   - Import errors: Make sure you're running from the project root directory
   - Port conflicts: If port 5000 is in use, modify `app.py` to use a different port

## Common Issues

### "Module not found" errors
- Ensure you're in the project root directory
- Run: `pip install -r requirements.txt`

### Database errors
- Delete `site.db` and let the app recreate it
- Check file permissions in the project directory

### Port already in use
- Change the port in `app.py`: `app.run(debug=True, port=5001)`

