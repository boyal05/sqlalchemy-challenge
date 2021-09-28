from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
from sqlalchemy.sql import exists 

from flask import Flask, jsonify
import numpy as np
import datetime as dt
import sqlalchemy
import re

# create engine to hawaii.sqlite
engine = create_engine("sqlite:///Resources/hawaii.sqlite")
# reflect an existing database into a new model
base = automap_base()
# reflect the tables
base.prepare(engine, reflect=True)
# Save references to each table
Measurement = base.classes.measurement
Station = base.classes.station


# Create the app
app = Flask(__name__)

# Home Page
@app.route("/")
def home():
    print("")
    return (f"\tHello there, Welcome to the 'Home' page. Routes availables:<br/>\n"
            f"\tPrecipitation: <a href=/api/v1.0/precipitation>/api/v1.0/precipitation</a><br/>\n"
            f"\tStations: <a href=/api/v1.0/stations>/api/v1.0/stations</a><br/>\n"
            f"\tTemperatures: <a href=/api/v1.0/tobs>/api/v1.0/tobs</a><br/>\n"
            f"\tTemperatures with starting date in YYYY-MM-DD format: /api/v1.0/start<br/>\n"
            f"\tTemperatures with the range of dates in YYYY-MM-DD format: /api/v1.0/start/end<br/>\n")

# Defining Routes

@app.route("/api/v1.0/precipitation")
def precipitation():
    prcp_lists = []
    session = Session(engine)

    # Retrieve the data and precipitation scores
    prcp_data = session.query(Measurement.date, Measurement.prcp).order_by(Measurement.date).all()
    
    # Converting the query results to a dictionary.
    for item in prcp_data:
        prcp_dic = {}
        prcp_dic["prcp"] = item[0]
        prcp_dic["date"] = item[1]
        prcp_lists.append(prcp_dic)

    session.close()
    return jsonify(prcp_lists)

@app.route("/api/v1.0/stations")
def stations():

    session = Session(engine)

    # Retrieve the data and precipitation scores
    results = session.query(Station.name).order_by(Station.name).all()
    
    stations_list = list(np.ravel(results))

    session.close()
    return jsonify(stations_list)

@app.route("/api/v1.0/tobs")
def tobs():
    tobs_year = []
    session = Session(engine)
    latest_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()
    years = dt.date(2017, 8, 23) - dt.timedelta(days=365)

    # Perform a query to retrieve the data and precipitation scores
    results = session.query(Measurement.date, Measurement.tobs).\
        filter(Measurement.station == 'USC00519281').\
        filter(Measurement.date >= years).\
        order_by(Measurement.date).all()
    
    # Convert the query results to a dictionary using date as the key and prcp as the value.
    
    for item in results:
        tobs_dic = {}
        tobs_dic["tobs"] = item[0]
        tobs_dic["date"] = item[1]
        
        tobs_year.append(tobs_dic)
    session.close()
    return jsonify(tobs_year)


@app.route("/api/v1.0/<start>") 
def start_input(start):
    # Create our session (link) from Python to the DB
    session = Session(engine)
    
    # Validate start date 
    valid_start_date = session.query(exists().where(Measurement.date == start)).scalar()
    if valid_start_date == True:
        results = (session.query(func.min(Measurement.tobs),func.max(Measurement.tobs),func.avg(Measurement.tobs)).filter(Measurement.date >= start).all())
        tob_max = results[0][1]
        tob_avg = "{:.1f}".format(results[0][2])
        tob_min = results[0][0]
        
        result_printout =( ['Start Date: ' + start, 'Min_Temperature: ' + str(tob_min), 'Max_Temperature: '+ str(tob_max),'Average_Temperature: '+ str(tob_avg)])
        return jsonify(result_printout)
    session.close()
    return jsonify({"error": f"Input date {start} not valid"}), 404
   

@app.route("/api/v1.0/<start>/<end>")
def start_end_input(start, end):
    session = Session(engine)

    # Validate end date 
    valid_end_date = session.query(exists().where(Measurement.date == end)).scalar()

    # Validate start date 
    valid_start_date = session.query(exists().where(Measurement.date == start)).scalar()
    

    if valid_start_date==True and valid_end_date == True and end>=start:
        results = session.query(func.min(Measurement.tobs),func.max(Measurement.tobs),func.avg(Measurement.tobs)).filter(Measurement.date >= start).filter(Measurement.date <= end).all()
        tob_max = results[0][1]
        tob_avg = "{:.1f}".format(results[0][2])
        tob_min = results[0][0]
        result_printout =( ['Start Date: ' + start, 'End Date: ' + end, 'Min_Temperature: '  + str(tob_min), 'Max_Temperature: ' + str(tob_max), 'Average_Temperature: ' + str(tob_avg)])
        return jsonify(result_printout)        
    return jsonify({"error": f"Input start date {start} or input end date {end} not valid. Also make sure the end date is not before the start date."}), 404
    session.close()
if __name__ == "__main__":
    app.run(debug=True)
