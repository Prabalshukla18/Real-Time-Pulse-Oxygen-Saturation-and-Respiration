# 🩺 Real-Time Pulse Oxygen Saturation & Respiration Monitoring

![IoT](https://img.shields.io/badge/Domain-IoT-blue)
![Python](https://img.shields.io/badge/Python-3.x-green)
![ESP32](https://img.shields.io/badge/Microcontroller-ESP32-orange)
![Status](https://img.shields.io/badge/Status-Completed-brightgreen)

---

## 📌 Project Overview

A **real-time health monitoring system** that measures:

* 🩸 **SpO₂ (Blood Oxygen Saturation)**
* ❤️ **Heart Rate**
* 🫁 **Respiratory Rate**

Built using **MAX30102 sensor + ESP32 + Python signal processing**, this project captures and analyzes **PPG (Photoplethysmography) signals** to generate meaningful health insights.

---

## 🚀 Key Features

* 📡 Real-time PPG data acquisition
* ❤️ Accurate heart rate detection via peak analysis
* 🫁 Respiratory rate extraction from signal patterns
* 🩸 SpO₂ calculation using ratio-of-ratios method
* 📊 Data visualization using Python
* ⚡ Low-cost, efficient IoT solution

---

## 🛠️ Tech Stack

**Hardware**

* ESP32
* MAX30102 Sensor

**Software**

* Python
* Arduino (Embedded C)

**Libraries & Tools**

* NumPy
* Pandas
* Matplotlib

---

## 🧠 System Workflow

```text
MAX30102 Sensor → ESP32 → Data Transmission → Python Processing → Visualization
```

1. Sensor captures IR & Red light signals
2. ESP32 reads and transmits raw PPG data
3. Python processes the signal:

   * Noise filtering
   * Peak detection
   * Feature extraction
4. Calculates:

   * Heart Rate
   * Respiratory Rate
   * SpO₂
5. Outputs visual insights

---

## 📂 Project Structure

```bash
├── Arduino_Code/        # ESP32 firmware
├── Python_Code/         # Signal processing logic
├── Data/                # Sample datasets
├── Results/             # Graphs & outputs
└── README.md
```

---

## 📈 Core Algorithms

* Peak detection for heart rate
* Moving average filtering
* Ratio-of-ratios for SpO₂
* Frequency-based respiration analysis

---

## 💡 Applications

* Remote patient monitoring
* Wearable health tech
* Fitness tracking
* Early respiratory issue detection

---

## ⚠️ Limitations

* Sensitive to motion noise
* Requires calibration for medical accuracy
* Not a replacement for clinical devices

---

---


