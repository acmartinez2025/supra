import os
from flask import Flask, request, jsonify, render_template, make_response
from flask_mail import Mail, Message
from dotenv import load_dotenv
from werkzeug.utils import secure_filename
from xhtml2pdf import pisa
from io import BytesIO
from datetime import datetime

# Load environment variables from .env
load_dotenv()


app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 15 * 1024 * 1024  # Limit upload size to 15 MB

# Flask-Mail Configuration
app.config.update(
    MAIL_SERVER=os.getenv("MAIL_SERVER", "smtp.gmail.com"),
    MAIL_PORT=int(os.getenv("MAIL_PORT", 587)),
    MAIL_USE_TLS=os.getenv("MAIL_USE_TLS", "True") == "True",
    MAIL_USERNAME=os.getenv("MAIL_USERNAME"),
    MAIL_PASSWORD=os.getenv("MAIL_PASSWORD"),
    MAIL_DEFAULT_SENDER=os.getenv("MAIL_DEFAULT_SENDER")
)

mail = Mail(app)

# Create an uploads folder if it doesn't exist
UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), 'uploads')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def generate_pdf_from_html(template_name, context):
    html = render_template(template_name, **context)
    result = BytesIO()
    pdf = pisa.CreatePDF(BytesIO(html.encode("utf-8")), dest=result)
    if not pdf.err:
        result.seek(0)
        return result
    return None

@app.route('/')
def show_form():
    return render_template('form.html')


# Route to serve the success page
@app.route('/success')
def success():
    return render_template('success.html')

@app.route('/submit', methods=['POST'])
def submit_form():
    try:
        print("🔧 Received request:", request.method)
        print("🔧 Form keys:", list(request.form.keys()))
        print("🔧 Files:", [file.filename for file in request.files.getlist('upload_files')])

        form_data = request.form
        form_data = form_data.to_dict(flat=True)
        form_data["acknowledgement"] = "Yes, user acknowledged the terms and conditions."
        files = request.files.getlist('upload_files')[:3]
        recipient = os.getenv("RECIPIENT_EMAIL", "supra@themls.com")

        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        subject = f"📩 New Supra eKEY Application — {form_data.get('name', 'Applicant')} @ {timestamp}"

        # Compose email
        msg = Message(subject, recipients=[recipient])
        msg.body = "Attached is the submitted Supra eKEY Application and documents."

        # Attach files
        for file in files:
            if file.filename:
                filename = secure_filename(file.filename)
                file_path = os.path.join(UPLOAD_FOLDER, filename)
                file.save(file_path)
                with open(file_path, "rb") as f:
                    msg.attach(filename, file.content_type or "application/octet-stream", f.read())

        pdf_stream = generate_pdf_from_html("pdf_template.html", form_data)
        if pdf_stream:
            msg.attach("Supra_Application.pdf", "application/pdf", pdf_stream.read())

        mail.send(msg)

        # Send PDF copy to the user if requested
        if form_data.get("send_copy_to_user") == "yes" and form_data.get("email"):
            user_email = form_data.get("email")
            user_msg = Message("📄 Your Supra eKEY Application Copy", recipients=[user_email])
            user_msg.body = "Attached is a PDF copy of your submitted Supra eKEY Application."
            
            # Regenerate PDF for user
            pdf_stream.seek(0)
            user_msg.attach("Supra_Application.pdf", "application/pdf", pdf_stream.read())
            
            mail.send(user_msg)

        return render_template("success.html", name=form_data.get("name"))

    except Exception as e:
        import traceback
        print("❌ Error while processing form:", e)
        traceback.print_exc()
        return render_template("error.html", message=str(e)), 500



if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5001)
