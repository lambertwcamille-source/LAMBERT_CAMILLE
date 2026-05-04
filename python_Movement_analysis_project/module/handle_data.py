# Install required packages in this Python environment
import re
import sys
import subprocess



# Import necessary libraries
import numpy as np 
import scipy as scipy
import pandas as pd
from unicodedata import name
from pathlib import Path

# Import the necessary  module
from dsSST import dsSST

"""
This module contains functions to extract features from the raw data. This is build to handle the data from the dataset of Zhou and al.
-'find_patient_visits': to return a dictionary information of {visit, imu_dir} in the dataset
-'load_acc_norm': to load the data of the accelerometer and return the norm of the acceleration and the time of a IMU sensor
-'fac_visit_from_info': to extract the FAC score of a given patient and visit from the participants.csv file.
-'Time_frequency_analyse': to apply the deshape synchrosqueezing transform on the norm of the acceleration to extract the fundamental frequency and the cadence of the walk and the time-frequency representation of the signal.

The function have been made with the help of claude IA. In case of problems a triangualation have been made with Copilot IA
All of the source used in the code Can be found in the End of this file in the "Sources" section.

"""
def find_patient_visits(data_root: Path):
    """
    Find the data of the dataset in the following path data_root/imuXXXX/visitN/imu/. 
    If the directory does not exist or it's not in the correct format, it is not added to the list.
    ----------------------------INPUT----------------------------
    data_root: Path to the root directory of the dataset, which contains the patient directories (imuXXXX).
    ----------------------------OUTPUT----------------------------
    A list of dictionaries, each containing {visit, imu_dir} for each valid patient visit found in the dataset.
    """
    # Initialize an empty list to store the information about patient visits
    information = []

    # We are going to find the directories of the visits, which are in the format "visitN" where N is a number, and then find the directory "imu" in each visit directory
    # sorted(...) ensures a consistent order of visits (ex: visit1 before visit2)
    for visit_dir in sorted(data_root.iterdir()):
        # Security to take only the directories and not the files that may be in the patient_dir
        if not visit_dir.is_dir():
                continue
        # re.match used to select only the directories beginning with "visit"
        if not re.match(r"visit\d+", visit_dir.name):
            continue
        # Find the "imu" directory within the visit directory
        imu_dir = visit_dir / "imu"
        # Check if the "imu" directory exists and is a directory, if so, add the information to the list
        if imu_dir.is_dir():
                information.append({
                    "visit": visit_dir.name,
                    "imu_dir": imu_dir,
                })
    return information

def load_acc_norm(csv_path: Path):
    """
    In our work we are going to use only the accelerometer data (accx, accy, accz) and the time of the IMU 
    For the deshape Synchrosqueezing algortihm only the norm is need to extract the fundamental frequency of the walk.
    So this function is used to compute the norm of the acceleration. The norm is the length of the acceleration vector, which is computed as sqrt(accx^2 + accy^2 + accz^2).
    ----------------------------INPUT----------------------------
    csv_path: Path to the csv file containing the raw data of the IMU sensor, which should contain at the columns "timestamp", "accx", "accy", "accz"
    ----------------------------OUTPUT----------------------------
    ts: numpy array containing the time of the IMU sensor, extracted from the "timestamp" column of the csv file.
    norm: numpy array containing the norm of the acceleration, computed from the "accx", "accy", "accz" columns of the csv file.
    """
    # Security check to ensure that the csv file exists
    if not csv_path.exists():
        return None, None

    # Frist we read the header of the csv file to find the columns we need, and to be able to handle the case where the columns are not in the same order
    # we are using pandas to read the csv file, and we read only the first row (nrows=0) to get the name of the data columns.
    # The columns are selected by .columns and transformed to a list by .tolist()
    colums_name = pd.read_csv(csv_path, nrows=0).columns.tolist()
    # for security we create a dictionary that maps the lowercase version of the column names to handle majuscule/minuscule differences.
    colums_name = {c.lower(): c for c in colums_name}
    # Dictionary of the columns we want extract. We initialise the values to None
    name_wanted = {"timestamp": None, "accx": None, "accy": None, "accz": None }
    # In a this loop we check if the columns we want extract are in the  file
    for key in list(name_wanted.keys()):
        if key in colums_name:
            name_wanted[key] = colums_name[key]
        # If a column is missing, we raise a ValueError with a message indicating which column is missing 
        else:
            raise ValueError(f"Column '{key}' missing in {csv_path.name}")

    # extract the columns we are going to use from the csv file using the name_wanted dictionary, and we convert them to numpy arrays.
    Used_name = list(name_wanted.values())
    df = pd.read_csv(csv_path, usecols=Used_name)

    ts   = df[name_wanted["timestamp"]].to_numpy()
    # we specify dtype=float to ensure that the data is in the correct format for the computation of the norm
    ax   = df[name_wanted["accx"]].to_numpy(dtype=float)
    ay   = df[name_wanted["accy"]].to_numpy(dtype=float)
    az   = df[name_wanted["accz"]].to_numpy(dtype=float)
    norm = np.sqrt(ax**2 + ay**2 + az**2)

    return ts, norm





