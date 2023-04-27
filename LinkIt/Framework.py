import csv
import importlib
from pluginApi import PluginApi
from collections import defaultdict


# need API analyze_column method to be updated so it takes column name and returns it 
# or can return string "generic or nongeneric"
# or if plugin names have that in title we can use strings to determine not sure

# need to make sure data written to catalog does not overwrite other data
# need to make sure each csv column is getting passed to analyze data


def read_csv_file(filename):
    """
    Reads in a CSV file and returns a list containing the specified column data and its name.
    """
    columns = defaultdict(list)
    with open("LinkIt/csv/" + filename, 'r') as csv_file:
        reader = csv.DictReader(csv_file) 
        for row in reader: 
            for (key,value) in row.items():
                columns[key].append(value) # append the value into the appropriate list
                                 
        return columns


                       #or could take a dictionary containg these 
def create_catalog(column_guesses, column_data):
    """
    Creates a catalog of analyzed CSV data, selecting the plugin with the highest confidence score.
    """
    # Populate catalog
    #need to make sure data does not get overwritten 
    column_names = list(column_guesses.keys())
    with open('catalog.csv', 'a', newline='') as file:
        writer = csv.writer(file)
        for column_name in column_names:
            best_plugin = list(column_guesses[column_name].keys())[0] #Andrew: fairly sure this will assign the right name
            best_confidence_score = column_guesses[column_name][best_plugin] #Andrew: fairly sure this will assign the right score 
            writer.writerow([column_name, best_plugin, best_confidence_score, column_data[column_name]]) #removed is_generic for now


def analyze_data(dict_values):
    column_names = list(dict_values.keys())
    api = PluginApi()
    dict_results = {}
    # Andrew: run analyze_column from API for every column in csv file
    for column_name in column_names:
        conf_score = api.analyze_column(column_name, dict_values[column_name])
        dict_results.update({column_name: conf_score})

    # Andrew: return dict {column name: {plugin names, confidence scores}}
    return dict_results

def column_find_best_guess(confidence_scores):
    #analyze data should return list of confidence scores & plugin names so it can be determined 
    #if they are generic or not, or scores can be tagged as generic or non gerneric
    #need to create values to determine which plugin and confidence score will be selected
    #if nongeneric is 80% or higher it should automattically win
    #if generic is 95% or higher it should win
    #if they are equal non generic wins
    # if nongenric is below 60% gernic wins

    generic_threshold = 0.6
    nongeneric_threshold = 0.8

    best_plugin = None
    best_confidence_score = -1
    is_generic = True

    # Andrew: return value, dict{column_name:{plugin_name:score}} 
    name_plugin_score = {}

    # Andrew: for each column in the original table
    for disp_column in confidence_scores:
        # Andrew: for each plugin that has given a confidence score for that column's type
        plugin_names = list(confidence_scores[disp_column].keys())
        for plugin in plugin_names:
            # Andrew: original logic, just updated variable names and added declaration for cleanliness
            current_score = confidence_scores[disp_column][plugin] 
            if current_score > best_confidence_score:
                best_confidence_score = current_score
                is_generic = False
                if current_score >= nongeneric_threshold:
                    best_plugin = plugin # Andrew: fairly sure this will assign String 
                elif best_plugin is None or best_confidence_score >= 0.95:
                    best_plugin = plugin if current_score >= generic_threshold else "generic"
        # Andrew: adds the best plugin and its score to the column name list
        plugin_and_score = {best_plugin: best_confidence_score}
        name_plugin_score.update({disp_column: plugin_and_score})

    return name_plugin_score




def start_linkit():
    """
    Main program entry point. Prompts user for CSV files to analyze and runs the analysis.
    """
    filenames_str = input("Enter the CSV files to be analyzed separated by commas: ")
    filenames = filenames_str.split(",")

    for filename in filenames:
        try:
            #reading files
            dict_values = read_csv_file(filename.strip()) #TO DO: only take sample of data

            #debug
            print("csv read...")

            #running plugin analysis 
            confidence_scores = analyze_data(dict_values)

            #debug
            print("confidence scores recieved...")

            # Andrew: made a seperate function for selecting the best plugin 
            column_guesses = column_find_best_guess(confidence_scores)

            #debug
            print("scores analyzed...")

            # populating output catalog with best guesses and sample data
            create_catalog(column_guesses, dict_values)

            #debug
            print("catalogue created...")

        except FileNotFoundError:
            print("File not found:", filename.strip())


# Start Program Run
start_linkit()

