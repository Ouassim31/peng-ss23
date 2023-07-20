import json
import datetime
import os
#import datetime
import random

class Aggregate:
  def __init__(self, original_dataset):
    self.original_dataset = original_dataset

  def fit_data_aggregate(self):
    # Define dataset with aggregated data points
    aggregated_dataset = []
  
    # Iteratation through each bucket in the original dataset
    for bucket in self.original_dataset['bucket']:
      # Get the start and end time of the bucket in milliseconds
      start_time = int(bucket['startTimeMillis'])
      end_time = int(bucket['endTimeMillis'])
  
      # Convert the start and end time to datetime objects
      start_datetime = datetime.datetime.fromtimestamp(start_time / 1000)
      end_datetime = datetime.datetime.fromtimestamp(end_time / 1000)
  
      # Initialize the aggregated values
      aggregated_calories = aggregated_heart_minutes = aggregated_active_minutes = 0
  
      # Iterate through each dataset in the bucket
      for dataset in bucket['dataset']:
        # Check if the dataset contains points
        if 'point' in dataset:
          # Iterate through each point in the dataset
          for point in dataset['point']:
            if dataset[
                'dataSourceId'] == 'derived:com.google.calories.expended:com.google.android.gms:aggregated':
              value = point['value'][0]
              if value['fpVal'] != 0:
                aggregated_calories += value['fpVal']
            elif dataset[
                'dataSourceId'] == 'derived:com.google.heart_minutes.summary:com.google.android.gms:aggregated':
              value = point['value'][1]
              if value['intVal'] != 0:
                aggregated_heart_minutes += value['intVal']
            elif dataset[
                'dataSourceId'] == 'derived:com.google.active_minutes:com.google.android.gms:aggregated':
              value = point['value'][0]
              if value['intVal'] != 0:
                aggregated_active_minutes += value['intVal']
  
    # Create the aggregated data point
      aggregated_data_point = {
        'startTime': start_datetime,
        'endTime': end_datetime,
        'aggregated_calories': aggregated_calories,
        'aggregated_heart_minutes': aggregated_heart_minutes,
        'aggregated_active_minutes': aggregated_active_minutes
      }
  
      # Append the aggregated data point to the aggregated dataset
      aggregated_dataset.append(aggregated_data_point)
    return aggregated_dataset

class AverageFitData:
  def __init__(self, entire_aggregated_dataset):
    self.entire_aggregated_dataset = entire_aggregated_dataset

  def average_fit_data(self):
    # Iterate over time and update the aggregated values
    overall_aggregated_calories = overall_aggregated_heart_minutes = overall_aggregated_active_minutes = 0
    a = b = c = 0
    
    for entry in self.entire_aggregated_dataset:
      aggregated_calories = entry['aggregated_calories']
      aggregated_heart_minutes = entry['aggregated_heart_minutes']
      aggregated_active_minutes = entry['aggregated_active_minutes']
      # Update overall aggregated values
      if aggregated_calories != 0:
        overall_aggregated_calories += aggregated_calories
        a += 1
      if aggregated_heart_minutes != 0:
        overall_aggregated_heart_minutes += aggregated_heart_minutes
        b += 1
      if aggregated_active_minutes != 0:
        overall_aggregated_active_minutes += aggregated_active_minutes
        c += 1
  
    average_aggregated_calories = overall_aggregated_calories / a if a != 0 else 0
    average_aggregated_heart_minutes = overall_aggregated_heart_minutes / b if b != 0 else 0
    average_aggregated_active_minutes = overall_aggregated_active_minutes / c if c != 0 else 0
    
    return {"agg_calories": average_aggregated_calories,
            "agg_heart_minutes": average_aggregated_heart_minutes,
            "agg_active_minutes": average_aggregated_active_minutes
           }

class WeekAggregate:
  def __init__(self, entire_aggregated_dataset ):
    self.entire_aggregated_dataset = entire_aggregated_dataset
    
  def week_aggregate(self):
    weekly_data = {}
    for entire_dataset in self.entire_aggregated_dataset:
      week_number = entire_dataset['startTime'].isocalendar()[1]  # Extract the ISO week number
      if week_number not in weekly_data:
        weekly_data[week_number] = []
      weekly_data[week_number].append(entire_dataset)
    return weekly_data
    
