# Rhythm Experiment Application

A Python application for conducting rhythm perception and synchronization experiments. The application presents rhythmic patterns and records participant responses through tapping.

## Prerequisites

- Python 3.x
- MacOS environment
- BlackHole audio driver
- Properly configured audio devices (details in Audio Setup)
- Working headphones / airpods / earplugs

## Installation

### 1. Clone Repositories
```bash
# Clone main repository
git clone [your-repository-url]
cd [repository-name]

# Install REPP dependency
git clone https://gitlab.com/computational-audition/repp.git
cd repp
pip install -e .
cd ..
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Audio Setup

#### A. Install BlackHole
1. Download BlackHole 2ch from: https://existential.audio/blackhole/
2. Install the downloaded package
3. Restart your computer after installation

#### B. Configure Audio MIDI Setup
1. Open Audio MIDI Setup (Applications > Utilities > Audio MIDI Setup)
2. Create Multi-Output Device:
   - Click '+' button at bottom left
   - Choose "Create Multi-Output Device"
   - Name it "Experiment Output"
   - Check your headphones/speakers
   - Check "BlackHole 2ch" (follow this order)
   - Set sample rate to 48.0 kHz

3. Create Aggregate Device:
   - Click '+' button again
   - Choose "Create Aggregate Device"
   - Name it "Experiment Input"
   - Check your built-in microphone
   - Check "BlackHole 2ch" (follow this order)
   - Set sample rate to 48.0 kHz
   - Ensure Drift Correction is checked for BlackHole 2ch and for the built-in microphone

#### C. Configure System Audio
1. Open System Settings > Sound
2. Set Output device to "Experiment Output"
3. Set Input device to "Experiment Input"
4. Verify in your audio settings:
   - BlackHole 2ch (2 in, 2 out)
   - Experiment Input (3 in, 0 out)
   - Experiment Output (0 in, 2 out)

## Running the Experiment

1. Launch the application:
```bash
python main.py
```

2. Follow the GUI prompts:
   - Enter participant ID (9 digits)
   - Complete headphone orientation check
   - Practice rhythms
   - Complete experimental trials

## Experiment Structure

- Random assignment to conditions:
  - Complexity (simple/complex rhythms)
  - Ear presentation (left/right)
  - Sequence order
- Practice Phase:
  - 2 practice trials per rhythm (listening only)
- Testing Phase:
  - 12 experimental trials per rhythm
- Breaks:
  - 15 seconds after 6 trials
  - 120 seconds between rhythms

## Data Output

Results are saved in the `output` directory with the following structure:
```
output/
└── participant_id/
    ├── allocation.txt
    ├── participant_analysis.csv
    └── stimulus_X/
        └── trial_Y/
            ├── recording_trial_Y.wav
            ├── numerical_data_trial_Y.json
            └── plot_trial_Y.png
```

## Analysis

The experiment uses [REPP (Rhythm Evaluation from Performance and Perception)](https://gitlab.com/computational-audition/repp) for rhythm analysis. REPP provides:
- Onset detection in audio recordings
- Response alignment with stimuli
- Analysis of timing accuracy and precision
- Visualization of tapping patterns

## Dependencies

### Core Dependencies
- matplotlib>=3.3.1
- click>=7.1.2
- scipy>=1.5.3
- jupyter>=1.0.0
- sounddevice>=0.4.1
- numpy>=1.20.2
- pandas>=1.3.0
- tk>=8.6
- repp>=0.6.0 (from GitLab repository)

### Development Dependencies
- pytest>=6.1.2
- pytest-benchmark>=3.2.3

## Troubleshooting

1. Audio Device Issues:
   - Ensure BlackHole is properly installed
   - Verify sample rates match (48.0 kHz) across all devices
   - Check that both "Experiment Input" and "Experiment Output" are properly configured
   - Make sure BlackHole 2ch is selected in both aggregate devices

2. Recording Issues:
   - Check microphone permissions in System Settings
   - Verify input levels are appropriate
   - Ensure correct devices are selected in System Sound settings

## Authors

Natalie Eliav & Adi Adar

## Acknowledgments

This project utilizes [REPP](https://gitlab.com/computational-audition/repp), developed by the Computational Audition lab.

