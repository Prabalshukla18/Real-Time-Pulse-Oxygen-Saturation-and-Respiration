import streamlit as st
import serial
import time
from collections import deque
import pandas as pd
import threading

from heart_rate import calculate_heart_rate
from respiratory_rate import calculate_respiratory_rate
from spo2 import calculate_spo2


class PPGMonitor:
    
    def __init__(self, port, baudrate=115200):
        self.port = port
        self.baudrate = baudrate
        self.ser = None
        
        # Buffer for 30 seconds at 50Hz = 1500 samples
        self.ir_buffer = deque(maxlen=1500)
        self.red_buffer = deque(maxlen=1500)
        
        self.hr_value = None
        self.rr_value = None
        self.spo2_value = None
        
        self.running = False
        self.thread = None
        
        # Track samples for calculation timing
        self.sample_count = 0
        self.last_calc_time = 0
    
    
    def connect(self):
        try:
            if self.ser:
                self.ser.close()
            self.ser = serial.Serial(self.port, self.baudrate, timeout=1)
            time.sleep(2)
            return True
        except Exception as e:
            return False
    
    
    def disconnect(self):
        self.running = False
        if self.thread:
            self.thread.join(timeout=2)
        if self.ser:
            self.ser.close()
    
    
    def read_data(self):
        """Read data from serial port and buffer it."""
        while self.running:
            try:
                line = self.ser.readline().decode('utf-8', errors='ignore').strip()
                
                if line and ',' in line:
                    ir, red = line.split(',')
                    ir_value = int(ir)
                    red_value = int(red)
                    
                    if 50000 < ir_value < 200000 and 50000 < red_value < 200000:
                        self.ir_buffer.append(ir_value)
                        self.red_buffer.append(red_value)
                        self.sample_count += 1
                        
                        # Calculate every 30 seconds (1500 samples)
                        # At 30s, 60s, 90s, 120s, etc.
                        if self.sample_count % 1500 == 0:
                            self.calculate_vitals()
                            self.last_calc_time = self.sample_count
            except:
                pass
    
    
    def calculate_vitals(self):
        """Calculate all vital signs from the current 30-second buffer."""
        
        # Convert deque to list
        ir_window = list(self.ir_buffer)
        red_window = list(self.red_buffer)
        
        print(f"\n=== Calculation at {self.sample_count} samples ({self.sample_count/50:.1f}s) ===")
        print(f"IR window length: {len(ir_window)}, Red window length: {len(red_window)}")
        
        # Need exactly 1500 samples for calculations
        if len(ir_window) != 1500 or len(red_window) != 1500:
            print(f"ERROR: Window length is {len(ir_window)}, expected 1500")
            return
        
        # Calculate vitals using the full 30-second buffer
        hr = calculate_heart_rate(ir_window, 50)
        print(f"HR result: {hr}")
        
        rr = calculate_respiratory_rate(ir_window, 50, 30)
        print(f"RR result: {rr}")
        
        spo2 = calculate_spo2(ir_window, red_window, 50)
        print(f"SpO2 result: {spo2}")
        
        # Update values - only update if we got a valid result
        # Keep previous value if None is returned
        if hr is not None:
            self.hr_value = hr
            
        if rr is not None:
            self.rr_value = rr
            
        if spo2 is not None:
            self.spo2_value = spo2
        
        print(f"Updated values - HR: {self.hr_value}, RR: {self.rr_value}, SpO2: {self.spo2_value}")
    
    
    def start_monitoring(self):
        self.running = True
        self.sample_count = 0
        self.last_calc_time = 0
        self.thread = threading.Thread(target=self.read_data, daemon=True)
        self.thread.start()
    
    
    def get_buffer_status(self):
        return len(self.ir_buffer), 1500
    
    
    def get_time_to_next_calc(self):
        """Get seconds until next calculation."""
        samples_since_last = self.sample_count - self.last_calc_time
        samples_to_next = 1500 - samples_since_last
        return samples_to_next / 50.0
    
    
    def get_chart_data(self):
        if len(self.ir_buffer) > 0:
            return pd.DataFrame({'IR': list(self.ir_buffer)[-500:]})
        return pd.DataFrame({'IR': []})
    
    
    def get_vitals(self):
        return self.hr_value, self.rr_value, self.spo2_value


