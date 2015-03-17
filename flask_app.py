import os
from flask import Flask, render_template, request, redirect, url_for
from reporting_tool import report, list_hospitals, Inputs, dstrp_u
from flask import send_from_directory
from werkzeug import secure_filename

app = Flask(__name__)

app.secret_key =''
app.debug = True

@app.route('/')
def hello_world():
    return render_template('index.html')

UPLOAD_FOLDER = '/home/shinson/mysite/uploads'
ALLOWED_EXTENSIONS = set(['csv'])
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS

@app.route('/upload', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        file = request.files['file']
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            return redirect(url_for('input_data', filename=filename))
    return render_template('upload1.html')


@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

@app.route('/input_data', methods=['GET'])
def input_data():
    if request.method == 'GET':
        filename = 'mysite/uploads/' + request.args.get('filename')
        form = Inputs()
        form.hospitalField.choices = list_hospitals(filename)
        if form.validate_on_submit():
            return redirect('/output_data')
    return render_template('input_data.html', form=form, filename=filename)


@app.route('/output_data', methods=['GET', 'POST'])
def output_data():
    indicators = [ 'hospital', 'cases', 'adultM', 'adultF', 'childM', 'childF', 'babyM', 'babyF', 'major', 'minor', 'otherCase', 'conflict', 'chronic', 'other', 'admission', 'referral', 'discharge', 'death']
    display=[]
    # filename = request.args.get['filenameField']
    filename = request.args.get('filenameField')
    report_type = request.args.get('reportTypeField')
    report_date = dstrp_u(request.args.get('reportDateField'))
    hospitals= request.args.getlist('hospitalField')
    delivery_dates = request.args.getlist('deliveryDateField')
    delivery_types = request.args.getlist('deliveryTypeField')

    for hospital, delivery_date, delivery_type in zip(hospitals, delivery_dates, delivery_types):
        display.extend([report(filename, hospital, dstrp_u(delivery_date), delivery_type, report_type, report_date)])

    return render_template('output_data.html', display=display, indicators=indicators, hospitals = hospitals)
