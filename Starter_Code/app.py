# Import the dependencies.
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
import numpy as np
from flask import Flask, jsonify
import datetime as dt

#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()

# reflect the tables
Base.prepare(autoload_with = engine)

# Save references to each table
measurement = Base.classes.measurement
station = Base.classes.station

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
def welcome():
    """List all available api routes."""
    return(
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/<start><br/>"
        f"/api/v1.0/<start>/<end>" )

#Precipitation route
@app.route("/api/v1.0/precipitation")
def precipitation():
    # Create our session (link) from Python to the DB
    session = Session(engine)

 # Query  
    date = dt.datetime(2016,8,23)
    one_year_prcp = session.query(Measurement.date, Measurement.prcp).\
                    filter(Measurement.date > date).\
                    order_by(Measurement.date).all()
    
    session.close()

 # Create a dictionary
    precipitation = []
    for date, prcp in one_year_prcp:
        precipitation_dict = {date:prcp}
        precipitation.append(precipitation_dict)   
    return jsonify(precipitation)
   
# Station names route    
@app.route("/api/v1.0/stations")
def stations():
    # Create our session (link) from Python to the DB
    session = Session(engine)    

    # Query the list of station names
    results = session.query(Station.station,Station.name).all()
    
    session.close()
    all_names = []
    for station, name in results:
        name_dict = {station:name}
        all_names.append(name_dict)
    return jsonify(all_names)

# tobs route
@app.route("/api/v1.0/tobs")
def tobs():
    # Create our session (link) from Python to the DB
    session = Session(engine)                     
                    
    # Query    
    query_date = dt.date(2017,8,23)- dt.timedelta(days=365)
    one_year_temp = session.query(Measurement.date, Measurement.tobs).\
                    filter(Measurement.date >= query_date).\
                    filter(Measurement.station == 'USC00519281').\
                    order_by(Measurement.date).all()

    session.close()

    # Create a dictionary
    temperature = []
    for date, tobs in one_year_temp:
        temperature_dict = {date:tobs}
        temperature.append(temperature_dict)   
    return jsonify(temperature)

# Start Date Route
@app.route("/api/v1.0/<start>")
def temp(start=None): 
        

    # Create session (link) from Python to the DB
    session = Session(engine) 
    
    sel = [Measurement.station,func.min(Measurement.tobs),
           func.avg(Measurement.tobs),
           func.max(Measurement.tobs)]
    start_date = dt.datetime.strptime(start,"%m%d%Y")
    
    result = session.query(*sel).\
             filter(Measurement.date >= start_date).\
             group_by(Measurement.station).all()

    session.close()
                 
    df= pd.DataFrame(result,columns=['STATION','TMIN','TAVG','TMAX'])
    analyse = df.values.tolist()
    analyse_dict = df.to_dict()    
    return jsonify(analyse)



# Start and End Date Route
@app.route("/api/v1.0/<start>/<end>")
def temps(start=None,end=None): 
         
    # Create session (link) from Python to the DB
    session = Session(engine) 
           
    start_date = dt.datetime.strptime(start , "%m%d%Y")       
    end_date = dt.datetime.strptime(end, "%m%d%Y")

    sel = [Measurement.station,func.min(Measurement.tobs),
           func.avg(Measurement.tobs),
           func.max(Measurement.tobs)]
        
    result = session.query(*sel).\
             filter(Measurement.date >= start_date).\
             filter(Measurement.date <= end_date).\
             group_by(Measurement.station).all()

    session.close()

    df= pd.DataFrame(result,columns=['STATION','TMIN','TAVG','TMAX'])
    analyse = df.values.tolist()
    analyse_dict = df.to_dict()      
    return jsonify(analyse)   


if __name__ == '__main__':
    app.run(debug=True)
