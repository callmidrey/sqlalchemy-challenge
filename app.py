# Import the dependencies.
from flask import Flask, jsonify
import numpy as np
import pandas as pd
import datetime as dt
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite", echo=False)

# reflect an existing database into a new model
Base = automap_base()
Base.prepare(autoload_with=engine)
Base.classes.keys()

# Save references to each table
Measurement=Base.classes.measurement
Station = Base.classes.station

# Create our session (link) from Python to the DB
session = Session(engine)

#################################################
# Flask Setup
#################################################
app = Flask(__name__)

#################################################
# Flask Routes
#################################################
@app.route("/")
def index():
    """List of available api routes"""
    return (
        f"Available routes:</br>"
        f"/api/v1.0/precipitation</br>"
        f"/api/v1.0/stations</br>"
        f"/api/v1.0/tobs</br>"
        f"/api/v1.0/<start_date></br>"
        f"/api/v1.0/<start_date>/<end_date>"
    )
@app.route("/api/v1.0/precipitation")
def precipatation ():
        #create session link
    session = Session(engine)
    #date 
    date=session.query(Measurement.date).\
    order_by(Measurement.date.desc()).first().date
    # Calculate the date one year from the last date in data set.
    year_last=dt.datetime.strptime(date,'%Y-%m-%d')-dt.timedelta(days=365)
    # Perform a query to retrieve the data and precipitation scores
    prcp_score=session.query(Measurement.date,Measurement.prcp).\
    filter(Measurement.date>=year_last).\
    order_by(Measurement.date).all()
    session.close()
    percp=list(np.ravel(prcp_score))
    return jsonify(percp)

    # List of Stations
@app.route("/api/v1.0/stations")
def stations ():
    
    session = Session(engine)
    
# list of station ID and 
    list_station=session.query(Station.station,Station.name).\
    group_by(Station.name).\
    order_by((Station.name).desc()).all()
        
    session.close()
    stat=list(np.ravel(list_station))
    print("List of Station ID and name")
    return jsonify(stat)
# temperature
@app.route("/api/v1.0/tobs")
def tobs ():
    session = Session(engine)
    #date 
    date=session.query(Measurement.date).\
    order_by(Measurement.date.desc()).first().date
    # Calculate the date one year from the last date in data set.
    year_last=dt.datetime.strptime(date,'%Y-%m-%d')-dt.timedelta(days=365)
    #last year temp
    temp_station=session.query(Measurement.date,Measurement.tobs).\
    filter(Measurement.date>=year_last).\
    filter(Measurement.station == "USC00519281").\
    order_by(Measurement.date).all()
    
    session.close()
    temp=list(np.ravel(temp_station))
    return jsonify(temp)  
# Sepecified date temperatures
@app.route("/api/v1.0/<start_date>")
def start_date (start_date):
    print("Into start date Selection")
    print("Minimum Temperature, Maximum Temperature,Average Temperature")
    print(start_date)
    #create session
    session=Session(engine)
    
    # date filter
    Temperature=session.query(func.min(Measurement.tobs),func.max(Measurement.tobs),func.avg(Measurement.tobs)).\
    filter(Measurement.date>=start_date).all()
    
    session.close()
    temp_st=list(np.ravel(Temperature))
    return jsonify(temp_st)  
#within dates (start and end dates)   
@app.route("/api/v1.0/<start_date>/<end_date>")
def st_ed_date (start_date,end_date):
    print(start_date)
    print(end_date)
    session = Session(engine)
    Temp_range=session.query(func.min(Measurement.tobs),func.max(Measurement.tobs),func.avg(Measurement.tobs)).\
    filter(Measurement.date>=start_date).\
    filter(Measurement.date>=end_date).all()
    session.close()
    temp_rg=list(np.ravel(Temp_range))
    return jsonify(temp_rg)
# App run and debug  
if __name__ =="__main__":
    app.run(debug=True)

# Close the session when done
session.close()