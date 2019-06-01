# Import dependencies
import numpy as np
from flask import Flask, jsonify
from datetime import datetime
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func


engine = create_engine("sqlite:///hawaii.sqlite?check_same_thread=False")
conn = engine.connect()

Base = automap_base()


Base.prepare(engine, reflect=True)


Measurement = Base.classes.measurement
Station = Base.classes.station

session = Session(engine)

app = Flask(__name__)



@app.route("/")
def home():
    
    return(
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/calc_temps/<start><br/>"
        f"/api/v1.0/calc_temps/<start>/<end>"
    )


@app.route("/api/v1.0/precipitation")
def precipitation():
    
        prcp_oneyear= session.query(Measurement.date, Measurement.prcp).\
        filter(Measurement.date >= "2016-08-23").filter(Measurement.date <= "2017-08-23").\
        order_by(Measurement.date).all()

        precipitation = []
        for prcp in prcp_oneyear:
            row = {"Date": "Precipitation"}
            row["Date"] = prec[0]
            row["Precipitation"] = float(prcp[1])
            precipitation.append(row)

        return jsonify(precipitation)


@app.route("/api/v1.0/stations")
def stations():
    
    stations = session.query(Station.station, Station.name).group_by(
        Station.station).all()
    station_list = list(np.ravel(stations))

    return jsonify(stations)


@app.route("/api/v1.0/tobs")
def tobs():
    """Return a list of dates and temps from a year of last data point"""
    temps = session.query(Measurement.station, Measurement.tobs).\
        filter(Measurement.date >= "2016-08-23").\
            filter(Measurement.date <= "2017-08-23")
    
    temp_data = []
    for temp in temps:
        temp_dic = {}
        temp_dic["Station"] = temp[0]
        temp_dic["Temperatures"] = float(temp[1])
        temp_data.append(temp_dic)
    
    return jsonify(temp_data)


@app.route("/api/v1.0/calc_temps/<start>")
def calc_temps(start="start_date"):
    start_date = datetime.strptime("2017-06-29", "%Y-%m-%d").date()
    start_results = session.query(func.max(Measurement.tobs),
                                  func.min(Measurement.tobs),
                                  func.avg(Measurement.tobs)).\
        filter(Measurement.date >= start_date)

    start_temps = []
    for temp in start_results:
        temp_dict = {}
        temp_dict["TAVG"] = float(temp[2])
        temp_dict["TMAX"] = float(temp[0])
        temp_dict["TMIN"] = float(temp[1])
        start_temps.append(temp_dict)

    return jsonify(start_temps)


@app.route("/api/v1.0/calc_temps/<start>/<end>")
def calc_temps_2(start="start_date", end="end_date"):
    start_date = datetime.strptime("2017-06-29", "%Y-%m-%d").date()
    end_date = datetime.strptime("2017-07-07", "%Y-%m-%d").date()
    trip_results = session.query(func.max(Measurement.tobs).label("max_temps"),
                                 func.min(Measurement.tobs).label("min_temps"),\
                                    func.avg(Measurement.tobs).label("avg_temps")).\
                                        filter(Measurement.date >= "start_date").\
                                            filter(Measurement.date <= "end-date")

    trip_temps = []
    for temp in trip_results:
        temp_dict = {}
        temp_dict["TAVG"] = float(temp[2])
        temp_dict["TMAX"] = float(temp[0])
        temp_dict["TMIN"] = float(temp[1])
        trip_temps.append(temp_dict)
        
    return jsonify(trip_temps)


if __name__ == "__main__":
    app.run(debug=True)