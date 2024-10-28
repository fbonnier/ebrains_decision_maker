# main script
# Decision maker is a script calculating from a comparison report (https://github.com/fbonnier/file_comparison)
# some statistics in order to help or give a clue, an idea about the distance of two file contents.
# The distance is calculated using different algorithms.
# If it is possible, the maximum delta, the maximum distance between two data and the average distance between all comparable data
# are given

import os
import argparse
import json
import statistics
from interval import interval, inf
import traceback

decisions = {"Red": interval([0, 50]), "Orange": interval([50, 70]), "Yellow": interval([70, 80]), "Green": interval([80, 100])}

error_types = {
    "Missing data": 
        ["- Ensure the run instruction is correct", "- Ensure the inputs data are the expected ones", "- Did the simulation crashed ?", "- Are we comparing the right data/files ?"]
    }

def get_average_score (list_of_scores):
    assert len(list_of_scores) > 0, "List of scores empty"
    return sum(list_of_scores)/len(list_of_scores)

def get_delta_max (list_of_differences):
    list_of_deltas = []
    for icouple in list_of_differences:
        list_of_deltas.append(get_delta_max_1_file([float(icouple[ikey]) for ikey in icouple]))

    return list_of_deltas

def get_delta_max_1_file (list_of_deltas):
    return max (list_of_deltas)

def get_delta_array_per_type (report_data):
    to_return = {"arithmetic": [], "levenshtein": []}
    for icouple in report_data:
        for item in icouple["differences"]:
            to_return[icouple["differences"][item]["type"]].append(icouple["differences"][item]["value"])

    return to_return

def compute_final_scores_1method (decision_block:dict, method_block:dict):


    for ikey in method_block.keys():
        print ("Key " + str(ikey))
        # Add Method's score to final score
        decision_block["score"] += method_block[ikey]["score"]

        # Add Method's report to final report
        decision_block["report"][ikey]= method_block[ikey]["report"]

        # Add Method's logs to final log
        decision_block["log"] += method_block[ikey]["log"]

        # Add Method's errors to final errors
        decision_block["error"] += method_block[ikey]["error"]

        # Add Method's advices to final advices
        decision_block["advice"] += method_block[ikey]["advice"]

    

    # # Mean Hash Score
    # method_block["mean hash score"] = sum([ipair["hash score"] for ipair in method_block["files"]])/len(method_block["files"])
    # method_block["mape"] = sum([ipair["mape_score"] for ipair in method_block["files"]])/len(method_block["files"])
    # scores = [\
    #             method_block["mean hash score"],\
    #             method_block["mape"],\
    #             # method_block["mpse"],\
    #             # method_block["rmpse"]\
    #             ]
    
    # method_block["score"] = (sum(scores))/len(scores)

    # # Propose advices according the errors and the score of the method
    # method_block["advices"] = []
    
    # # array size errors
    # if method_block["error"] and "size" in method_block["error"]:
    #     method_block["advices"].append (error_types["Missing data"])

    return decision_block