class DailyAggregate:
  def __init__(self, entire_aggregated_dataset ):
    self.entire_aggregated_dataset = entire_aggregated_dataset
    
  def daily_aggregate(self):
    daily_data = {}
    for entire_dataset in self.entire_aggregated_dataset:
      start_time = entire_dataset['startTime']
      day = start_time.strftime("%Y %m %d")
      if day not in daily_data:
        daily_data[day] = []
      daily_data[day].append(entire_dataset)
    return daily_data 


class HourAggregate:
  def __init__(self, entire_aggregated_dataset ):
    self.entire_aggregated_dataset = entire_aggregated_dataset
    
  def hour_aggregate(self):
    hourly_data = {}
    for entire_dataset in self.entire_aggregated_dataset:
      start_time = entire_dataset['startTime']
      dayhr = start_time.strftime("%Y %m %d %H")
      if dayhr not in hourly_data:
        hourly_data[dayhr] = []
      hourly_data[dayhr].append(entire_dataset)
    return hourly_data 


class PrintAverage:
  def __init__(self, aggregated_dataset ):
    self.aggregated_dataset = aggregated_dataset

    #  Overall average aggregated information
  def print_average(self):
    print("Overall Aggregated Information:")
    print(f"Aggregated Calories: {self.aggregated_dataset['agg_calories']}")
    print(f"Aggregated Heart Minutes: {self.aggregated_dataset['agg_heart_minutes']}")
    print(f"Aggregated Active Minutes: {self.aggregated_dataset['agg_active_minutes']}")

class FileOpenAggregate:
  def __init__(self, dict ):
    self.dict = dict

  def file_open(self):
      # Parsing original dataset JSON into a Python dictionary
      
      #Aggregate dataset
      fit_aggregate = Aggregate(self.dict)
      entire_aggregated_dataset = fit_aggregate.fit_data_aggregate()
      return entire_aggregated_dataset

class HeatRateMRP:
    def __init__(self, HR):
        self.HR = HR

    def calculate_category(self):
        if self.HR == 0:
          return "No Record"
        elif self.HR < 40:
            return "Low"
        elif 40 <= self.HR < 80:
            return "Normal"
        elif 80 <= self.HR < 100:
            return "Light"
        elif 100 <= self.HR < 140:
            return "Moderate"
        elif self.HR >= 140:
            return "Intensive"

class NoiseActive:
  def __init__(self, active):
      self.active = active

  def add_noise(self):
    noise = abs(random.gauss(50, 200))  # Gaussian noise with mean 0 and standard deviation 1
    noisy_value = self.active + noise
    return noisy_value

class CalorieRange:
  def __init__(self, calorie):
      self.calorie = calorie

  def add_range(self):
    if 0 <= self.calorie <= 100:
      return "0 - 100"
    elif 100 <= self.calorie <= 200:
      return "100 - 200"
    elif 200 <= self.calorie <= 400:
      return "200 - 400"
    elif 400 <= self.calorie <= 700:
      return "400 - 700"
    elif 700 <= self.calorie <= 1000:
      return "700 - 1000"
    elif 1000 <= self.calorie <= 1500:
      return "1000 - 1500"
    elif 1500 <= self.calorie <= 1800:
      return "1000 - 1500"
    elif 1800 <= self.calorie <= 2200:
      return "1800 - 2200"
    elif self.calorie >= 2200:
      return "Above 2200"

class FitDataManuplation:
  def __init__(self, overall_week_average_fit_data):
      self.overall_week_average_fit_data = overall_week_average_fit_data

  def fit_data_manuplation(self):
    #Heart Rate Scale
    data_HR = HeatRateMRP(self.overall_week_average_fit_data["agg_heart_minutes"])
    heatrate = data_HR.calculate_category()
    
    #Calorie  Scale
    calorie_data = CalorieRange(self.overall_week_average_fit_data["agg_calories"])
    calorierange = calorie_data.add_range()
    
    #Active Rate Scale
    active_data = NoiseActive(self.overall_week_average_fit_data["agg_active_minutes"])
    activenoise = active_data.add_noise()
    return [heatrate , calorierange , activenoise]


