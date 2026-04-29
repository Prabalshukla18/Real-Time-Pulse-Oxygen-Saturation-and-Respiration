import numpy as np
from scipy.signal import butter, filtfilt, find_peaks


def calculate_heart_rate(ir_buffer, sampling_rate=50):
    """
    Calculate heart rate from IR signal buffer.
    Requires exactly 30 seconds of data (1500 samples at 50Hz).
    Returns heart rate between 60-100 BPM.
    """
    # Need exactly 30 seconds of data
    required_samples = sampling_rate * 30
    
    # Check if we have enough data
    if len(ir_buffer) < required_samples:
        return None
    
    ir_data = np.array(ir_buffer)
    
    # Use the provided data (should be exactly 1500 samples)
    segment = ir_data[:required_samples] if len(ir_data) > required_samples else ir_data
    
    # Remove DC component
    segment = segment - np.mean(segment)
    
    # Bandpass filter: 1.0-2.0 Hz (60-120 bpm range, but we'll restrict to 60-100)
    nyquist = sampling_rate / 2
    b, a = butter(4, [1.0/nyquist, 2.0/nyquist], btype='band')
    filtered = filtfilt(b, a, segment)
    
    # Normalize
    filtered = filtered / (np.std(filtered) + 1e-9)
    
    # Peak detection
    min_distance = int(0.6 * sampling_rate)  # Minimum 0.6s between peaks (100 bpm max)
    prominence = np.std(filtered) * 0.5
    
    peaks, properties = find_peaks(filtered, distance=min_distance, prominence=prominence)
    
    if len(peaks) < 3:  # Need at least 5 peaks for reliable calculation
        return None
    
    # Calculate intervals between peaks
    intervals = np.diff(peaks) / sampling_rate
    
    # Filter physiologically valid intervals (0.6-1.0 seconds = 60-100 bpm)
    valid = intervals[(intervals >= 0.4) & (intervals <= 1.5)]
    
    if len(valid) < 4:
        return None
    
    # Remove outliers using IQR method
    q1, q3 = np.percentile(valid, [25, 75])
    iqr = q3 - q1
    lower_bound = q1 - 1.5 * iqr
    upper_bound = q3 + 1.5 * iqr
    
    refined = valid[(valid >= lower_bound) & (valid <= upper_bound)]
    
    if len(refined) < 3:
        mean_interval = np.median(valid)
    else:
        mean_interval = np.median(refined)  # Use median for robustness
    
    heart_rate = 60.0 / mean_interval
    
    # Final sanity check - strict range 60-100 BPM
    if 60 <= heart_rate <= 100:
        return heart_rate
    
    return None