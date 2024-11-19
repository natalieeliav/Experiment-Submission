# Experiment_to_submit

## Rhythm Experiment Application
A Python application for conducting rhythm perception and synchronization experiments. The application presents rhythmic patterns and records participant responses through tapping.
Prerequisites

Python 3.x
BlackHole audio driver
Two configured audio devices named:

"experiment input"
"experiment output"

# Installation

Clone the repository:

bashCopygit clone [your-repository-url]

Install REPP dependency:

bashCopygit clone https://gitlab.com/computational-audition/repp.git
cd repp
pip install -e .
cd ..

Install other dependencies:

bashCopypip install -r requirements.txt

# Audio Setup

Install BlackHole audio driver
Configure two audio devices:

Name one device "experiment input" for recording
Name another "experiment output" for playback

# Running the Experiment

Launch the application:

bashCopypython main.py

Follow the GUI prompts to:

Enter participant ID (9 digits)
Complete headphone orientation check
Practice rhythms
Complete experimental trials

# Experiment Structure

Random assignment to conditions:

Complexity (simple/complex rhythms)
Ear presentation (left/right)
Sequence order


2 practice trials per rhythm (listening only)
12 experimental trials per rhythm
Breaks:

15 seconds after 6 trials
120 seconds between rhythms



Data Output
Results are saved in the output directory with the following structure:
Copyoutput/
└── participant_id/
    ├── allocation.txt
    ├── participant_analysis.csv
    └── stimulus_X/
        └── trial_Y/
            ├── recording_trial_Y.wav
            ├── numerical_data_trial_Y.json
            └── plot_trial_Y.png
Analysis
The experiment uses REPP (Rhythm Evaluation from Performance and Perception) for rhythm analysis. REPP provides:

Onset detection in audio recordings
Response alignment with stimuli
Analysis of timing accuracy and precision
Visualization of tapping patterns
