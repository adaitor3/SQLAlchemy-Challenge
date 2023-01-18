import pandas as pd 
import numpy as np
import sqlalchemy 
import datetime as dt
from sqlalchemy import create_engine, func
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
import flask
from flask import Flask , jsonify

# Database setup 
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# Reflect existing database into new model 
Base = automap_base()
# Reflect the tables
Base.prepare(engine, reflect = True)

# Save reference to the table 
measurement_df = Base.classes.measurement
station_df = Base.classes.station

# Setting up Flask 
app = Flask(__name__)

# Define the routes users can take 
@app.route("/")
def welcome():
    """List all available API routes."""
    return (
        f"Available Routes: 1 <br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/start<br/>"
        f"/api/v1.0/start/end<br/>"
    )

# Converting the query results from the precipitation analysis to a dictionary using date as the key and prcp as the value 
# Then return JSON representation

@app.route("/api/v1.0/precipitation")
def precipitation():
# Last 12 months of precipitation data 
    session = Session(engine)
    precip_results = session.query(measurement_df.date, measurement_df.prcp).filter(measurement_df.date >=('2016-08-23')).\
    order_by(measurement_df.date).all()
    
    session.close()
    return jsonify(dict(precip_results))

# Return a JSON list of stations from the dataset
# Create session from link to DB
@app.route("/api/v1.0/stations")
def stations():
    session = Session(engine)
    stations = session.query(station_df.station).all()
    session.close()
# Return JSON list
    stations_list = list(np.ravel(stations))
    return jsonify(stations_list)

# Querying dates and temperature observation of the most active stations data from prev year. 
@app.route("/api/v1.0/tobs")
def tobs():
    session = Session(engine)
# Temperature observation from past year of most active station. 
    last_12_mo =  dt.date(2017,8,23) - dt.timedelta(days = 365)
    temp_results = session.query(measurement_df.date, measurement_df.tobs).\
        filter(measurement_df.date >= last_12_mo).\
        filter(measurement_df.station == 'USC00519281').all()
# Return JSON 
    session.close()
    return jsonify(dict(temp_results))

# Get min, avg, max for dates greater than or equal to start date 
@app.route("/api/v1.0/<start>")
def temp(start):
    session = Session(engine)
    min_temp = session.query(func.min(measurement_df.tobs)).filter(measurement_df.date >= start).all()
    max_temp = session.query(func.max(measurement_df.tobs)).filter(measurement_df.date >= start).all()
    avg_temp = session.query(func.avg(measurement_df.tobs)).filter(measurement_df.date >= start).all()

    session.close()
    return jsonify(f"{min_temp}, {max_temp}, {avg_temp}")
    

# For a specified start date and end date, calculate TMIN, TAVG, and TMAX for the dates from the start date to the end date, inclusive.
@app.route("/api/v1.0/<start>/<end>")
def temps(start, end): 
    session = Session(engine) 
    max_temps = session.query(func.max(measurement_df.tobs)).filter(measurement_df.date >= start).filter(measurement_df.date <= end).all()
    min_temps = session.query(func.min(measurement_df.tobs)).filter(measurement_df.date >= start).filter(measurement_df.date <= end).all()
    avg_temps = session.query(func.avg(measurement_df.tobs)).filter(measurement_df.date >= start).filter(measurement_df.date <= end).all()

    session.close()
    return jsonify(f"{max_temps}, {min_temps}, {avg_temps}")


if __name__ == '__main__':
    app.run(debug=True)
    
