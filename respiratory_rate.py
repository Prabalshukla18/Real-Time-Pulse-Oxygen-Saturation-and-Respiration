import numpy as np
from scipy.signal import butter, filtfilt, find_peaks


def calculate_respiratory_rate(ir_buffer, sampling_rate=50, window_duration=30):
    required_samples = sampling_rate * window_duration
    
    if len(ir_buffer) < required_samples:
        return None
    
    ir_data = np.array(ir_buffer)
    
    ir_centered = ir_data - np.mean(ir_data)
    
    nyquist = sampling_rate / 2
    b, a = butter(4, [0.1/nyquist, 0.5/nyquist], btype='band')
    filtered = filtfilt(b, a, ir_centered)
    
    min_distance = int(sampling_rate * 1.5)
    prominence = np.std(filtered) * 0.3
    
    peaks, _ = find_peaks(filtered, distance=min_distance, prominence=prominence)
    
    num_breaths = len(peaks)
    respiratory_rate = (num_breaths / window_duration) * 60
    
    if 6 <= respiratory_rate <= 40:
        return respiratory_rate
    
    return None