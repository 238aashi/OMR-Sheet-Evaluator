import cv2
import csv
import os
import main
import time
import pandas as pd

start_time=time.time()
input_dir = "../set1/"
output_file1 = "output1.csv"
output_file2 = 'output2.xlsx'

all_results = []
idx=0
for filename in os.listdir(input_dir):
    if filename.endswith(".jpg"):
        # Process the OMR sheet
        results = main.process_omr_sheet(os.path.join(input_dir, filename),idx,4,-1,0,68)
        # Add the results to the list of all results
        all_results.append([*results])
        idx+=1

with open(output_file1, 'w', newline='') as csvfile:
    writer = csv.writer(csvfile)
    writer.writerow(["S.No","RegNo", "Set", "SchoolCode", "CorrectAns", "IncorrectAns", "Left", "Score"])
    for row in all_results:
        writer.writerow(row)


# Convert the list of results to a pandas DataFrame
df = pd.DataFrame(all_results, columns=["S.No","RegNo", "Set", "SchoolCode", "CorrectAns", "IncorrectAns", "Left", "Score"])

# Write the DataFrame to an Excel file
df.to_excel(output_file2, index=False)
end_time=time.time()
print("Time Taken : ")
print(end_time-start_time)
# print(all_results)
