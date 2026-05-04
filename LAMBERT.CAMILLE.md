# How the window length of the dsSST algorithm affects the estimation of the cadence and the fondamental frequency of a sustained harmonic walk found with the wrist accelerometer data

### Introduction of the project
The de shape synchrosqueezing transform (dsSST) extracts the instantaneous frequency of a signal by a combinaison of two non linear operations, the de shape operation and the synchrosqueezing operation. This reable technique used to extract he fondamental frequency of a sustained harmonic walk can be used in futur works to extract the period of walk from the hamrnic component of the signal.

The reacher question behind this work is: Is the detection of walk cadence by the deshape synchrosqueezing on acceleration data the same for sensor position on the wrist incomparaison with sensor on the feet for stroke patient who can walk without physical assistance ?

The goal of this work is to asset the capacity of the dsSST algorithm to found the fundamental frequency from accelerometer data of sensor worn at the feets, wrists, sacrum of a stroke patient.

The deshape synchrosqueezing transform is a powerful tool to extract the fundamental frequency of a sustained harmonic walk from accelerometer data. The pipeline used in this work have been done from the article of Wu et Harezlak, « Application of de-shape synchrosqueezing to estimate gait cadence from a single-sensor accelerometer placed in different body locations ».
Change have been made to stabilise the short time ceptrum transform with the implementation of a long pass filter. This method is based on the article of Lin et al., « Wave-Shape Function Analysis -- When Cepstrum Meets Time-Frequency Analysis».

The dataset used in this work have been choice because it's have walk data of stroke patients with sensors at the feets, wrists and sacrum. The dataset is Zhou et al., « Dataset for Monitoring and Visualizing Stroke Rehabilitation Progress using Wearable Sensors (IMU) ». It's available in https://zenodo.org/records/10534055

This folder has been made with the help of the work of Victor Fernando Lopes De Souza, who made the code for the extraction of Marion data and the GitHub activity_acc_clustering

### Code construction
The code construction has been helping a lot with the co-pilot IA and Claude IA.

In this folder you will find a python directory who contains the code for handeling the data information and extracting the fondamental frequency from the dsSST pipeline .

In the R directory you will find the code for the statistical analysis of the results and the visualisation of the results.

### Analysis of the results 

The result show us that the sensor location doesn't have a significant impact on the ability to find the fundamental frequency of the walk with the dsSST algorithm.


### Bibliography

Wu, Hau-Tieng, et Jaroslaw Harezlak. « Application of de-shape synchrosqueezing to estimate gait cadence from a single-sensor accelerometer placed in different body locations ». Physiological Measurement 44, nᵒ 5 (2023): 055009.
Lin, Chen-Yun, Su Li, et Hau-Tieng Wu. « Wave-Shape Function Analysis -- When Cepstrum Meets Time-Frequency Analysis | Request PDF ». ResearchGate, publication en ligne anticipée, 5 août 2025. https://doi.org/10.1007/s00041-017-9523-0.
Zhou, Lin, Torsten Rackoll, Lennard Ekrod, et al. « Dataset for Monitoring and Visualizing Stroke Rehabilitation Progress using Wearable Sensors (IMU) ». Zenodo, 19 janvier 2024. https://doi.org/10.5281/zenodo.10534055.
Zhou, Lin, Torsten Rackoll, Lennard Ekrod, et al. « Monitoring and Visualizing Stroke Rehabilitation Progress using Wearable Sensors ». 2024 46th Annual International Conference of the IEEE Engineering in Medicine and Biology Society (EMBC), juillet 2024, 1‑6. https://doi.org/10.1109/EMBC53108.2024.10782489.


Muradeli, John. OverLordGoldDragon/ssqueezepy. Python. 29 janvier 2020, released 2 février 2026. https://github.com/OverLordGoldDragon/ssqueezepy.
« pandas.melt — pandas 3.0.2 documentation ». Consulté le 29 avril 2026. https://pandas.pydata.org/docs/reference/api/pandas.melt.html.
« pandas.read_csv — pandas 3.0.2 documentation ». Consulté le 28 avril 2026. https://pandas.pydata.org/docs/reference/api/pandas.read_csv.html.




