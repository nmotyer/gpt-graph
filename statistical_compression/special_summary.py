from statistics import median, quantiles
from datetime import datetime, timedelta

def compress_array(arr, date_threshold=365):
    if not arr:
        return {}

    keys = set()
    values = {}

    # Extract keys and initialize empty lists for values
    for d in arr:
        for key, value in d.items():
            keys.add(key)
            if key not in values:
                values[key] = []

    # Populate the lists of values for each key
    for d in arr:
        for key in keys:
            if key in d:
                values[key].append(d[key])
            else:
                values[key].append(None)

    # Compress the array by summarizing the data
    result = {}

    date_keys = ['date', 'date_range', 'year', 'month']

    for key in keys:
        if all(value is None for value in values[key]):
            continue

        is_date_key = any(date_key in key.lower() for date_key in date_keys)

        if all(isinstance(value, (int, float)) for value in values[key]) and not is_date_key:
            median_value = median(values[key])
            q90 = quantiles(values[key], n=10)[8]
            result[f'median-{key}'] = median_value
            result[f'90th-percentile-{key}'] = q90

            if key.lower() == 'growth':
                years_above_median = [arr[i]['year'] for i, value in enumerate(values[key]) if value > median_value]
                result['years_growth_above_median'] = years_above_median

        elif all(isinstance(value, str) for value in values[key]):
            unique_values = set(values[key])

            # Check if the key name is likely to contain dates
            if any(is_date(value, date_keys=date_keys) for value in unique_values):
                date_ranges = get_date_ranges(unique_values, date_threshold)
                result[f'{key}-range'] = date_ranges[0]

                if len(date_ranges) > 1:
                    # Create additional date-range key for non-adjacent ranges
                    result[f'date-range-2'] = date_ranges[1]
            else:
                result[f'unique-{key}s'] = ', '.join(unique_values)

    return result


def is_date(value, format='%Y-%m-%d', date_keys=None):
    if isinstance(value, (int, float)):
        value = str(int(value))
    elif not isinstance(value, str):
        return False

    try:
        if date_keys and any(key in value for key in date_keys):
            datetime.strptime(value, format)
        elif any(date_key in value.lower() for date_key in ['year', 'month']):
            datetime.strptime(value, '%Y-%m')
        elif len(value) == 2:
            datetime.strptime(value, '%m')
        elif len(value) == 4:
            datetime.strptime(value, '%Y')
        else:
            datetime.strptime(value, format)
        return True
    except ValueError:
        return False


def get_date_ranges(date_values, date_threshold):
    dates = []
    for date_str in date_values:
        try:
            dates.append(datetime.strptime(date_str, '%Y-%m-%d'))
        except ValueError:
            try:
                dates.append(datetime.strptime(date_str, '%Y'))
            except ValueError:
                pass

    dates.sort()

    date_ranges = []
    current_range_start = dates[0]
    previous_date = dates[0]

    for date in dates[1:]:
        if date - previous_date > timedelta(days=date_threshold):
            date_range = f'{current_range_start.strftime("%Y-%m-%d")}-{previous_date.strftime("%Y-%m-%d")}'
            date_ranges.append(date_range)
            current_range_start = date
        else:
            current_range_start = min(current_range_start, date)

        previous_date = date

    last_date_range = f'{current_range_start.strftime("%Y-%m-%d")}-{previous_date.strftime("%Y-%m-%d")}'
    date_ranges.append(last_date_range)

    return date_ranges

def merge_date_ranges(date_range1, date_range2):
    date1_start, date1_end = date_range1.split('-')
    date2_start, date2_end = date_range2.split('-')

    if date1_end >= date2_start:
        # Merge overlapping date ranges
        merged_start = min(date1_start, date2_start)
        merged_end = max(date1_end, date2_end)
        return f'{merged_start}-{merged_end}'

    # If date ranges are not adjacent, return the original ranges
    return f'{date_range1}, {date_range2}'

if __name__ == '__main__':
    data = [
        {'year': '1980', 'growth': 1000},
        {'year': '2020', 'growth': 1000},
        {'year': '2021',  'growth': 2000},
        {'year': '2022',  'growth': 1500},
        {'year': '2023',  'growth': 1800},
]

result = compress_array(data, date_threshold=365)
print(result)