# flask related modules 
from flask import Flask, request, make_response, redirect, render_template, session, url_for, flash
from flask_bootstrap import Bootstrap
from flask_moment import Moment
from flask_wtf import Form
from wtforms import StringField, SubmitField, SelectField
from wtforms.validators import Required
from datetime import datetime
import os
from werkzeug.utils import secure_filename
from flask import send_from_directory
# opencv related modules
from scipy.spatial import distance as dist
from imutils import perspective
from imutils import contours
import numpy as np
import imutils
import cv2
# other modules
import requests
import json
# cloudant modules
from cloudant.client import Cloudant
from cloudant.error import CloudantException
from cloudant.result import Result, ResultByKey

UPLOAD_FOLDER = '/media/sf_D_DRIVE/emeli/Documents/ShapeRPic/Hackathon ReCoding Aviation/NoSurPRICEsflaskApp'
ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'])

app = Flask(__name__)
app.config['SECRET_KEY'] = "super secret string"
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config["CACHE_TYPE"] = "null"

serviceUsername = "<YOUR_USER_NAME>-bluemix"
servicePassword = "<YOUR_PASSWORD>"
serviceURL = "https://<YOUR_USER_NAME>-bluemix.cloudant.com"
bootstrap = Bootstrap(app)
moment = Moment(app)

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
		
class NameForm(Form):
	name = StringField("Which airline are you flying with?", validators=[Required()])
	sumbit = SubmitField("Submit")

class SelectAirline(Form):
	name = SelectField(u'Please select your airline', choices=[('Ryanair','Ryanair'),('easyJet','easyJet'), ('AerLingus','AerLingus'), ('AirFrance','AirFrance'), ('Delta','Delta'), ('KLM','KLM'), ('Lufthansa','Lufthansa'), ('Vueling','Vueling'), ('Flybe','Flybe'), ('Norwegian','Norwegian'), ('Qatar','Qatar')])	
	sumbit = SubmitField("Submit")
	
class ConfirmButton(Form):
	confirm = SubmitField("Confirm")
	
@app.route("/", methods=["GET","POST"])
def index():
	form = SelectAirline()
	measurements = None
	if form.validate_on_submit():
			session['name'] = form.name.data
			f = open('static/airline.txt', 'w')
			f.write(session['name'])
			f.close()
			return redirect(url_for('upload_front'))
	return render_template('index.html', current_time = datetime.utcnow(), form=form, name=session.get('name'), measurements = session.get('measurements'))


@app.route("/upload_front", methods=["GET","POST"])
def upload_front():
	saved = None
	path = None
	url = None
	if request.method == 'POST':
	# check if the post request has the file part
		if 'file' not in request.files:
			flash('No file part')
			return redirect(request.url)
		file = request.files['file']
		# if user does not select file, browser also
		# submit a empty part without filename
		if file.filename == '':
			flash('No front pic added')
			return redirect(request.url)
		if file and allowed_file(file.filename):
			file.save(os.path.join(app.config['UPLOAD_FOLDER'], "static/front.jpg"))
			path = "static/front.jpg"
			saved = True
			url = url_for('upload_side')
	return render_template('upload.html', angle="front", path=path, saved=saved, url=url)	

@app.route("/upload_side", methods=["GET","POST"])
def upload_side():
	saved = None
	path = None
	url = None
	if request.method == 'POST':
	# check if the post request has the file part
		if 'file' not in request.files:
			flash('No file part')
			return redirect(request.url)
		file = request.files['file']
		# if user does not select file, browser also
		# submit a empty part without filename
		if file.filename == '':
			flash('No side pic added')
			return redirect(request.url)
		if file and allowed_file(file.filename):
			file.save(os.path.join(app.config['UPLOAD_FOLDER'], "static/side.jpg"))
			path = "static/side.jpg"
			saved = True
			url = "measure_luggage/front"
	return render_template('upload.html', angle="side", path=path, saved=saved, url=url)	

def midpoint(ptA, ptB):
	return ((ptA[0] + ptB[0]) * 0.5, (ptA[1] + ptB[1]) * 0.5)	

