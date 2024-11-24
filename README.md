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
git clone https://github.com/natalieeliav/Experiment-Submission.git
cd Experiment-Submission

# Clone REPP in the project directory
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

## Running the Experiment

1. Launch the application:
```bash
python PythonGui-Experiment.py
```

2. Follow the GUI prompts:
   - Enter participant ID (9 digits)
   - Complete headphone orientation check
   - Practice rhythms
   - Complete experimental trials

## Experiment Design

### Random Assignment
Participants are randomly assigned to:
1. **Complexity Level** (maintained throughout experiment)
   - Simple rhythms
   - Complex rhythms

2. **Initial Parameters**
   - First ear presentation (left/right)
   - Sequence order (1st/2nd)

### Experimental Flow

#### For Each Sequence:

1. **Practice Phase**
   - 2 practice trials (listening only, in both ears)
   
2. **First Testing Block**
   - 6 trials with assigned ear
   - 15 seconds break
   
3. **Second Testing Block**
   - 6 additional trials with the assigned ear

**Important Notes:**

- Both sequences are from the same complexity level (simple or complex)
- Each sequence is presented to only one ear
- The ear presentation switches between sequences
- There is a 120 seconds break between the two sequences
- The code uses REPP framework for stimulus generation and analysis

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

- matplotlib>=3.3.1
- click>=7.1.2
- scipy>=1.5.3
- jupyter>=1.0.0
- sounddevice>=0.4.1
- numpy>=1.20.2
- pandas>=1.3.0
- repp>=0.6.0 (from GitLab repository)

## Run Example

This repository includes a `run-example` directory that contains an example run of an experiment submission process, including stimulus trials and participant analysis.

### Project Structure of run-example
- `OUTPUT/`: Directory containing output files
  - `Stimulus 1 Trial 1/`: Directory for first stimulus trial 1
  - `Stimulus 2 Trial 1/`: Directory for second stimulus trial 1
  - `README.md`: More information about the output
  - `allocation.txt`: Contains participant allocation information
  - `participant_analysis.csv`: Contains analysis results for the participant
- `Experiment Screen Recording`: [View the experiment screen recording](https://drive.google.com/file/d/1JkSBiQr7USAOlaPEKG1UtsnkLb9W3r7i/view?usp=sharing)
   * Contains a video of the experiment flow, presenting 12 trials of the first sequence, the 2-minute break, and the first trial of the second sequence. (The other trials follow the same pattern)

### Output Example Directory
Due to storage constraints, this repository includes a simplified example showing only two trials.
The real structure is as described above.

### File Descriptions in run-example
- `allocation.txt`: Contains participant allocation information
- `participant_analysis.csv`: Contains analysis results for the participant
- `recording_trial_Y.wav`: Audio recording from each trial (stimulus + tapping)
- `numerical_data_trial_Y.json`: Raw numerical data from each trial
- `plot_trial_Y.png`: Visualization of trial data

Note: 'Y' in file names represents the trial number.

## Troubleshooting

1. Audio Device Issues:
   - Ensure BlackHole is properly installed
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

