# File 3: spo2.py

import numpy as np
from scipy.signal import butter, filtfilt, find_peaks


def calculate_spo2(ir_buffer, red_buffer, sampling_rate=50):
    if len(ir_buffer) < sampling_rate * 8:
        return None
    
    ir_data = np.array(ir_buffer)
    red_data = np.array(red_buffer)
    
    window_size = min(len(ir_data), sampling_rate * 8)
    ir_segment = ir_data[-window_size:]
    red_segment = red_data[-window_size:]
    
    ir_centered = ir_segment - np.mean(ir_segment)
    
    nyquist = sampling_rate / 2
    b, a = butter(3, [0.7/nyquist, 3.5/nyquist], btype='band')
    filtered = filtfilt(b, a, ir_centered)
    
    filtered_norm = filtered / (np.std(filtered) + 1e-9)
    derivative = np.abs(np.diff(filtered_norm, prepend=filtered_norm[0]))
    
    window = int(0.1 * sampling_rate)
    kernel = np.ones(window) / window
    enhanced = np.convolve(derivative, kernel, mode='same')
    
    threshold = np.mean(enhanced) + 0.5 * np.std(enhanced)
    min_distance = int(0.4 * sampling_rate)
    
    peaks, _ = find_peaks(enhanced, height=threshold, distance=min_distance)
    
    if len(peaks) < 2:
        return None
    
    spo2_values = []
    
    for i in range(len(peaks) - 1):
        start = peaks[i]
        end = peaks[i + 1]
        
        if end - start < 3:
            continue
        
        ir_beat = ir_segment[start:end]
        red_beat = red_segment[start:end]
        
        ac_ir = np.max(ir_beat) - np.min(ir_beat)
        dc_ir = np.mean(ir_beat)
        ac_red = np.max(red_beat) - np.min(red_beat)
        dc_red = np.mean(red_beat)
        
        if dc_ir == 0 or dc_red == 0:
            continue
        
        R = (ac_red / dc_red) / (ac_ir / dc_ir)
        spo2_val = 104 - 17 * R
        
        spo2_values.append(spo2_val)
    
    if len(spo2_values) == 0:
        return None
    
    return np.clip(np.mean(spo2_values), 70, 100)