import re

def categorise(text):
    # Define regex patterns to match text-data or graph keywords
    text_data_pattern = r'\b(text|data)\b'
    graph_pattern = r'\b(graph|plot)\b'

    # Count the number of matches for each category
    text_data_count = len(re.findall(text_data_pattern, text, re.IGNORECASE))
    graph_count = len(re.findall(graph_pattern, text, re.IGNORECASE))

    # Categorize based on the count of matches
    if text_data_count > graph_count:
        return 'text-data'
    else:
        return 'graph'

if __name__ == '__main__':

    # Example usage
    text1 = 'This is a text about data and analysis'
    text2 = 'The graph below shows the results of the experiment'

    category1 = categorise(text1)
    category2 = categorise(text2)

    print(category1) # Output: 'text-data'
    print(category2) # Output: 'graph'