# Streamlit UI
st.set_page_config(page_title="PPG Monitor", layout="wide")

if 'monitor' not in st.session_state:
    st.session_state.monitor = None

st.title("🩺 PPG Vital Signs Monitor")
st.caption("Vitals calculated every 30 seconds")

PORT = st.sidebar.text_input("COM Port", "COM5")
BAUDRATE = st.sidebar.number_input("Baud Rate", value=115200)

col1, col2 = st.sidebar.columns(2)

if col1.button("Connect"):
    if st.session_state.monitor:
        st.session_state.monitor.disconnect()
    
    st.session_state.monitor = PPGMonitor(PORT, BAUDRATE)
    
    if st.session_state.monitor.connect():
        st.session_state.monitor.start_monitoring()
        st.sidebar.success("✓ Connected")
    else:
        st.sidebar.error("✗ Connection failed")
        st.session_state.monitor = None

if col2.button("Stop"):
    if st.session_state.monitor:
        st.session_state.monitor.disconnect()
        st.session_state.monitor = None
    st.sidebar.info("Stopped")

st.sidebar.divider()

# Create a single placeholder for status info
if 'status_placeholder' not in st.session_state:
    st.session_state.status_placeholder = st.sidebar.empty()

# Show window info only once using the placeholder
if st.session_state.monitor and st.session_state.monitor.running:
    calc_number = (st.session_state.monitor.sample_count // 1500) + 1
    st.session_state.status_placeholder.info(f"📊 **Status:**\nCalculation #{calc_number} at {calc_number * 30}s")
else:
    st.session_state.status_placeholder.info("⏱️ **Calculation Schedule:**\nEvery 30 seconds\n(30s, 60s, 90s, ...)")

chart_placeholder = st.empty()
progress_placeholder = st.empty()
timer_placeholder = st.empty()

col1, col2, col3 = st.columns(3)
metric_hr = col1.empty()
metric_rr = col2.empty()
metric_spo2 = col3.empty()

if st.session_state.monitor and st.session_state.monitor.running:
    
    current, total = st.session_state.monitor.get_buffer_status()
    progress = current / total
    progress_placeholder.progress(progress, text=f"Buffer: {current}/{total} samples ({current/50:.1f}s)")
    
    # Show countdown to next calculation
    time_remaining = st.session_state.monitor.get_time_to_next_calc()
    
    if time_remaining > 29:
        timer_placeholder.warning(f"⏳ Collecting initial data... {time_remaining:.0f}s remaining")
    else:
        timer_placeholder.info(f"⏱️ Next calculation in: {time_remaining:.0f}s")
    
    chart_data = st.session_state.monitor.get_chart_data()
    if not chart_data.empty:
        chart_placeholder.line_chart(chart_data, height=250)
    
    hr, rr, spo2 = st.session_state.monitor.get_vitals()
    
    # Show actual values or indicate if calculation failed vs waiting for first calculation
    if st.session_state.monitor.sample_count < 1500:
        # Still collecting data for first calculation
        metric_hr.metric("❤️ Heart Rate", "Calculating")
        metric_rr.metric("🫁 Respiratory Rate", "Calculating")
        metric_spo2.metric("💉 SpO2", "Calulating")
    else:
        # After first calculation attempt
        metric_hr.metric("❤️ Heart Rate", f"{hr:.1f} bpm" if hr is not None else "No valid signal")
        metric_rr.metric("🫁 Respiratory Rate", f"{rr:.1f} /min" if rr is not None else "No valid signal")
        metric_spo2.metric("💉 SpO2", f"{spo2:.1f}%" if spo2 is not None else "No valid signal")
    
    time.sleep(0.5)
    st.rerun()

else:
    chart_placeholder.info("👈 Click 'Connect' to start monitoring")
    progress_placeholder.progress(0)
    timer_placeholder.empty()
    metric_hr.metric("❤️ Heart Rate", "--")
    metric_rr.metric("🫁 Respiratory Rate", "--")
    metric_spo2.metric("💉 SpO2", "--")