def Time_frequency_analyse(signal_norm, fs, **dsSST_paramaters):
    """Application of the dsSST on the accelerometer norm to find the cadence and the fundamental frequency.
    -----------------------------INPUT----------------------------
    signal_norm: numpy array containing the norm of the acceleration, computed from the "accx", "accy", "accz" columns of the csv file.
    fs: sampling frequency of the IMU sensor
    dsSST_paramaters : paramater to compute the deshape synchrosqueezing transform.
        It should contain the following keys:
        - "gamma": the gamma parameter of the dsSST is the threshold for the synchrosqueezing step
        - "lambda_reg": penelization parameter for the extraction by recurence 
        - "lifter_threshold": the threshold for the liftering step, which is used to remove the low quefrency components of the signal.
        - "window_length_s": the length of the window used for the short-time Fourier transform (STFT) in seconds.
    -----------------------------OUTPUT----------------------------
    A dictionary containing the following keys:
    - "f0_freq_hz": the fundamental frequency of the walk, extracted from the deshape synchrosqueezing transform of the signal.
    - "cadence": the cadence of the walk, computed from the fundamental frequency as cadence = f0_freq_hz*2
    - "V_Zxx": the deshape synchrosqueezing transform of the signal, which is a time-frequency representation of the signal.
    - "V_f": the frequency axis of the deshape synchrosqueezing transform
    - "V_t": the time axis of the deshape synchrosqueezing transform
    - "Tx": the time-frequency representation of the signal obtained by applying the deshape synchrosqueezing transform
    - "freq_axis": the frequency axis of the deshape synchrosqueezing transform

    """
    result = dsSST(signal_norm, fs, **dsSST_paramaters)
    if result is None:
        return None
    (peak_frequency_hz,
     V_Zxx, V_f, V_t,
     C_lifted, U, W,
     Tx, freq_axis) = result
    return {
        "peak_frequency_hz":      peak_frequency_hz,
        "V_Zxx": V_Zxx, "V_f": V_f, "V_t": V_t,
        "C_lifted": C_lifted, "U": U, "W": W,
        "Tx": Tx, "freq_axis": freq_axis,
    }


"""
Sources: these is the list of the sources used to write the code . The source are listed in the function in which they are used.

The dataset: Zhou, Lin, Torsten Rackoll, Lennard Ekrod, et al. « Dataset for Monitoring and Visualizing Stroke Rehabilitation Progress using Wearable Sensors (IMU) ». Zenodo, 19 janvier 2024. https://doi.org/10.5281/zenodo.10534055.
The article of the data set: Zhou, Lin, Torsten Rackoll, Lennard Ekrod, et al. « Monitoring and Visualizing Stroke Rehabilitation Progress using Wearable Sensors ». 2024 46th Annual International Conference of the IEEE Engineering in Medicine and Biology Society (EMBC), juillet 2024, 1‑6. https://doi.org/10.1109/EMBC53108.2024.10782489.

Used in the function "find_patient_visits":
- The use of the Path library to navigate through the directories: TradingCode, « Find out If a Path Is an Existing Directory with Python’s `Path.Is_dir()` Method ».
- The use  of the re library to see if the directory name starts with "imu" or "visit" : GeeksforGeeks, « Re.Match() in Python ».

Used in the function "load_acc_norm":
- The use of pandas to read the csv file and extract the header by nrows=0: « pandas.read_csv — pandas 3.0.2 documentation ».

Used in the function "Time_frequency_analyse":
- Information about the deshape synchrosqueezing transform and its parameters are in the file "dsSST.py" store in the same directory as this file. 

"""
