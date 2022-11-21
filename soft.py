import csv                                  # Import csv lib to work with csv files
from tkinter import *                       # Import tkinter lib
from tkinter import filedialog              # Import dialog box from tkinter
import pandas as pd                         # Import pandas lib to do data analysis
import numpy as np                          # Import numpy lib to do data analysis
from matplotlib import pyplot as plt        # Import matplotlib to plot graph


# Global function to ask user to choose a file from a pop-up dialog window
def openFile():
    global path
    path = filedialog.askopenfilename(initialdir="C:\\Users\\USERNAME\\Desktop", title="Open a file", filetypes=(
        ("all files", "*.*"), ("text files", "*.txt")))
    label.config(text=path)


# Global function to find the closest number to a given value
def find_closet_num(A, target):
    min_diff = float("inf")
    low = 0
    high = len(A) - 1
    closet_num = None

    # when the list is empty or only 1 element
    if len(A) == 0:
        return None
    if len(A) == 1:
        return A[0]

    while low <= high:
        mid = (low + high) // 2

        # Ensure we don't read beyond bound of the list
        # and obtain left and right difference values
        if mid + 1 < len(A):
            min_diff_right = abs(A[mid+1] - target)
        if mid > 0:
            min_diff_left = abs(A[mid-1] - target)

        # Check if the abs value between left and right
        # elements are smaller than any seen prior
        if min_diff_left < min_diff:
            min_diff = min_diff_left
            closet_num = A[mid-1]
        if min_diff_right < min_diff:
            min_diff = min_diff_right
            closet_num = A[mid+1]

        # Update the mid point via binary search
        if A[mid] < target:
            low = mid + 1
        elif A[mid] > target:
            high = mid - 1
        # If the mid point is the target itself
        else:
            return A[mid]
    return closet_num


# Global function to print the result in tabulate form
def print_table(result):
    longest = 0
    len_list = []

    for row in result:
        length = len(str(row[0]))
        len_list.append(length)
        if length > longest:
            longest = length

    for i, row in enumerate(result):
        length = len_list[i]
        spaces = (longest - length) * ' '
        print(row[0], spaces, row[1])


# main body of the program
path = ''
# Create a user prompt dialog box
root = Tk()
root.title("Open a File")
root.geometry("500x250")
button = Button(root, text="Open")
button.config(command=openFile)
button.config(font=('', 20))
label = Label(root, text=path)
label.pack()
button.pack(pady=30)
close = Button(root, text='Done', command=root.destroy)
close.config(font=('', 20))
close.pack()
root.mainloop()

# Read the input file
with open(path, 'r') as rf:
    with open('log.csv', 'w') as wf:
        for line in rf:
            wf.write(line.replace("\t", ","))

rf.close()
wf.close()

data = []

# Convert the input data into csv type
with open('log.csv', 'r') as f:
    value = csv.reader(f)
    for row in value:
        data.append(row)

    f.close()

listI = []
listV = []
power = []
power_list = []
# Convert current data into numerical form
for x in range(1, len(data), 1):
    listI.append(float(data[x][1]))

# Convert voltage data into numerical form
for y in range(1, len(data), 1):
    listV.append(float(data[y][0]))

# Read the data quickly analyze them
sample_data = pd.read_csv('log.csv')

if len(sample_data.columns) == 2:
    sample_data.columns = 'Voltage', 'Current'
elif len(sample_data.columns) == 3:
    sample_data.columns = 'Voltage', 'Current', 'Abs Current'

# Prompt user to verify type of experiments
ans = input("Is this dark current case? ")
if ans.lower() == 'n' or ans.lower() == 'no':

    # Sort V and I in increasing order
    listI_sort = sorted(listI)
    listV_sort = sorted(listV)

    index_I = find_closet_num(listI_sort, 0)
    index_V = find_closet_num(listV_sort, 0)

    # Find out the value of voltage when current = 0
    for x in range(0, len(listI), 1):
        if listI[x] == index_I:
            VOC = abs(listV[x])

    # Find out the value of current when voltage = 0
    for y in range(0, len(listV), 1):
        if listV[y] == index_V:
            ISC = abs(listI[y])

    # Calculate power curve
    for z in range(0, len(listI), 1):
        power.append(listV[z] * listI[z])

    # Insert power curves into a list
    for i in range(0, len(power), 1):
        if power[i] < 0:
            power_list.append(power[i])

    # Prepare the result for lamp case
    result_1 = [
        ['Voltage open circuit (V)', round(VOC, 5)],
        ['Current short circuit (mA)', round(ISC*1000, 5)],
        ['Maximum power (mW)',  round(abs(min(power_list))*1000, 5)],
    ]

    print_table(result_1)

    sample_data['Power'] = sample_data['Voltage'] * sample_data['Current']
    # Plot current and voltage
    plt.plot(sample_data['Voltage'], sample_data['Current'])
    # Plot power and voltage
    plt.plot(sample_data['Voltage'], sample_data['Power'])
    # Plot edit
    plt.legend(["Current A", "Power W"])
    plt.xlabel('Voltage V')
    plt.ylabel('Current A')
    plt.tight_layout()
    plt.grid(True)
    plt.ylim(None, 0)

    plt.show()

elif ans.lower() == 'y' or ans.lower() == 'yes':

    sample_data['Ln Current'] = np.log(abs(sample_data['Current']))

    # Compute the trend line y = mx +b
    coeff = np.polyfit(sample_data['Voltage'], sample_data['Ln Current'], 1)
    m = coeff[0]
    b = coeff[1]

    # Compute coefficient of determination from residuals
    cfit = m * sample_data['Voltage'] + b
    residuals = cfit - sample_data['Ln Current']
    r2 = 1 - np.sum(residuals**2) / \
        np.sum((sample_data['Ln Current'] -
               np.mean(sample_data['Ln Current']))**2)

    # Prepare the result for dark current case
    result = [
        ['Gradient of linear region', round(m, 5)],
        ['Coefficient of determination', round(r2, 5)],
        ['Ideality factor', round(1.6e-19/(298*m*1.38e-23), 5)],
    ]

    print_table(result)

    # Plot the graph of natural log current against voltage
    plt.plot(sample_data['Voltage'], sample_data['Ln Current'])
    plt.xlabel('Voltage/V')
    plt.ylabel('ln(current)/A')
    plt.tight_layout()
    plt.grid(True)

    plt.show()

input()