if __name__ == "__main__":

    # 0: the report file is given as an entry
    parser = argparse.ArgumentParser(description='Gathers scores and proposes quality from verification methods reports ')
    parser.add_argument("--json", type=argparse.FileType('r'), metavar='report_list', dest="report_list", nargs="+", help='Report Files list to analyze')
    parser.add_argument('--out', type=argparse.FileType('w'), metavar='out', nargs=1, help='JSON File containing final decision and final report')

    args = parser.parse_args()

    # List of all method reports available
    report_list = args.report_list
    print ("List of reports : ")
    print (report_list)

    # Output file containing final decision, final score, advices, errors et all report blocks of verification methods
    output_report = args.out[0]
    
    # Logs to report issues and warnings
    log = []

    # Block storing all method's report blocks and final score
    decision_block = {"score": 0.,
              "log": [],
              "error": [],
              "report": {},
              "advice": [],
              "decision": None}

    # Method's names
    # methods = ["Reusability Verification"]

    # Check if there is one or more report to analyze
    if len(report_list) < 1:
        decision_block["log"].append ("Decision Error: No verification report")
        decision_block["error"].append ("Decision Error: No verification report")
        decision_block["score"] = None
    else:
        # Open and get info from each report file
        for ireport in report_list:
            
            try:
                with open (ireport.name, 'r') as report_file:
                    report_data = json.load (report_file)

                    # Try each method
                    # for imethod in methods:

                    try:
                        decision_block = compute_final_scores_1method(decision_block, report_data)

                    except Exception as e:
                        decision_block["log"].append (str("".join(traceback.format_exception(etype=type(e), value=e, tb=e.__traceback__))))
                        print (str("".join(traceback.format_exception(etype=type(e), value=e, tb=e.__traceback__))))

            except Exception as e:
                decision_block["log"].append (str("".join(traceback.format_exception(etype=type(e), value=e, tb=e.__traceback__))))

        # Calculate final score
        decision_block["score"] = decision_block["score"]/len(report_list)

    try:
        with open (output_report.name, 'w') as score_file:
            json.dump(decision_block, score_file, indent=4)
    except Exception as e:
        print (str("".join(traceback.format_exception(etype=type(e), value=e, tb=e.__traceback__))))
    

    # # 1: Open the JSON report containing differences and scores of two list of files
    # with open (args.file[0].name, 'r') as report_file:
    #     report_data = json.load(report_file)

    #     # 2: Build the list of scores
    #     total_number_of_data = len(report_data)
    #     # print (report_data[1]["score"])
    #     # print ("Scores: " + str([item["score"] for item in report_data]))
    #     # list_of_scores = [float(item["score"]) for item in report_data]

    #     # 3: Build list of delta sorted by type (arithmetic, levenshtein distance)
    #     delta_per_type = get_delta_array_per_type (report_data)
    #     # print (delta_per_type)

    #     # 4-1: Arithmetic Statistics
    #     print ("===============================\n# Arithmetic\n===============================")
    #     print ("# Min value = " + str (min(delta_per_type["arithmetic"])))
    #     print ("# Max value = " + str (max(delta_per_type["arithmetic"])))
    #     print ("# Harmonic mean = " + str (statistics.harmonic_mean(delta_per_type["arithmetic"])))
    #     print ("# Mean (Average) = " + str (statistics.mean(delta_per_type["arithmetic"])))
    #     print ("# Median = " + str (statistics.median(delta_per_type["arithmetic"])))
    #     print ("# Median Low = " + str (statistics.median_low(delta_per_type["arithmetic"])))
    #     print ("# Median High = " + str (statistics.median_high(delta_per_type["arithmetic"])))
    #     print ("# Mode = " + str (statistics.mode(delta_per_type["arithmetic"])))
    #     print ("# Standard Deviation Population = " + str (statistics.pstdev(delta_per_type["arithmetic"])))
    #     print ("# Standard Deviation = " + str (statistics.stdev(delta_per_type["arithmetic"])))
    #     print ("# Population Variance = " + str (statistics.pvariance(delta_per_type["arithmetic"])))
    #     print ("# Variance = " + str (statistics.variance(delta_per_type["arithmetic"])))
    #     print ("===============================\n")

    #     # 4-2: Levenshtein Statistics
    #     print ("===============================\n# Levenshtein\n===============================")
    #     print ("# Min value = " + str (min(delta_per_type["levenshtein"])))
    #     print ("# Max value = " + str (max(delta_per_type["levenshtein"])))
    #     print ("# Harmonic mean = " + str (statistics.harmonic_mean(delta_per_type["levenshtein"])))
    #     print ("# Mean (Average) = " + str (statistics.mean(delta_per_type["levenshtein"])))
    #     print ("# Median = " + str (statistics.median(delta_per_type["levenshtein"])))
    #     print ("# Median Low = " + str (statistics.median_low(delta_per_type["levenshtein"])))
    #     print ("# Median High = " + str (statistics.median_high(delta_per_type["levenshtein"])))
    #     print ("# Mode = " + str (statistics.mode(delta_per_type["levenshtein"])))
    #     print ("# Standard Deviation Population = " + str (statistics.pstdev(delta_per_type["levenshtein"])))
    #     print ("# Standard Deviation = " + str (statistics.stdev(delta_per_type["levenshtein"])))
    #     print ("# Population Variance = " + str (statistics.pvariance(delta_per_type["levenshtein"])))
    #     print ("# Variance = " + str (statistics.variance(delta_per_type["levenshtein"])))
    #     print ("===============================\n")

    #     # 4-3: Key errors, missing data
    #     # print ("===============================\n# Missing data\n===============================")
    #     # print ("# Number of missing values = " + str (len(report_data["missing"])))
    #     # print ("===============================\n")

    #     # 4-4: Machine precision
    #     print ("===============================\n# Machine precision\n===============================")
    #     print ("!!WARNING!!: Only arithmetic values can be compared to machine precision. \U0001F595")
    #     print ("# Numpy.EPS = " + str(numpy.finfo(float).eps) + "\n")
    #     for ivalue in delta_per_type["arithmetic"]:
    #         if ivalue > numpy.finfo(float).eps:
    #             print (str(ivalue)  + " :: Value too far from machine precision")
    #     print ("\n")
    #     print ("===============================\n")

    #     # 4-4: Raised Errors
    #     # print ("===============================\n# Raised Errors\n===============================")
    #     # print ("# Number of errors = " + str(len(report_data["errors"])) + "\n")
    #     # print (report_data["errors"])
    #     # print ("\n")
    #     # print ("===============================\n")

    #     # 4.5: Is there a documentation ?
    #     # print ("===============================\n# README\n===============================")



    #     # average_score = get_average_score (list_of_scores)
    #     # print ("Average Score: " + str(average_score))
    #     #
    #     # list_of_differences = [item["differences"] for item in report_data]
    #     # print ("Differences: " + str(list_of_differences))
    #     #
    #     # list_of_delta = []
    #     # for idiff in list_of_differences:
    #     #     print ("idiff: " + str(idiff))
    #     #     # list_of_delta.append(list_of_differences[idiff])
    #     # print ("Deltas: " + str(list_of_delta))



    #     # list_of_delta_max = get_delta_max (list_of_differences)
    #     # print ("Delta Max: " + str(list_of_delta_max))


    #     # list_of_scores = [report_data[idx]["score"] for idx in range(1, len(report_data))]
    #     # print (list_of_scores)
    #     # for idata in report_data:
    #     #     print (idata)


    exit (0)