class SelectAggregationType:
  def __init__(self, type, dict ):
    self.type = type
    self.dict = dict

  def aggregation_type(self):
    # Whole Data aggregation
    if self.type == 1:
      file_op=FileOpenAggregate(self.dict)
      entire_aggregated_dataset = file_op.file_open()
       # Average of entire dataset
      overall_average_fit_data = {}
      average_date = AverageFitData(entire_aggregated_dataset)
      overall_average_fit_data = average_date.average_fit_data()
      print_entire_avgerage = PrintAverage(overall_average_fit_data)
      
      return(overall_average_fit_data)
      
    # aggregation by weekly
    elif self.type == 2:
      file_op=FileOpenAggregate(self.dict)
      entire_aggregated_dataset = file_op.file_open()
      #Weekly aggregate fit data
      week_aggreate = WeekAggregate(entire_aggregated_dataset)
      weekly_data = week_aggreate.week_aggregate()
      #Weekly average fit data
      weekly_average_data = {}
      for week_number, week_data in weekly_data.items():
        overall_average_fit_data = {}
        average_date = AverageFitData(week_data)
        overall_week_average_fit_data = average_date.average_fit_data()

        data_privacy = FitDataManuplation(overall_week_average_fit_data)
        mannu_data = data_privacy.fit_data_manuplation()
        
        overall_week_average_fit_data["agg_heart_minutes"] = mannu_data[0]  
        overall_week_average_fit_data["agg_calories"] = mannu_data[1]        
        overall_week_average_fit_data["agg_active_minutes"] = mannu_data[2]
                
        weekly_average_data[week_number] = []
        weekly_average_data[week_number].append(overall_week_average_fit_data)
       
      return(weekly_average_data)


    # aggregation by Daily
    elif self.type == 3:
      file_op=FileOpenAggregate(self.dict)
      entire_aggregated_dataset = file_op.file_open()
      #Daily aggregate fit data
      daily_aggreate = DailyAggregate(entire_aggregated_dataset)
      daily_data = daily_aggreate.daily_aggregate()
      daily_average_data = {}
      for day, day_data in daily_data.items():
        overall_average_fit_data = {}
        average_date = AverageFitData(day_data)
        overall_day_average_fit_data = average_date.average_fit_data()

        data_privacy = FitDataManuplation(overall_day_average_fit_data)
        mannu_data = data_privacy.fit_data_manuplation()
        
        overall_day_average_fit_data["agg_heart_minutes"] = mannu_data[0]  
        overall_day_average_fit_data["agg_calories"] = mannu_data[1]        
        overall_day_average_fit_data["agg_active_minutes"] = mannu_data[2]
                
        daily_average_data[day] = []
        daily_average_data[day].append(overall_day_average_fit_data)
        
      return(daily_average_data)
    
    # aggregation by hourly
    elif self.type == 4:
      file_op=FileOpenAggregate(self.dict)
      entire_aggregated_dataset = file_op.file_open()
      #Hourly aggregate fit data
      hour_aggreate = HourAggregate(entire_aggregated_dataset)
      hourly_data = hour_aggreate.hour_aggregate()
    
      #Weekly average fit data
      hourly_average_data = {}
      for hour, hour_data in hourly_data.items():
        overall_average_fit_data = {}
        average_date = AverageFitData(hour_data)
        overall_hour_average_fit_data = average_date.average_fit_data()

        data_privacy = FitDataManuplation(overall_hour_average_fit_data)
        mannu_data = data_privacy.fit_data_manuplation()

        overall_hour_average_fit_data["agg_heart_minutes"] = mannu_data[0]  
        overall_hour_average_fit_data["agg_calories"] = mannu_data[1]        
        overall_hour_average_fit_data["agg_active_minutes"] = mannu_data[2]
        
        hourly_average_data[hour] = []
        hourly_average_data[hour].append(overall_hour_average_fit_data)
        
      
      return(hourly_average_data)
      
    else:
      return "No fitness data available"


#type_select = SelectAggregationType(2, "test_fit_Data.json")
#type_select.aggregation_type()

