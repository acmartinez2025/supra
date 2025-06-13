# Supra eKEY Application Form

This project contains a complete frontend and backend implementation of the Supra eKEY Application form.

## Features

- UI using HTML5 + CSS
- Digital signature capture (mouse/finger)
- File upload (max 3 files, 15MB each, types: PDF, JPEG, HEIC)

- Dynamic fee calculator based on selections
- Email submission with PDF generation
- Fully Flask-compatible backend integration

## Deployment Instructions

1. Install Python dependencies:
   ```
   pip install -r requirements.txt
   ```

2. Add a `.env` file in the root with:
   ```
   MAIL_SERVER=smtp.gmail.com
   MAIL_PORT=587
   MAIL_USE_TLS=True
   MAIL_USERNAME=youremail@example.com
   MAIL_PASSWORD=yourpassword
   MAIL_DEFAULT_SENDER=youremail@example.com
   RECIPIENT_EMAIL=Supra@themls.com
   ```

3. Run the app locally:
   ```
   python app.py
   ```



## Files

- `templates/form.html` — The form UI
- `static/images/` — Logos and reference images
- `app.py` — Optional backend logic (Flask)
- `uploads/` — Temporarily stores submitted files

## Notes

- Signature is saved as a PNG in the generated PDF.
- All form data is processed securely via Flask backend.


