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
    Most_recent_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first().date
    # Calculate the date one year from the last date in data set.
    Year_Precipitation = (dt.date(2017,8,23) - dt.timedelta(days=365)).strftime('%Y-%m-%d')
    Year_from_date = session.query(Measurement.date, Measurement.prcp).filter(Measurement.date >= Year_Precipitation).all()
    # Perform a query to retrieve the data and precipitation scores
    Year_Precipitation_df = pd.DataFrame(Year_from_date, columns=['date', 'precipitation'])
    # Sort the dataframe by date
    Year_Precipitation_df = Year_Precipitation_df.sort_values('date')
    session.close()
    percp=list(np.ravel(Year_from_date))
    return jsonify(percp)

    # List of Stations
@app.route("/api/v1.0/stations")
def stations ():
    
    session = Session(engine)
    
# list of station ID and 
    Active_Stations = session.query(Measurement.station, func.count(Measurement.station)).\
    group_by(Measurement.station).\
    order_by(func.count(Measurement.station).desc()).all()
        
    session.close()

    stat=list(np.ravel(Active_Stations))
    print("List of Station ID and name")
    return jsonify(stat)
# temperature
@app.route("/api/v1.0/tobs")
def tobs ():
    session = Session(engine)
    #date 
    Most_recent_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first().date

    # Design a query to calculate the total number of stations in the dataset
    session.query(func.count(Station.station)).all()

    Active_Stations = session.query(Measurement.station, func.count(Measurement.station)).\
    group_by(Measurement.station).\
    order_by(func.count(Measurement.station).desc()).all()

    # Using the most active station id from the previous query, calculate the lowest, highest, and average temperature.
    Most_Actve_Station_Id = 'USC00519281'

    lowest_temp = session.query(func.min(Measurement.tobs)).filter(Measurement.station == Most_Actve_Station_Id).one()[0]
    highest_temp = session.query(func.max(Measurement.tobs)).filter(Measurement.station == Most_Actve_Station_Id).one()[0]
    avgerage_temp = session.query(func.avg(Measurement.tobs)).filter(Measurement.station == Most_Actve_Station_Id).one()[0]
    
    # Using the most active station id, Query the last 12 months of temperature observation data for this station and plot the results as a histogram
    Year_Precipitation = (dt.date(2017,8,23) - dt.timedelta(days=365)).strftime('%Y-%m-%d')
    Annual_data = session.query(Measurement.date, Measurement.tobs).\
    filter(Measurement.station == Most_Actve_Station_Id).\
    filter(Measurement.date >= Year_Precipitation).all()
    Annual_Data_df = pd.DataFrame(Annual_data, columns=['date', 'temperature'])
    temperature =list(np.ravel(Most_Actve_Station_Id))

    return jsonify(temperature)  
    
session.close()

# Sepecified date temperatures
@app.route("/api/v1.0/<start_date>")
def start_date (start_date):
    print("Into start date Selection")
    print("Minimum Temperature, Maximum Temperature,Average Temperature")
    print(start_date)
    #create session
    session=Session(engine)
    
    # Using the most active station id from the previous query, calculate the lowest, highest, and average temperature.
    Most_Actve_Station_Id = 'USC00519281'
    lowest_temp = session.query(func.min(Measurement.tobs)).filter(Measurement.station == Most_Actve_Station_Id).one()[0]
    highest_temp = session.query(func.max(Measurement.tobs)).filter(Measurement.station == Most_Actve_Station_Id).one()[0]
    avgerage_temp = session.query(func.avg(Measurement.tobs)).filter(Measurement.station == Most_Actve_Station_Id).one()[0]
    print(f"lowest_temp = {lowest_temp}, highest_temp = {highest_temp}, average_temp = {avgerage_temp}")
    
    session.close()
    Temperature=list(np.ravel(Most_Actve_Station_Id))
    return jsonify(Temperature)  
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