# Prediction of walking periods with the combination of the de shape synchrosqueezing transform and the sustained harmonic walking algorithm

This work have been done with the help of Claude IA and Copilot IA. 

This folder has been made with the help of the work of Victor Fernando Lopes De Souza.

In this work you will fond 3 main directories. The first one the python_Movement_analysis_project contains the code for handling the data and processing them. The r_Movement_analysis_project contains the code for the analysis of the data and visualisation of them. The last one is the results directory where you can find the results of the analysis.
You are able to found also the LAMBERT.Camille foulders who contain the information background and the reasons for this work around the necessity of the foundamental frequency of the walk.

The repository is organized as follows:
The repository is organized as follows:
- `python_Movement_analysis_project/`: Contains the Python code for data handling and processing.
- `r_Movement_analysis_project/`: Contains the R code for data analysis and visualization.
- `results/`: Contains the results of the analysis.
- `LAMBERT.Camille/`: Contains background information and the rationale for this work
- `Readme/`: Contains information about the project and its structure.

## python_Movement_analysis_project
You have three main directories in the python_Movement_analysis_project. 
    - 1  the data directory where you can find the data used for this work. 
    - 2 the module directory where you can find the code for handling the data and processing with the dsSST.

The dsSST is the heart the pipe line found in the module directory will allow you to compute a accelerometer signal and to extract the fundamental frequency of this periodic signal. You will have also the information on the time frequency representation of the signal with the Short Time Fourier Transform and the de shape synchrosqueezing transform.
The important package in this work is the ssqueezepy package of "John Muradeli, ssqueezepy, 2020. GitHub repository, https://github.com/OverLordGoldDragon/ssqueezepy/. DOI: 10.5281/zenodo.5080508"
The other packages needed are : numpy , panda, matplotlib, scipy, librosa

The data used in this work is the one from the data of Zhou et al., « Dataset for Monitoring and Visualizing Stroke Rehabilitation Progress using Wearable Sensors (IMU) ».

## The r_Movement_analysis_project
In this direcory you can found the rmd statisque_analyse_of_results where you can found the code for the statistical analysis of the results. 

## Project structure

```
python_Movement_analysis_project/    # Python code for data handling and processing
├── data/
│   └── imu0001/
│       ├── visit1/
│       │   └── imu/
│       │       ├── LF/
│       │       ├── RF/
│       │       ├── LW/
│       │       ├── RW/
│       │       └── SA/
│       └── visit2/
│           └── imu/
│               ├── LF/
│               ├── RF/
│               ├── LW/
│               ├── RW/
│               └── SA/
├── module/
│   ├── dsSST/
│   └── handle_data/
└── Notebook/
    └── notebook_python/

r_Movement_analysis_project/         # R code for data analysis and visualization
├── statisque_analyse_of_results/
└── analyse_stat_dsSST/

results/                             # Analysis results
├── RF_visit1_analysis/
└── frequency_summary/
```


## Bibliography 
The following article contains the theoretical background and the imortant source for the work 

Wu, Hau-Tieng, and Jaroslaw Harezlak. « Application of de-shape synchrosqueezing to estimate gait cadence from a single-sensor accelerometer placed in different body locations .» Physiological Measurement 44, nᵒ 5 (2023): 055009.
Lin, Chen-Yun, Su Li, et Hau-Tieng Wu. « Wave-Shape Function Analysis -- When Cepstrum Meets Time-Frequency Analysis | Request PDF ». ResearchGate, publication en ligne anticipée, 5 août 2025. https://doi.org/10.1007/s00041-017-9523-0.
Zhou, Lin, Torsten Rackoll, Lennard Ekrod, et al. « Monitoring and Visualizing Stroke Rehabilitation Progress using Wearable Sensors ». 2024 46th Annual International Conference of the IEEE Engineering in Medicine and Biology Society (EMBC), juillet 2024, 1‑6. https://doi.org/10.1109/EMBC53108.2024.10782489.
Zhou, Lin, Torsten Rackoll, Lennard Ekrod, et al. « Dataset for Monitoring and Visualizing Stroke Rehabilitation Progress using Wearable Sensors (IMU) ». Zenodo, 19 janvier 2024. https://doi.org/10.5281/zenodo.10534055.
Muradeli, John. OverLordGoldDragon/ssqueezepy. Python. 29 janvier 2020, released 2 février 2026. https://github.com/OverLordGoldDragon/ssqueezepy.
