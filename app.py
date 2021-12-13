# 1. import Flask
import numpy as np

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify

#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

# Save reference to each table
Measurement = Base.classes.measurement
Station = Base.classes.station

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
        f"/api/v1.0/<start_date><br/>"
        f"/api/v1.0/<start_date>/<end_date><br/>"
        f"Dates muste be entered in the following manner yyyy-mm-dd<br/>"
    )

@app.route("/api/v1.0/precipitation")
def precipitation():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    """Convert the query results to a dictionary using `date` as the key and `prcp` as the value."""
    # Query precipitation
    results = session.query(Measurement.date, Measurement.prcp).all()

    session.close()

    # Convert list into dictionary
    precipitation = []
    for date,prcp in results:
        precipitation_dict = {}
        precipitation_dict["Date"] = date
        precipitation_dict["Precipitation"] = prcp
        precipitation.append(precipitation_dict)

    return jsonify(precipitation_dict)


@app.route("/api/v1.0/stations")
def stations():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    """Return a JSON list of stations from the dataset."""
    # Query stations
    results = session.query(Station.station).all()
    session.close()

    stations = list(np.ravel(results))
    return jsonify(stations)


@app.route("/api/v1.0/tobs")
def tobs():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    """Query the dates and temperature observations of the most active station for the last year of data."""
    """Return a JSON list of temperature observations (TOBS) for the previous year."""
    # Query stations
    results = session.query(Measurement.date, Measurement.tobs).\
              filter(Measurement.station == 'USC00519281').\
                  filter(Measurement.date >= '2016-08-23').filter(Measurement.date <= '2017-08-23').all()  
    session.close()

    tobs_list = []
    for date, tobs in results:
        tobs_d = {}
        tobs_d["Date"] = date
        tobs_d["Tobs"] = tobs
        tobs_list.append(tobs_d)
    return jsonify(tobs_list)



@app.route("/api/v1.0/<start_date>")
def start_date(start_date):
    # Create our session (link) from Python to the DB
    session = Session(engine)

    """Return a JSON list of the minimum temperature, the average temperature, and the max temperature for a given start or start-end range.
    When given the start only, calculate `TMIN`, `TAVG`, and `TMAX` for all dates greater than and equal to the start date.
    When given the start and the end date, calculate the `TMIN`, `TAVG`, and `TMAX` for dates between the start and end date inclusive."""

    results = session.query(func.min(Measurement.tobs), func.max(Measurement.tobs), func.avg(Measurement.tobs)).\
        filter(Measurement.date >= start_date).all()
    session.close()

    tobs_start = []
    for min,max,avg in results:
        start_dict = {}
        start_dict["TMin"] = min
        start_dict["TMax"] = max
        start_dict["TAvg"] = avg
        tobs_start.append(start_dict)
    return jsonify(tobs_start)


@app.route("/api/v1.0/<start_date>/<end_date>")
def start_end(start_date, end_date):
    
    # Create our session (link) from Python to the DB
    session = Session(engine)

    results = session.query(func.min(Measurement.tobs), func.max(Measurement.tobs), func.avg(Measurement.tobs)).\
        filter(Measurement.date >= start_date).\
            filter(Measurement.date <= end_date).all()
    session.close()

    start_end= []
    for min,max,avg in results:
        s_e_dict = {}
        s_e_dict["TMin"] = min
        s_e_dict["TMax"] = max
        s_e_dict["TAvg"] = avg
        start_end.append(s_e_dict)
    return jsonify(start_end)


if __name__ == "__main__":
    app.run(debug=True)
