import json
import datetime
import os



def aggregate_fitdata(input):
    # Define dataset with aggregated data points
    aggregated_dataset = []

    # Iterate through each bucket in the original dataset
    for bucket in input['bucket']:
        # Get the start and end time of the bucket in milliseconds
        start_time = int(bucket['startTimeMillis'])
        end_time = int(bucket['endTimeMillis'])

        # Convert the start and end time to datetime objects
        start_datetime = datetime.datetime.fromtimestamp(start_time / 1000)
        end_datetime = datetime.datetime.fromtimestamp(end_time / 1000)

        # Initialize the aggregated values
        aggregated_calories = 0
        aggregated_heart_minutes = 0
        aggregated_active_minutes = 0
        n = 0
        m = 0
        k = 0

        # Iterate through each dataset in the bucket
        for dataset in bucket['dataset']:
            # Check if the dataset contains points
            if 'point' and len(dataset['point'])>0 in dataset:
                # Iterate through each point in the dataset
                for point in dataset['point']:
                    # Get the value of the point
                    value = point['value'][0]

                    # Check the data type and aggregate accordingly
                    if dataset['dataSourceId'] == 'derived:com.google.calories.expended:com.google.android.gms:aggregated':
                        aggregated_calories += value['fpVal']
                        n += 1
                    elif dataset['dataSourceId'] == 'derived:com.google.heart_minutes.summary:com.google.android.gms:aggregated':
                        aggregated_heart_minutes += value['intVal'] 
                        m += 1
                    elif dataset['dataSourceId'] == 'derived:com.google.active_minutes:com.google.android.gms:aggregated':
                        aggregated_active_minutes += value['intVal']
                        k += 1

        # Create the aggregated data point
        aggregated_data_point = {
            'startTime': start_datetime,
            'endTime': end_datetime,
            'aggregated_calories': aggregated_calories / n if n>0 else 0,
            'aggregated_heart_minutes': aggregated_heart_minutes / m if m>0 else 0,
            'aggregated_active_minutes': aggregated_active_minutes / k if k>0 else 0
        }

        # Append the aggregated data point to the aggregated dataset
        aggregated_dataset.append(aggregated_data_point)

    # Print the aggregated dataset
    for data_point in aggregated_dataset:
        print(
            f"Start Time: {data_point['startTime']}, End Time: {data_point['endTime']}")
        print(f"Aggregated Calories: {data_point['aggregated_calories']}")
        print(
            f"Aggregated Heart Minutes: {data_point['aggregated_heart_minutes']}")
        print(
            f"Aggregated Active Minutes: {data_point['aggregated_active_minutes']}")
        print()

    # Calculate overall aggregated values
    overall_aggregated_calories = sum(
        data_point['aggregated_calories'] for data_point in aggregated_dataset)
    overall_aggregated_heart_minutes = sum(
        data_point['aggregated_heart_minutes'] for data_point in aggregated_dataset)
    overall_aggregated_active_minutes = sum(
        data_point['aggregated_active_minutes'] for data_point in aggregated_dataset)

    # Calculate overall average aggregated values
    total_buckets = len(aggregated_dataset)
    average_aggregated_calories = overall_aggregated_calories / total_buckets
    average_aggregated_heart_minutes = overall_aggregated_heart_minutes / total_buckets
    average_aggregated_active_minutes = overall_aggregated_active_minutes / total_buckets

    # Print overall average aggregated information
    print("Overall Average Aggregated Information:")
    print(f"Total Aggregated Calories: {average_aggregated_calories}")
    print(
        f"Total Aggregated Heart Minutes: {average_aggregated_heart_minutes}")
    print(
        f"Total Aggregated Active Minutes: {average_aggregated_active_minutes}")
    return {'average_heart_rate_per_active_period': average_aggregated_calories,
            'average_calories_burnt_per_active_period': average_aggregated_heart_minutes,
            'average_active_interval': average_aggregated_active_minutes}
