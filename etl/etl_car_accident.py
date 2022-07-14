"""
警察庁　オープンデータ 2020年
交通事故情報 ( https://www.npa.go.jp/publications/statistics/koutsuu/opendata/2020/opendata_2020.html )

BigQueryに取り込むための簡単な練習コード
"""
import pandas as pd 

PROJECTID = "enjoy-open-data"

YYYY = 2020
assert YYYY >= 2019, "[assert] 2019年未満のデータは公開されていません"
ACCIDENT_DATA_PATH = f"https://www.npa.go.jp/publications/statistics/koutsuu/opendata/{YYYY}/honhyo_{YYYY}.csv"

df = pd.read_csv(ACCIDENT_DATA_PATH, encoding="shift-jis")

old_cols = df.columns

new_cols = [
    'file_classification', 'prefecture_code', 'policestation_code',
    'main_record_number', 'accident_details', 'number_deaths', 'number_injuries', 'route_code',
    'up_down_line', 'location_code', 'city_code', 'occurrence_year', 'occurrence_month',
    'occurrence_day', 'occurrence_hour','occurrence_minute', 'day_and_night', 'weather',
    'terrain', 'road_surface_condition', 'road_geometry', 'diameter_of_circular_intersection',
    'traffic_signal', 'temporary_stop_sign_A', 'temporary_force_stop_sign_A', 'temporary_stop_sign_B', 
    'temporary_force_stop_sign_B', 'roadway_width','roadway_alignment', 'collision_point', 
    'zone_control', 'median_facilities_etc', 'footpath_classification',
    'accident_type', 'age_A', 'age_B', 'party_type_A', 'party_type_B',
    'use_type_A', 'use_type_B', 'vehicle_shape_A', 'vehicle_shape_B',
    'speed_restriction_A', 'speed_restriction_B', 'vehicle_crash_site_A', 'vehicle_crash_site_B', 
    'damage_to_vehicle_A', 'damage_to_vehicle_B', 'equipped_airbags_A',
    'equipped_airbags_B', 'equipped_sideairbags_A', 'equipped_sideairbags_B',
    'injury_A', 'injury_B', 'latitude', 'longitude', 'dow','holiday'
]

assert len(old_cols) == len(new_cols), "[assertion error] カラムの数が違います"

df.columns = new_cols
df["file_csv"] = f"honhyo_{YYYY}.csv"

schem_list = [ {"name": new_cols[i], "type": "INTEGER", "description": old_cols[i]} for i in range(len(new_cols))]
schem_list.append( {"name": "file_csv", "type": "STRING", "description": f"honhyo_{YYYY}.csv"})

df.to_gbq(
    "raw_open_data.car_accident",
     project_id=PROJECTID,
    if_exists="append", 
    table_schema=schem_list
    )

print("読込終了")