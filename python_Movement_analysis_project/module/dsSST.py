# Install required packages in this Python environment
import sys
import subprocess
from tkinter import SW

# kick fix for the problem of the import of ssqueezepy in Mac and Windows
def install(package):
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-q", package])
    except subprocess.CalledProcessError:
        # Fallback pour macOS / Python géré par le système
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-q", "--user", package])

try:
    import ssqueezepy
except ImportError:
    install("ssqueezepy")
    import ssqueezepy


# Import necessary libraries
import numpy as np 
import scipy as scipy
import scipy.signal as signal
from scipy import stats
import scipy.interpolate as interpolate
import ssqueezepy as ss

"""
Algorithme of de shape synchrosequeezing is based on the work of Hau Tieng Wu and Chen-Yun Lin 
for analyse a non stationary signal with two non linear combined method . 
The STC (short time cepstrum) and the iSTC (inverse shor time cepstrum) combined with SST (synchrosqueezing)
The aim of this algorithm is to found the cadence during the gait by mutiply the instantaneous frequency by two

The ssquezepy is need for the SST it's have been done by John Muradeli, ssqueezepy, 2020. GitHub repository, https://github.com/OverLordGoldDragon/ssqueezepy/. DOI: 10.5281/zenodo.5080508

The algorthim have 6 different steps:
1.preprocessing the data by detrend and butterworth them
2.Compute the STFT of the signal (V_Zxx)
3.Compute the STC of the signal and the iSTC of the signal (C_lifted, U)
4.Compute the deshape STFT by a hadamard product between the STFT and the iSTC (W)
5.Compute the synchrosqueezing of the deshape STFT (dsSST)
6. extract the curve of dsSST
7.Compute the instantaneous frequency

Your input need his : Signal_norm ,frequency,
The output are : instantaneous_frequency, V_Zxx, C_lifted, U, W, dsSST
"""
def dsSST(Signal_norm ,frequency,gamma=10**-9,lambda_reg=1,lifter_threshold=10,window_length_s=12):

    # -------------------------------------------------------------------------
    # Step 1 : Preprocessing
    # -------------------------------------------------------------------------
    #detrend and butterworth the signal

    f = np.asarray(Signal_norm, dtype=float).copy()

    # Interpolate NaN values
    nan_mask = np.isnan(f)
    if np.any(nan_mask):
        valid = ~nan_mask
        if np.sum(valid) < 2:
            return None
        idx_arr = np.arange(len(f), dtype=float)
        f[nan_mask] = np.interp(idx_arr[nan_mask], idx_arr[valid], f[valid])

    # Article: "detrend by the standard median filter with order 10*fs"
    median_order = int(10 * frequency)
    if median_order % 2 == 0:
        median_order += 1
    trend = signal.medfilt(f, kernel_size=median_order)
    f_detrended = f - trend

    # Article: "rectify the detrended signal (take the magnitude)"
    f_rect = np.abs(f_detrended)

    # b, a = signal.butter(4, 0.5 / (frequency / 2), btype='highpass')
    # sig = signal.filtfilt(b, a, f_rect)

    # -------------------------------------------------------------------------
    # Step 2 : STFT
    # -------------------------------------------------------------------------
    #than do the stft of the signal to have the V matrix for the hadamard product with the iSTC
    nperseg = int(frequency * window_length_s)
    K = nperseg // 2
    window_len = 2 * K + 1

    # Exact construction according to the paper
    k = np.arange(1, window_len + 1)
    sigma = 0.15  # free parameter, to be tested

    h_window = np.exp(-((k - 1) / (2 * K) - 0.5) ** 2 / (2 * sigma ** 2))

    V_f, V_t, V_Zxx = V=signal.stft(x=f_rect,
              fs=frequency,
              window=h_window,
              nperseg=window_len,
              noverlap=window_len // 2,
              nfft=None,
              return_onesided=True,
              boundary=None,
              padded=False,
              axis=-1)
    
    
    # -------------------------------------------------------------------------
    # Step 3 : STC + iSTC
    # -------------------------------------------------------------------------
    #compute the stc of the signal and the iSTC of the signal
    espilon = 1e-12
    V_Zxx_modulate=np.abs(V_Zxx)**0.3# modulate by a power law to enhance the fundamental frequency component in the cepstrum like in the paper of Hau Tieng Wu and Chen-Yun Lin
    C = np.fft.fft(V_Zxx_modulate, axis=0)# the cepstrum can be done by a ifft or a fft , we do a fft like in the paper of Hau Tieng Wu and Chen-Yun Lin 
    
    """the iSTCT is numerically unstable to stabilise it you have two solution:
    .do a long long-pass lifter of the cepstrum to isolate the fundamental quefrency component in the cepstrum 
    .discretize I by a suitable weighting, for example, by the Jacobian of I, so that the iSTCT is defined on the uniform frequency grid."""
    
    # High frequency threshold to pass in U(f)
    # Exclude the quefrencies below this threshold, normally between [10,20] according to Lin et al. 2018
    C_lifted = np.copy(C)
    C_lifted[:lifter_threshold, :] = 0  # We want to do a long long-pass lifter to isolate the fundamental quefrency component in the cepstrum
    
    # inverse short time cepstrum
    # iSTCT by inverse-axis interpolation: U(f) = C(q=1/f)
    # Build quefrency axis from STFT frequency step
    # iSTC: U(f) = C(q=1/f)  — evaluate cepstrum at quefrency q = 1/f
    N= len(V_f)
    delta_f =(V_f[1] - V_f[0])  # resolution in quefrency

    q_axis=np.arange(N)/(N*delta_f)  # quefrency axis
    U=interpolate.interp1d(q_axis, C_lifted, axis=0, bounds_error=False, fill_value=0)((1.0 / V_f))
    
    # -------------------------------------------------------------------------
    # Step 4 : Deshape STFT (Hadamard product)
    # -------------------------------------------------------------------------
    # Deshape STFT by a Hadamard product between V and U
    """The deshape STFT is computed by a Hadamard product between the STFT and the iSTC, 
    it is a way to enhance the fundamental frequency component in the STFT by multiplying it with the iSTC 
    which have been lifter to isolate the fundamental quefrency component in the cepstrum"""

    W = (V_Zxx) * (U)

    # -------------------------------------------------------------------------
    # Step 5 : Synchrosqueezing
    # -------------------------------------------------------------------------
    # compute the synchrosqueezing of the deshape STFT

    dWx = np.gradient(W, V_t, axis=1, edge_order=2)# compute the derivative of W with respect to time
    dsSST = ss.ssqueeze(
        Wx=W,# the signal to be synchrosqueezed, in our case the deshape STFT            
        w=None,
        ssq_freqs=V_f,
        scales=None,  # we provide the frequencies, so ssqueeze won't compute the scales internally
        dWx=dWx,  # we provide the derivative dWx, so ssqueeze won't compute it internally
        Sfs=V_f,
        gamma=gamma,# lower threshold to avoid suppressing almost all energy
        transform='stft',
        fs=frequency,
        squeezing='sum',
        maprange='maximal'
        )
    # Tx: time frequency representation of the deshape STFT, it is a 2D array where the first dimension is the frequency and the second dimension is the time
    Tx = np.asarray(dsSST[0])
    freq_axis = np.asarray(dsSST[1])
    power = np.abs(Tx) ** 2

    # -------------------------------------------------------------------------
    # Step 6 : Extraction of the c* curve by dynamic programming
    # -------------------------------------------------------------------------
    """
    The curve c* is the curve that maximizes the energy in the synchrosqueezed representation while penalizing rapid changes in frequency. 
       c* = argmax  Σ log(|SW(c(m), m)| / Σ_j |SW(j, m)|)- λ Σ |c(m) - c(m-1)|

    The frist term set the curve to follow the maximum energy in the synchrosqueezed representation, 
    while the second term penalize rapid changes in frequency by adding a regularization term 
    that is proportional to the absolute difference between the current frequency bin and the previous frequency bin.

    The dynamic processing follow a Viterbi like algorithm where we compute a score matrix that is the sum of the log of the energy 
    and we capture the backtrack to extract the curve c* that maximize the score.

    """
    # Preparation
    SW    = Tx.T                    # [N_time, N_freq] — no more restriction
    interval_len = SW.shape[0]        # N_time
    M_band       = SW.shape[1] - 1   # all frequency bins
    # Frame normalisation: for each time step m, the value is divided by the sum of the amplitudes in the frame. 
    # This makes the functional comparable across frames (each frame contributes equally, regardless of its absolute amplitude).
    denom_per_frame = np.abs(SW).sum(axis=1)  # [N_time]
    denom_per_frame = np.maximum(denom_per_frame, 1e-12)  # protection 

    # Initialization by calculating the frequency resolution and the regularization cost
    # df[m, k]        : best score for a path ending at c(m) = k.
    # backtrack[m, k] : best predecessor c(m-1) that maximizes df[m, k].

    df        = np.full((interval_len, M_band + 1), -np.inf) # [N_temps, N_freq]
    backtrack = np.zeros((interval_len, M_band + 1), dtype=int)  # sur tous les bins fréquentiels permet de le faire localement
    
    # Matric cost of regularization (total variation penalty) for transitions between frequency bins:
    # reg_matrix[k, k'] = λ * |k - k'|
    # Penalizes transitions from bin k' to bin k proportionally to their distance.
    c_range   = np.arange(M_band + 1)
    reg_matrix = lambda_reg * np.abs(c_range[:, None] - c_range[None, :])
    # Initialization of the first time step (m=0) by the log of the normalized energy in the synchrosqueezed representation for each frequency bin:
    df[0, :] = np.log(np.abs(SW[0, :]) / denom_per_frame[0] + 1e-12)

    # ---- Forward recurrence ----
    # At each time step, for each target bin k, we look for the best
    # previous bin k' that maximizes (score at time m-1 - transition cost).
    for t in range(1, interval_len):
        # normalized energy at the current frame (data attachment term)
        log_terms       = np.log(np.abs(SW[t, :]) / denom_per_frame[t] + 1e-12)
        # scores[k, k'] = df[t-1, k'] - λ |k - k'|
        scores_matrix   = df[t-1, :][None, :] - reg_matrix
        # for each target k, we keep the optimal k'
        backtrack[t, :] = np.argmax(scores_matrix, axis=1)
        # update : score = data attachment term + best transition score
        df[t, :]        = log_terms + scores_matrix[c_range, backtrack[t, :]]

    # ---- "Backtracking" : build optimal path ----
    # We start from the final time step (choosing the best bin), then move backward in time following the predecessors stored in `backtrack`.
    c_opt     = np.zeros(interval_len, dtype=int)
    c_opt[-1] = np.argmax(df[-1, :])
    for t in range(interval_len - 2, -1, -1):
        c_opt[t] = backtrack[t + 1, c_opt[t + 1]]

    # -------------------------------------------------------------------------
    # Step 7 : Instantaneous frequency and fundamental frequency
    # -------------------------------------------------------------------------
    # Conversion of c* indices to real frequencies (Hz)
    instantaneous_frequency = freq_axis[c_opt]  # equivalent to c_opt * (fs / 2M)
    median_instantaneous_frequency = float(np.median(instantaneous_frequency[instantaneous_frequency > 0]))

    return (
        median_instantaneous_frequency,
        V_Zxx, V_f, V_t,
        C_lifted, U, W,
        Tx, freq_axis
    )