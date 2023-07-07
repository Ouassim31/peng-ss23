import json
import datetime
import os



def aggregate_fitdata(input):
    # Define dataset with aggregated data points
    entire_aggregated_dataset = []

    # Iteratation through each bucket in the original dataset
    for bucket in input['bucket']:
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
        entire_aggregated_dataset.append(aggregated_data_point)

    # Iterate over time and update the aggregated values
    overall_aggregated_calories = overall_aggregated_heart_minutes = overall_aggregated_active_minutes = 0
    a = b = c = 0

    for entry in entire_aggregated_dataset:
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

    #  Overall average aggregated information
    print("Overall Aggregated Information:")
    print(f"Total Aggregated Calories: {average_aggregated_calories}")
    print(f"Total Aggregated Heart Minutes: {average_aggregated_heart_minutes}")
    print(
        f"Total Aggregated Active Minutes: {average_aggregated_active_minutes}")
    return {'average_heart_rate_per_active_period': average_aggregated_calories,
            'average_calories_burnt_per_active_period': average_aggregated_heart_minutes,
            'average_active_interval': average_aggregated_active_minutes}