@app.route("/measure_luggage/<angle>")
def measure_luggage(angle):
	name = None
	saved = None
	filename = "static/"+angle+".jpg"
	#reading the image 
	image = cv2.imread(filename)
	image = cv2.GaussianBlur(image, (7, 7), 0)
	edged = cv2.Canny(image, 35, 70)
	#edged = cv2.Canny(image, 50, 100)
	 
	#applying closing function 
	kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (7, 7))
	closed = cv2.morphologyEx(edged, cv2.MORPH_CLOSE, kernel)
	# finding the contours for retrieving the measurement object (white object)
	lower = np.array([190,190,190])
	upper = np.array([255,255,255])
	shapeMask = cv2.inRange(image, lower, upper) 
	pixelsPerMetric = None
	(_, contours, _) = cv2.findContours(shapeMask.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

	# finding the measurement object
	count = 0
	savecount = 0
	for cnt in contours:
		count = count+1
		area = cv2.contourArea(cnt)
		cntlimit = 10000
		if area < cntlimit:
			continue
		orig = image.copy()	
		cv2.drawContours(orig, [cnt], -1, (0, 255, 0), 2)
		box = cv2.minAreaRect(cnt)
		box = cv2.cv.BoxPoints(box) if imutils.is_cv2() else cv2.boxPoints(box)
		box = np.array(box, dtype="int")
		box = perspective.order_points(box)
		cv2.drawContours(orig, [box.astype("int")], -1, (0, 255, 0), 2)
		for (x, y) in box:
			cv2.circle(orig, (int(x), int(y)), 5, (0, 0, 255), -1)
		(tl, tr, br, bl) = box
		(tltrX, tltrY) = midpoint(tl, tr)
		(blbrX, blbrY) = midpoint(bl, br)
		# compute the midpoint between the top-left and top-right points,
		# followed by the midpoint between the top-righ and bottom-right
		(tlblX, tlblY) = midpoint(tl, bl)
		(trbrX, trbrY) = midpoint(tr, br)

		# draw the midpoints on the orig
		cv2.circle(orig, (int(tltrX), int(tltrY)), 5, (255, 0, 0), -1)
		cv2.circle(orig, (int(blbrX), int(blbrY)), 5, (255, 0, 0), -1)
		cv2.circle(orig, (int(tlblX), int(tlblY)), 5, (255, 0, 0), -1)
		cv2.circle(orig, (int(trbrX), int(trbrY)), 5, (255, 0, 0), -1)

		# draw lines between the midpoints
		cv2.line(orig, (int(tltrX), int(tltrY)), (int(blbrX), int(blbrY)),
			(255, 0, 255), 3)
		cv2.line(orig, (int(tlblX), int(tlblY)), (int(trbrX), int(trbrY)),
			(255, 0, 255), 3)

		# compute the Euclidean distance between the midpoints
		dA = dist.euclidean((tltrX, tltrY), (blbrX, blbrY))
		dB = dist.euclidean((tlblX, tlblY), (trbrX, trbrY))
		
		if pixelsPerMetric is None:
			pixelsPerMetric = dB / 10

		# compute the size of the object
		dimA = dA / pixelsPerMetric
		dimB = dB / pixelsPerMetric

		# draw the object sizes on the orig
		cv2.putText(orig, "{:.1f}cm".format(dimA),
			(int(tltrX - 15), int(tltrY - 10)), cv2.FONT_HERSHEY_SIMPLEX,
			2, (255, 255, 255), 3)
		cv2.putText(orig, "{:.1f}cm".format(dimB),
			(int(trbrX + 10), int(trbrY)), cv2.FONT_HERSHEY_SIMPLEX,
			2, (255, 255, 255), 3)
		break

	(_, cnts, _) = cv2.findContours(closed.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)	 

	# finding the trolley
	if pixelsPerMetric is None:
		return "<h1> We did not spot your coaster </h1>"
	count = 0
	savecount = 0
	for c in cnts:
		count = count + 1
		print count
		print cv2.contourArea(c)
		# if the contour is not sufficiently large, ignore it
		area = cv2.contourArea(c)
		cntlimit = 170000
		if area < cntlimit:
			continue
		# compute the rotated bounding box of the contour
		orig = image.copy()
		box = cv2.minAreaRect(c)
		box = cv2.cv.BoxPoints(box) if imutils.is_cv2() else cv2.boxPoints(box)
		box = np.array(box, dtype="int")

		box = perspective.order_points(box)
		cv2.drawContours(orig, [box.astype("int")], -1, (0, 255, 0), 2)

		# loop over the original points and draw them
		for (x, y) in box:
			cv2.circle(orig, (int(x), int(y)), 5, (0, 0, 255), -1)

		(tl, tr, br, bl) = box
		(tltrX, tltrY) = midpoint(tl, tr)
		(blbrX, blbrY) = midpoint(bl, br)

		(tlblX, tlblY) = midpoint(tl, bl)
		(trbrX, trbrY) = midpoint(tr, br)

		# draw the midpoints on the image
		cv2.circle(orig, (int(tltrX), int(tltrY)), 5, (255, 0, 0), -1)
		cv2.circle(orig, (int(blbrX), int(blbrY)), 5, (255, 0, 0), -1)
		cv2.circle(orig, (int(tlblX), int(tlblY)), 5, (255, 0, 0), -1)
		cv2.circle(orig, (int(trbrX), int(trbrY)), 5, (255, 0, 0), -1)

		# draw lines between the midpoints
		cv2.line(orig, (int(tltrX), int(tltrY)), (int(blbrX), int(blbrY)),
			(255, 0, 255), 3)
		cv2.line(orig, (int(tlblX), int(tlblY)), (int(trbrX), int(trbrY)),
			(255, 0, 255), 3)

		# compute the Euclidean distance between the midpoints
		dA = dist.euclidean((tltrX, tltrY), (blbrX, blbrY))
		dB = dist.euclidean((tlblX, tlblY), (trbrX, trbrY))

		# compute the size of the object
		dimA = dA / pixelsPerMetric
		dimB = dB / pixelsPerMetric

		# draw the object sizes on the image
		cv2.putText(orig, "{:.1f}cm".format(dimA),
			(int(tltrX - 15), int(tltrY - 10)), cv2.FONT_HERSHEY_SIMPLEX,
			2, (255, 255, 255), 3)
		cv2.putText(orig, "{:.1f}cm".format(dimB),
			(int(trbrX + 10), int(trbrY)), cv2.FONT_HERSHEY_SIMPLEX,
			2, (255, 255, 255), 3)
			
		# show the output orig
		name = "static/measured_"+angle+".jpg"
		cv2.imwrite(name, orig)
		name = "http://localhost:5000/static/measured_"+angle+".jpg"
		saved = True
		url_good = "http://localhost:5000/calculation/"+angle
		url_bad = "http://localhost:5000/measure_luggage/"+angle
		textfile = "static/"+angle+"_measurements.txt"
		f = open(textfile, 'w')
		f.write(str(dimA)+";")
		f.write(str(dimB))
		f.close()
		return render_template("measure_luggage.html", angle=angle, saved=saved, name=name, url_good=url_good, url_bad=url_bad)		

@app.route("/calculation/<angle>")
def calculation(angle):
	if angle == "front":
		return redirect("measure_luggage/side")
	if angle == "side":
		h_and_w = open('static/front_measurements.txt', 'r').readlines()
		h_and_w = h_and_w[0].split(";")
		if float(h_and_w[0]) > float(h_and_w[1]):
			h = float(h_and_w[0])
			w = float(h_and_w[1])
		else:
			w = float(h_and_w[0])
			h = float(h_and_w[1])
		h_and_d = open('static/side_measurements.txt', 'r').readlines()
		h_and_d = h_and_d[0].split(";")
		if float(h_and_d[0]) > float(h_and_d[1]):
			d = float(h_and_d[1])	
		else:
			d = float(h_and_d[0])
		airline = open('static/airline.txt', 'r').readlines()
		r = requests.get('https://389c0932-8ba8-406b-8730-ff8b76623111-bluemix.cloudant.com/maxsize/'+airline[0])
		response = json.loads(r.text)
		allowed_h = response['baggageHeight']
		allowed_w = response['baggageWidth']
		allowed_d = response['baggageDepth']
		your_measurements = str(round(h,2))+" x "+str(round(w,2))+" x "+str(round(d,2))
		airline_measurements = str(allowed_h)+" x "+str(allowed_w)+" x "+str(allowed_d)
		if h > allowed_h:
			approved = False
			send_data(approved, h, w, d)
			return render_template('pity.html', your_measurements=your_measurements,airline_measurements=airline_measurements,airline=airline[0])
		if w > allowed_w:
			approved = False
			send_data(approved, h, w, d)
			return render_template('pity.html', your_measurements=your_measurements,airline_measurements=airline_measurements,airline=airline[0])
		if d > allowed_d:
			approved = False
			send_data(approved, h, w, d)
			return render_template('pity.html', your_measurements=your_measurements,airline_measurements=airline_measurements,airline=airline[0])
		approved = True
		send_data(approved, h, w, d)
		return render_template('succes.html', your_measurements=your_measurements,airline_measurements=airline_measurements,airline=airline[0])
	
def send_data(approved, h, w, d):
	# Use the Cloudant library to create a Cloudant client.
	client = Cloudant(serviceUsername, servicePassword, url=serviceURL)

	# Connect to the server.
	client.connect()

	# This is the name of the database we are working with.
	databaseName = "baggage"

	# Connect to the database.
	myDatabaseDemo = client[databaseName]
	
	baggage_id_txt = open('static/baggage_id.txt', 'r').readlines()
	baggage_id = baggage_id_txt[0]
	
	# Create a JSON document that stores all the data
	jsonDocument = {
		'_id': str(baggage_id),
		'height': h,
		'width': w,
		'depth': d,
		'approved': approved
		}

	# Create a new entry on the database using the API.
	newDocument = myDatabaseDemo.create_document(jsonDocument)
	
	# replace the zero index with the latest input
	zero = myDatabaseDemo['0']
	zero['count'] = baggage_id
	zero.save()

	# Disconnect from the server
	client.disconnect()	
	
	baggage_id = int(baggage_id)+1
	baggage_id_text = open('static/baggage_id.txt', 'w')
	baggage_id_text.write(str(baggage_id))
	baggage_id_text.close()

	
@app.errorhandler(404)
def page_not_found(e):
	return render_template("404.html"), 404	
	
if __name__ == "__main__":
	app.run(debug=True)	