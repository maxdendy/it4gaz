from flask import Flask, request, jsonify, Response
from sqlalchemy import create_engine, Column, Integer, Float, Sequence, DateTime, and_
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime
import csv
import io
import numpy as np

app = Flask(__name__)

# Настройки базы данных
PGSQL_USERNAME = "userforus"
PGSQL_PASSWORD = "bA6si2bUA2dba2-G"
PGSQL_HOST = "mxdndy.ru"
database_URL = f'postgresql://{PGSQL_USERNAME}:{PGSQL_PASSWORD}@{PGSQL_HOST}/it4gaz'

engine = create_engine(database_URL)
session_factory = sessionmaker(bind=engine)
Session = scoped_session(session_factory)

Base = declarative_base()


class Data(Base):
    __tablename__ = 'data'

    id = Column(Integer, Sequence('data_id_seq'), primary_key=True)
    Time = Column(DateTime)
    T_K_1 = Column(Float)
    T_K_2 = Column(Float)
    T_K_3 = Column(Float)
    T_L_1 = Column(Float)
    T_L_2 = Column(Float)
    T_L_3 = Column(Float)
    T_Up_1 = Column(Float)
    T_Up_2 = Column(Float)
    T_Up_3 = Column(Float)
    T_1 = Column(Float)


Base.metadata.create_all(engine)


def filter_and_convert_to_array(data, start_time, end_time):
    filtered_data = [
        [d.id, d.Time, d.T_K_1, d.T_K_2, d.T_K_3, d.T_L_1, d.T_L_2, d.T_L_3, d.T_Up_1, d.T_Up_2, d.T_Up_3, d.T_1]
        for d in data if start_time <= d.Time <= end_time
    ]
    return np.array(filtered_data)


@app.route('/data', methods=['GET'])
def get_data():
    session = Session()

    # Параметры фильтрации
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    sensor_id = request.args.get('id')
    deformation_level = request.args.get('T_1')
    page = int(request.args.get('page', 1))
    per_page = int(request.args.get('per_page', 10))
    export_csv = request.args.get('export_csv', 'false').lower() == 'true'

    filters = []
    if start_date:
        start_date = datetime.fromisoformat(start_date)
        filters.append(Data.Time >= start_date)
    if end_date:
        end_date = datetime.fromisoformat(end_date)
        filters.append(Data.Time <= end_date)
    if sensor_id:
        filters.append(Data.id == int(sensor_id))
    if deformation_level:
        filters.append(Data.T_1 == float(deformation_level))

    query = session.query(Data).filter(and_(*filters))
    data = query.all()
    session.close()

    # Преобразование данных в массив и фильтрация
    if start_date and end_date:
        result_array = filter_and_convert_to_array(data, start_date, end_date)
        return jsonify(result_array.tolist())

    # Обработка экспорта в CSV
    if export_csv:
        return export_to_csv(data)

    # Пагинация
    total_items = len(data)
    paginated_data = data[(page - 1) * per_page: page * per_page]

    result = [
        {
            "id": d.id,
            "Time": d.Time.strftime('%Y-%m-%d %H:%M:%S') if d.Time else '',
            "T_K_1": d.T_K_1,
            "T_K_2": d.T_K_2,
            "T_K_3": d.T_K_3,
            "T_L_1": d.T_L_1,
            "T_L_2": d.T_L_2,
            "T_L_3": d.T_L_3,
            "T_Up_1": d.T_Up_1,
            "T_Up_2": d.T_Up_2,
            "T_Up_3": d.T_Up_3,
            "T_1": d.T_1
        } for d in paginated_data
    ]

    return jsonify({
        "total_items": total_items,
        "page": page,
        "per_page": per_page,
        "data": result
    })


def export_to_csv(data):
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(
        ["id", "Time", "T_K_1", "T_K_2", "T_K_3", "T_L_1", "T_L_2", "T_L_3", "T_Up_1", "T_Up_2", "T_Up_3", "T_1"])

    for d in data:
        writer.writerow([
            d.id,
            d.Time.strftime('%Y-%m-%d %H:%M:%S') if d.Time else '',  # Изменение формата даты
            d.T_K_1, d.T_K_2, d.T_K_3,
            d.T_L_1, d.T_L_2, d.T_L_3,
            d.T_Up_1, d.T_Up_2, d.T_Up_3,
            d.T_1
        ])

    response = Response(output.getvalue(), content_type='text/csv')
    response.headers["Content-Disposition"] = "attachment; filename=data.csv"
    return response


if __name__ == '__main__':
    app.run(debug=True)
