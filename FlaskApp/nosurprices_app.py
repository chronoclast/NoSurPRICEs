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
from nocache import nocache
# opencv related modules
from scipy.spatial import distance as dist
from imutils import perspective
from imutils import contours
import numpy as np
import argparse
import imutils
import cv2
from matplotlib import pyplot as plt
import time

UPLOAD_FOLDER = '/media/sf_D_DRIVE/emeli/Documents/ShapeRPic/Hackathon ReCoding Aviation/NoSurPRICEsflaskApp'
ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'])

app = Flask(__name__)
app.config['SECRET_KEY'] = "super secret string"
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config["CACHE_TYPE"] = "null"

bootstrap = Bootstrap(app)
moment = Moment(app)

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
		
class NameForm(Form):
	name = StringField("Which airline are you flying with?", validators=[Required()])
	sumbit = SubmitField("Submit")

class SelectAirline(Form):
	name = SelectField(u'Please select your airline', choices=[('Ryanair','Ryanair'),('EasyJet','EasyJet'), ('AirBerlin','AirBerlin'), ('Transavia','Transavia')])	
	sumbit = SubmitField("Submit")
	
class ConfirmButton(Form):
	confirm = SubmitField("Confirm")
	
@app.route("/", methods=["GET","POST"])
def index():
	form = SelectAirline()
	measurements = None
	if form.validate_on_submit():
			session['name'] = form.name.data
			if session['name'] == "Ryanair":
				session['measurements'] = "55 cm x 40 cm x 20 cm"
			return redirect(url_for('upload_front'))
	return render_template('index.html', current_time = datetime.utcnow(), form=form, name=session.get('name'), measurements = session.get('measurements'))


@app.route("/upload_front", methods=["GET","POST"])
@nocache
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
@nocache
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
@nocache	
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

	(_, cnts, _) = cv2.findContours(closed.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)	 

	# finding the trolley
	count = 0
	savecount = 0
	for c in cnts:
		count = count + 1
		print count
		print cv2.contourArea(c)
		# if the contour is not sufficiently large, ignore it
		area = cv2.contourArea(c)
		cntlimit = 120000
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
		
		if pixelsPerMetric is None:
			pixelsPerMetric = dB / 2

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
		return render_template("measure_luggage.html", angle=angle, saved=saved, name=name)		
	
@app.route("/user/<name>")
def user(name):
	return render_template('user.html', name=name)
	
@app.errorhandler(404)
def page_not_found(e):
	return render_template("404.html"), 404
	

if __name__ == "__main__":
	app.run(debug=True)	