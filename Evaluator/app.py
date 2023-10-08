import os
import shutil
import tkinter as tk
from tkinter import ttk
from tkinter import filedialog, messagebox
import pandas as pd
import time
import main
import cv2

output_file1 = "abstract.xlsx"
output_file2 = 'detailed.xlsx'

# Get the parent directory
parent_dir = os.path.dirname(os.getcwd())

# Create folders
os.makedirs(os.path.join(parent_dir, "non_evaluated"), exist_ok=True)
os.makedirs(os.path.join(parent_dir, "evaluated"), exist_ok=True)

class App:
    def __init__(self, root):
        self.root = root
        self.root.title("NCC OMR Sheet Evaluator")
        self.root.geometry("600x500")
        self.folder_path = ""
        self.answer_key_path = ""
        
        # Set the background color to a calm blue
        self.root.config(bg="#add8e6")
        

        self.label = tk.Label(self.root, text="Click on the Start Button to Begin!")
        self.label.pack(pady=10)

        self.btn_start = tk.Button(self.root, text="Start", command=self.start, width=10)
        self.btn_start.pack(pady=15)

    def start(self):
        # destroy start button
        self.btn_start.destroy()

        self.label.config(text="Enter Marking Scheme for:")
        # Create a label frame to group the input fields
        self.input_frame = ttk.LabelFrame(root, text="")
        self.input_frame.pack(padx=10, pady=10)
        
        # Create labels and text fields for each input
        default_correct = 4
        self.label1 = ttk.Label(self.input_frame, text="Correct Answers:")
        self.label1.grid(row=0, column=0, padx=5, pady=5)
        self.text_field1 = ttk.Entry(self.input_frame)
        self.text_field1.insert(0, default_correct)
        self.text_field1.grid(row=0, column=1, padx=5, pady=5)

        default_incorrect = -1
        self.label2 = ttk.Label(self.input_frame, text="Incorrect Answers:")
        self.label2.grid(row=1, column=0, padx=5, pady=5)
        self.text_field2 = ttk.Entry(self.input_frame)
        self.text_field2.insert(0, default_incorrect)
        self.text_field2.grid(row=1, column=1, padx=5, pady=5)

        default_left = 0
        self.label3 = ttk.Label(self.input_frame, text="Unattemped:")
        self.label3.grid(row=2, column=0, padx=5, pady=5)
        self.text_field3 = ttk.Entry(self.input_frame)
        self.text_field3.insert(0, default_left)
        self.text_field3.grid(row=2, column=1, padx=5, pady=5)

        # Create the submit button widget and bind it to the handle_click function
        self.btn_submit = ttk.Button(root, text="Submit", command=self.mark_scheme)
        self.btn_submit.pack(pady=10)
        

    def mark_scheme(self):

        try:
            # Try to get the input values from the text fields
            self.input1 = int(self.text_field1.get())
            self.input2 = int(self.text_field2.get())
            self.input3 = int(self.text_field3.get())
           
        except ValueError:
            # If any input can't be converted to an integer, show an error message
            tk.messagebox.showerror("Error", "Please enter integers for all inputs.")
                                
        # destroy submit button
        self.btn_submit.destroy()
        self.input_frame.destroy()

        # Default Threshold for response evaluation
        default_threshold = 68
        self.label.config(text="Enter a threshold for response evaluation (50-100):")
        self.text_field = tk.Entry(root)
        self.text_field.insert(0, default_threshold)
        self.text_field.pack()

        self.btn_next1 = tk.Button(self.root, text="Next", command=self.threshold, width=10)
        self.btn_next1.pack(pady=10)


    def threshold(self):
        try:
            # Try to convert the input to an integer
            self.thresh = int(self.text_field.get())

        except ValueError:
            # If the input can't be converted to an integer, show an error message
            tk.messagebox.showerror("Error", "Please enter an integer.")
        
        # Destroy next button
        self.btn_next1.destroy()
        self.text_field.destroy()

        self.label.config(text="Select the desired Scanned OMRs and Answer Key Files to evaluate:")
        self.btn_browse1 = tk.Button(self.root, text="Upload OMRs Folder", command=self.browse_folder, width=15)
        self.btn_browse1.pack(pady=10)
        
        self.btn_browse2 = tk.Button(self.root, text="Upload Answer Key", command=self.browse_answerkey, width=15)
        self.btn_browse2.pack(pady=10)

        self.btn_next2 = tk.Button(self.root, text="Next", command=self.Next_Evaluate, state="disabled", width=12)
        self.btn_next2.pack(pady=10)

    def browse_folder(self):
        self.folder_path = filedialog.askdirectory()
        if self.folder_path:
            file_count = len(os.listdir(self.folder_path))
            messagebox.showinfo("File Count", f"Number of files in folder: {file_count}")
            self.label.config(text=f"OMRs Folder: {self.folder_path}", fg="blue")
            self.check_next_button_state()

    def browse_answerkey(self):
        self.answer_key_path = filedialog.askopenfilename(filetypes=[("Excel Files", "*.xlsx;*.xls")])
        if self.answer_key_path:
            self.label.config(text=f"Answer Key: {self.answer_key_path}", fg="blue")
            self.check_next_button_state()

    def check_next_button_state(self):
        if self.folder_path and self.answer_key_path:
            self.btn_next2["state"] = "normal"
        else:
            self.btn_next2["state"] = "disabled"
            
    def Next_Evaluate(self):

        #destroy next button
        self.btn_browse1.destroy()
        self.btn_browse2.destroy()
        self.btn_next2.destroy()

        self.label.config(text="Select the Desired Mode of Evaluation:")
        
        self.btn_fast = tk.Button(self.root, text="Fast Mode", command=self.evaluate_fast, width=10)
        self.btn_fast.pack(pady=10)

        self.btn_visibility = tk.Button(self.root, text="Visibility Mode", command=self.evaluate_visibility, width=12)
        self.btn_visibility.pack(pady=10)

        self.btn_correction = tk.Button(self.root, text="Correction Mode", command=self.evaluate_correction, width=14)
        self.btn_correction.pack(pady=10)        
    
    def evaluate_fast(self):
        start_time=time.time()
        all_results1 = []
        all_results2 = []
        idx=1

        #Clear folders
        shutil.rmtree(os.path.join(parent_dir, "evaluated"))

        # Create folders
        os.makedirs(os.path.join(parent_dir, "evaluated"), exist_ok=True)
        
        for filename in os.listdir(self.folder_path):
            if filename.endswith(".jpg"):
                # Process the OMR sheet
                results1,results2,imgInput,imgOutput = main.process_omr_sheet(os.path.join(self.folder_path, filename),idx, self.input1, self.input2, self.input3, self.thresh, self.answer_key_path)
                # Add the results to the list of all results
                all_results1.append([*results1])
                all_results2.append([*results2])
                idx+=1

                # Move the input and output images to the evaluated folder
                regno = results1[1]  # Assuming "RegNo" is the second item in results1
                cv2.imwrite(os.path.join(parent_dir, "evaluated", f"{regno}_inp.tif"), imgInput)
                cv2.imwrite(os.path.join(parent_dir, "evaluated", f"{regno}_out.tif"), imgOutput)

        # Convert the list of results to a pandas DataFrame
        df1 = pd.DataFrame(all_results1, columns=["S.No","RegNo", "Set", "SchoolCode", "CorrectAns", "IncorrectAns", "Left", "Score"])
        df2 = pd.DataFrame(all_results2)
        columns = ['S.No', 'RegNo', 'Set']
        columns.extend(['Q{}'.format(i) for i in range(1,76)])
        df2.columns = columns
        # Write the DataFrame to an Excel file
        df1.to_excel(output_file1, index=False)
        df2.to_excel(output_file2,index=False)

        self.download()
        end_time=time.time()
        print("Time Taken : ")
        print(end_time-start_time)

    def evaluate_visibility(self):
        start_time=time.time()
        all_results1 = []
        all_results2 = []
        idx=1

        #Clear folders
        shutil.rmtree(os.path.join(parent_dir, "evaluated"))

        # Create folders
        os.makedirs(os.path.join(parent_dir, "evaluated"), exist_ok=True)
        
        for filename in os.listdir(self.folder_path):
            if filename.endswith(".jpg"):
                # Process the OMR sheet
                results1,results2,imgInput,imgOutput= main.process_omr_sheet(os.path.join(self.folder_path, filename),idx, self.input1, self.input2, self.input3, self.thresh, self.answer_key_path)
                cv2.imshow("evaluated_image", imgOutput)
                cv2.waitKey(0)
                # Add the results to the list of all results
                all_results1.append([*results1])
                all_results2.append([*results2])
                idx+=1

                # Move the input and output images to the evaluated folder
                regno = results1[1]  # Assuming "RegNo" is the second item in results1
                cv2.imwrite(os.path.join(parent_dir, "evaluated", f"{regno}_inp.tif"), imgInput)
                cv2.imwrite(os.path.join(parent_dir, "evaluated", f"{regno}_out.tif"), imgOutput)

        # Convert the list of results to a pandas DataFrame
        df1 = pd.DataFrame(all_results1, columns=["S.No","RegNo", "Set", "SchoolCode", "CorrectAns", "IncorrectAns", "Left", "Score"])
        df2 = pd.DataFrame(all_results2)
        columns = ['S.No', 'RegNo', 'Set']
        columns.extend(['Q{}'.format(i) for i in range(1,76)])
        df2.columns = columns
        # Write the DataFrame to an Excel file
        df1.to_excel(output_file1, index=False)
        df2.to_excel(output_file2,index=False)

        self.download()
        end_time=time.time()
        print("Time Taken : ")
        print(end_time-start_time)

    def evaluate_correction(self):
        start_time=time.time()
        all_results1 = []
        all_results2 = []
        idx=1

        #Clear folders
        shutil.rmtree(os.path.join(parent_dir, "evaluated"))
        shutil.rmtree(os.path.join(parent_dir, "non_evaluated"))

        # Create folders
        os.makedirs(os.path.join(parent_dir, "non_evaluated"), exist_ok=True)
        os.makedirs(os.path.join(parent_dir, "evaluated"), exist_ok=True)
        
        for filename in os.listdir(self.folder_path):
            if filename.endswith(".jpg"):
                # Process the OMR sheet
                self.root.iconify()
                results1,results2,imgInput,imgOutput= main.process_omr_sheet(os.path.join(self.folder_path, filename),idx, self.input1, self.input2, self.input3, self.thresh, self.answer_key_path)
                cv2.imshow("Orignal_Image", imgInput)
                cv2.imshow("Evaluated_Image", imgOutput)
                #cv2.waitKey(0)
                confirmation = messagebox.askokcancel("Confirmation", "Are you sure you want to consider this Data?")
                if confirmation:
                    # Add the results to the list of all results
                    all_results1.append([*results1])
                    all_results2.append([*results2])
                    idx+=1

                    # Move the input and output images to the evaluated folder
                    regno = results1[1]  # Assuming "RegNo" is the second item in results1
                    cv2.imwrite(os.path.join(parent_dir, "evaluated", f"{regno}_inp.tif"), imgInput)
                    cv2.imwrite(os.path.join(parent_dir, "evaluated", f"{regno}_out.tif"), imgOutput)
                else:
                    # Move the file to the non_evaluated folder
                    regno = results1[1]
                    cv2.imwrite(os.path.join(parent_dir, "non_evaluated", f"{regno}.tif"), imgInput)
                    
                cv2.destroyAllWindows()
                self.root.deiconify()
        end_time=time.time()
        print("Time Taken : ")
        print(end_time-start_time)

        # Convert the list of results to a pandas DataFrame
        df1 = pd.DataFrame(all_results1, columns=["S.No","RegNo", "Set", "SchoolCode", "CorrectAns", "IncorrectAns", "Left", "Score"])
        df2 = pd.DataFrame(all_results2)
        columns = ['S.No', 'RegNo', 'Set']
        columns.extend(['Q{}'.format(i) for i in range(1,76)])
        df2.columns = columns
        # Write the DataFrame to an Excel file
        df1.to_excel(output_file1, index=False)
        df2.to_excel(output_file2,index=False)

        self.download()
       

    def download(self):
        # destroy browse and evaluate
        self.btn_fast.destroy()
        self.btn_visibility.destroy()
        self.btn_correction.destroy()
        
        self.label.config(text="Evaluation complete. Download the desired results file.", fg="green")

        self.btn_download1 = tk.Button(self.root, text="Abstract Result", command=lambda: os.startfile(output_file1), width=15)
        self.btn_download1.pack(pady=10)

        self.btn_download2 = tk.Button(self.root, text="Detailed Result", command=lambda: os.startfile(output_file2), width=15)
        self.btn_download2.pack(pady=10)
        end_time=time.time()


root = tk.Tk()

# Create a label with the logo image
logo_img = tk.PhotoImage(file="logo.png")
logo_label = tk.Label(root, image=logo_img, bg="#add8e6")
logo_label.pack(pady=20)

# Create a label with the heading text
heading_label = tk.Label(root, text="NCC OMR Sheet Evaluator", font=("Arial", 18, "bold"), bg="#add8e6")
heading_label.pack(pady=10)

app = App(root)

root.mainloop()
