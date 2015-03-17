from datetime import datetime, timedelta
from flask_wtf import Form
from wtforms import TextField, SelectField
from wtforms.fields.html5 import DateField
from wtforms.validators import DataRequired

class Inputs(Form):
	reportTypeField = SelectField(u'Report Type', choices = [('monthly','Monthly'), ('weekly', 'Weekly')], validators=[DataRequired()])
	reportDateField = DateField(u'Report Date', format='%m/%d/%Y')
	hospitalField = SelectField(u'Hospital', choices = [], validators=[DataRequired()])
	deliveryDateField = DateField(u'Delivery Date', format='%m/%d/%Y')
	deliveryTypeField = SelectField(u'Delivery Type', choices=[('consumable','Consumables'), ('durable', 'Durables')],  validators=[DataRequired()])
	filenameField = TextField(u'Filename', validators=[DataRequired()])

def dstrp_u(date):
    date = datetime.strptime(date, "%Y-%m-%d")
    return date

def list_hospitals(filename):
    filename=filename
    xfile = [line.rstrip().split(',') for line in open(filename, 'rU').readlines()]

    hospital_list = []
    data = []

    for record in xfile[1:]:
    	hospital, date, cases, adultM, adultF, childM, childF, babyM, babyF, major, minor, otherCase, conflict, chronic, other, admission, referral, discharge, death = record
    	hospital_list.append(hospital)


    for names in set(hospital_list):
        option = (names, names)
        data.append(option)

    return data

def report(filename, hospital, delivery_date, type_of_support, report_type, report_begins ):

	#Makes Datetime compatible
	def dstrp(date):
		date = datetime.strptime(date, "%m/%d/%Y")
		return date

	#Calculates end date of support for Consumables delivery
	def calculate_consumables_end_date(begin_date):
		end_consumables = begin_date + timedelta(weeks = 6)
		return end_consumables

	#Calculates end date of support for Durable delivery
	def calculate_durables_end_date(beg_date):
		end_durables = beg_date + timedelta(weeks=12)
		while end_durables.day != beg_date.day:
			end_durables += timedelta(days=1)
		return end_durables

	def organize_by_date(file):
		for record in file[1:]:
			hospital, date, cases, adultM, adultF, childM, childF, babyM, babyF, major, minor, otherCase, conflict, chronic, other, admission, referral, discharge, death = record
			data_by_date.setdefault(hospital, {}).update({ date: {'cases': int(cases),'adultM': int(adultM), 'adultF':int(adultF), 'childM':int(childM), 'childF': int(childF), 'babyM':int(babyM), 'babyF':int(babyF), 'major': int(major), 'minor': int(minor), 'otherCase':int(otherCase), 'conflict':int(conflict), 'chronic':int(chronic),'other':int(other), 'admission':int(admission), 'referral': int(referral), 'discharge':int(discharge), 'death':int(death)}})
		return data_by_date

	filename = filename
	hospital = hospital
	delivery_date = delivery_date
	type_of_support = type_of_support
	report_type= report_type
	report_begins = report_begins


	ifile = [line.rstrip().split(',') for line in open(filename, 'rU').readlines()]

# 	indicators_lst = [ 'cases', 'adultM', 'adultF', 'childM', 'childF', 'babyM', 'babyF', 'major', 'minor', 'otherCase', 'conflict', 'chronic', 'other', 'admission', 'referral', 'discharge', 'death']

	#Organizes data by Date and includes indicators and their values
	data_by_date = {}

	organize_by_date(ifile)

	#Calculates the end date for a Consumable or Durable purchase
	if type_of_support.lower() == "consumable":
		end_date_support = calculate_consumables_end_date(delivery_date)
	elif type_of_support.lower() == "durable":
		end_date_support = calculate_durables_end_date(delivery_date)
	else:
	    end_date_support = None


	data_by_date_supported = {}

#   Filters out dates and the data to a new dictionary of which dates are supported
	for each_date in data_by_date[hospital]:
	    if dstrp(each_date)>=delivery_date and dstrp(each_date)<= end_date_support:
	        data_by_date_supported.setdefault(each_date,{}).update(data_by_date[hospital][each_date])

#   Chooses which type of report you want and then  calculates the end date of reporting
	if report_type.lower() == "weekly":
		report_ends = report_begins + timedelta(days=6)
	elif report_type.lower() == "monthly":
		day_after = "{0}/{1}/{2}".format(str(report_begins.month+1), str(report_begins.day), str(report_begins.year))
		if day_after[:2]=="13":
		    day_after = "01/{0}/{1}".format(str(report_begins.day), str(report_begins.year+1))
		    report_ends= dstrp(day_after) - timedelta(days=1)
		else:
		    report_ends= dstrp(day_after) - timedelta(days=1)


	data_by_date_reported = {}

# 	Filters  out the dates for the report and sets up the indicators and their values into a list so that they can be added up.
	for each_date in data_by_date_supported.keys():
		if dstrp(each_date)>=report_begins and dstrp(each_date)<=report_ends:
			for each_indicator in data_by_date_supported[each_date]:
				data_by_date_reported.setdefault(each_indicator, []).append(data_by_date_supported[each_date][each_indicator])


	return data_by_date_reported



