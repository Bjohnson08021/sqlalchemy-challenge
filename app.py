from flask import Flask, jsonify
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
import numpy as np
import pandas as pd
import datetime as dt

#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")
# reflect an existing database into a new model
base = automap_base()
base.prepare(engine,reflect=True)
measurement = base.classes.measurement
station = base.classes.station

#################################################
# Flask Setup
#################################################
app = Flask(__name__)

#################################################
# Flask Routes
#################################################

@app.route("/")
def welcome():
    """List all available api routes."""
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/start<br/>"
        f"/api/v1.0/start/end"
    )
@app.route("/api/v1.0/precipitation")
def precipitation():
    session = Session(engine)
    newest_info = session.query(measurement.date).order_by(measurement.date.desc()).first()
    year_ago = dt.date(2017,8,23) - dt.timedelta(days=365)
    last_year = session.query(measurement.date, measurement.prcp).\
    filter(measurement.date>= year_ago).\
    order_by(measurement.date).all()
    prcp_dict = dict(last_year)
    session.close()
    return jsonify(prcp_dict)

@app.route("/api/v1.0/stations")
def stations():
    session = Session(engine)
    beloved_stations= session.query(measurement.station, func.count(measurement.station)).\
    group_by(measurement.station).\
    order_by(func.count(measurement.station).desc()).all()
    all_stations=[]
    for station, count in beloved_stations: 
        all_stations.append(station)
    session.close()
    return jsonify(all_stations)
@app.route("/api/v1.0/tobs")
def tobs():
    session = Session(engine)
    year_ago = dt.date(2017,8,23) - dt.timedelta(days=365)
    active_station_temp = session.query(measurement.tobs).\
    filter(measurement.date>= year_ago).\
    filter(measurement.station == "USC00519281").\
    order_by(measurement.date).all()
    temp_list = list(np.ravel(active_station_temp))
    session.close()
    return jsonify(temp_list)
@app.route("/api/v1.0/<start>")
def beginning(start):
    session = Session(engine)
    trip_start = dt.datetime.strptime(start,"%Y-%m-%d")
    results = session.query(measurement.date, func.min(measurement.tobs), func.avg(measurement.tobs), func.max(measurement.tobs)).\
    filter(measurement.date >= trip_start).\
    group_by(measurement.date).all()

    tmin=results[0][1]
    tavg=results[0][2]
    tmax=results[0][3]
    
    
    start_list=[]
    for date, tmin, tavg, tmax in results:
        start_date_list={}
        start_date_list["Date"]=date
        start_date_list["TMIN"]=tmin
        start_date_list["TAVG"]=tavg
        start_date_list["TMAX"]=tmax
        start_list.append(start_date_list)
        
    session.close()
    return jsonify(start_list)
@app.route("/api/v1.0/<start>/<end>")
def roundtrip(start,end):
    session = Session(engine)
    trip_start = dt.datetime.strptime(start,"%Y-%m-%d")
    trip_end = dt.datetime.strptime(end,"%Y-%m-%d")
    results = session.query(measurement.date, func.min(measurement.tobs), func.avg(measurement.tobs), func.max(measurement.tobs)).\
    filter(measurement.date >= trip_start).filter(measurement.date <= trip_end).\
    group_by(measurement.date).all()

    tmin=results[0][1]
    tavg=results[0][2]
    tmax=results[0][3]
    
    
    start_list=[]
    for date, tmin, tavg, tmax in results:
        start_date_list={}
        start_date_list["Date"]=date
        start_date_list["TMIN"]=tmin
        start_date_list["TAVG"]=tavg
        start_date_list["TMAX"]=tmax
        start_list.append(start_date_list)
    
    session.close()
    return jsonify(start_list)
    
    



if __name__ == "__main__":
    app.run(debug=True)