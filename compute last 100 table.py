import csv
import matplotlib.pyplot as plt
import numpy as np
import glob

# values that can/should be changed
file_path = "./fl/*.csv"
png_path = "plot_of_plots.png"

def read_csv(file_path):
    keys = []   # each variation of dbuff/var is a key
    #bins = [[] for _ in range(100)]   # not to be confused with data binning, just a list to collect 100 data points across all of the same dbuff/var rows in a 2d grid
    data_list = []
    data = {}
    entries = []
    max_bound = -np.inf
    min_bound = np.inf
    for f_in in glob.glob(file_path):
        with open(f_in, newline='') as csvfile:
            csv_reader = csv.reader(csvfile)

            #process rows into dict
            for row in csv_reader:
                #get key in consistant format
                si = row[0].split('/')
                if int(si[0]) > 50000:
                    continue
                key = f"{int(si[0])}/{float(si[1])}"
                # Convert dbuff and var to floats
                if key not in data:
                    data[key] = [[] for _ in row[1:]]
                    entries.append([int(si[0]), float(si[1])])

                #Extract values from the rest of the row
                for i, val in enumerate(map(float, row[1:])):
                    #find max and min bounds of the data, for graphs
                    if max_bound < val:
                        max_bound = val
                    if min_bound > val:
                        min_bound = val
                    # Sort bins into list
                    data[key][i].append(val)

    #process stats
    for key in sorted(entries, key=lambda x: x[1]):
        dbuff, var = key
        values = []
        for inner_list in data[f"{dbuff}/{var}"][-10:]:
            values.extend(inner_list)

        entry = [dbuff, var, values]
        data_list.append(entry)

    return data_list, max_bound, min_bound


def compute_correlation(x, y):
    x_mean = np.mean(x)
    y_mean = np.mean(y)
    x_var = ((x-x_mean)**2).sum()
    y_var = ((y-y_mean)**2).sum()
    upper = ((x-x_mean) * (y-y_mean)).sum()
    lower = np.sqrt(x_var * y_var)
    return upper/lower


result_list, max_bound, min_bound = read_csv(file_path)
min_bound = -250

baseline = {}
baseline_error = {}
perf_diff = {}
perf_diff_error = {}


for i, entry in enumerate(result_list):
    dbuff, var, values = entry
    if var == 0:
        baseline[dbuff] = sum(values)/len(values)
        baseline_error[dbuff] = 1.96*(np.std(values)/ np.sqrt(len(values)))
    else:
        if dbuff not in perf_diff:
            perf_diff[dbuff] = {var:sum(values)/len(values)}
            perf_diff_error[dbuff] = {var:1.96*(np.std(values)/ np.sqrt(len(values)))}
        else:
            perf_diff[dbuff][var] = sum(values)/len(values)
            perf_diff_error[dbuff][var] = 1.96*(np.std(values)/ np.sqrt(len(values)))

# process data and output perfromance difference in latex table format
# raw perf
for b in perf_diff:
    print(f"{b} &$\\num{{{baseline[b]:.2e}}}\\pm\\num{{{baseline_error[b]:.2e}}}$ ", end="")
    for v in perf_diff[b]:
        print(f"&$\\num{{{perf_diff[b][v]:.2e}}}\\pm\\num{{{perf_diff_error[b][v]:.2e}}}$ ", end="")
    print("\\\\")
#perf change
var_vals = set()
perf_vals = {dbs:[] for dbs in perf_diff}
for b in perf_diff:
    print(f"{b} ", end="")
    for v in perf_diff[b]:
        var_vals.add(v)
        print(f"&${100*(perf_diff[b][v] - baseline[b])/baseline[b]:.1f}\\pm{100*(perf_diff_error[b][v] + baseline_error[b])/baseline[b]:.1f}$ ", end="")
    print("\\\\")
#rb correlation
for v in var_vals:
    perf_vals = []
    for b in perf_diff:
        perf_vals.append(100*(perf_diff[b][v] - baseline[b])/baseline[b])
    print(f"&${compute_correlation(np.array(list(perf_diff.keys())), np.array(perf_vals)):.1f}$ ", end="")