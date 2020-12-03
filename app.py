
import datetime as dt
import numpy as np
import pandas as pd

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify


#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
#reflect the tables
Base.prepare(engine, reflect=True)

# Save references to each table
Measurement = Base.classes.measurement
Station = Base.classes.station

# Create our session (link) from Python to the DB
session = Session(engine)

#################################################
# Flask Setup
#################################################
app = Flask(__name__)
# Calculate the date 1 year ago from last date in database
engine.execute("SELECT * from Measurement limit 10").fetchall()
maxdate=engine.execute('SELECT max(date) from Measurement').fetchall()
ldate=maxdate[0]
curyeardate=ldate[0]
prevyeardate = dt.datetime.strptime (curyeardate, '%Y-%m-%d') - dt.timedelta(days=365)
prevyeardates=str(prevyeardate.date())
#
#
#################################################
# Flask Routes
#################################################

@app.route("/")
def welcome():
    return (
        f"Welcome to the Hawaii Climate Analysis API!<br/>"
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/temp/start/end"
    )


@app.route("/api/v1.0/precipitation")
def precipitation():
    """Return the precipitation data for the last year"""
     
    precipit = (session.query(Measurement.date, Measurement.prcp, Measurement.station).filter(Measurement.date > prevyeardates).order_by(Measurement.date).all())   

    session.close()

    PrecipitData=[]

    for data in precipit:
        PrecipitDict={data.date: data.prcp, "Station": data.station}
        PrecipitData.append(PrecipitDict)

    return jsonify(PrecipitData)



@app.route("/api/v1.0/stations")
def stations():
    """Return a list of stations."""
    Stationlist = session.query(Station.name).all()
    session.close()
    # Unravel results into a 1D array and convert to a list
    allstations = list(np.ravel(Stationlist))
    return jsonify(allstations)





@app.route("/api/v1.0/tobs")
def temp_monthly():
  
    # Query the primary station for all tobs from the last year Time of Observation Bias
    TOBs = session.query(Measurement.tobs).filter(Measurement.station == 'USC00519281').filter(Measurement.date >= prevyeardate).all()
    session.close()

    # Unravel results into a 1D array and convert to a list
    temps = list(np.ravel(TOBs))

    # Return the results
    return jsonify(temps=temps)


@app.route("/api/v1.0/temp/<start>")
@app.route("/api/v1.0/temp/<start>/<end>")
def stats(start=None, end=None):
    """Return TMIN, TAVG, TMAX."""

    # Select statement
    sel = [func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)]

    if not end:
        # calculate TMIN, TAVG, TMAX for dates greater than start
        Tempstart = session.query(*sel).filter(Measurement.date >= prevyeardates).all()
        session.close()
        # Unravel results into a 1D array and convert to a list
    
        temps = []                       
        for temp in Tempstart:
            datedic = {}
        
            datedic["Low Temp"] = temp[0]
            datedic["Avg Temp"] = temp[1]
            datedic["High Temp"] = temp[2]
            temps.append(datedic)

        return jsonify(temps)

    # calculate TMIN, TAVG, TMAX with start and stop
    Tempsend = session.query(*sel).filter(Measurement.date >= prevyeardates).filter(Measurement.date <= curyeardate).all()
    session.close()
    # Unravel results into a 1D array and convert to a list
    temps = []                       
    for temp in Tempsend:
        datedic = {}
        
        datedic["Low Temp"] = temp[0]
        datedic["Avg Temp"] = temp[1]
        datedic["High Temp"] = temp[2]
        temps.append(datedic)
    

    return jsonify(temps=temps)


if __name__ == '__main__':
    app.run()
