## Output Example Directory
Due to storage constraints, this repository includes a simplified example showing only two trials.
In the actual experiment, results are saved in the `output` directory with the following structure:
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

## File Descriptions

- `allocation.txt`: Contains participant allocation information
- `participant_analysis.csv`: Contains analysis results for the participant
- `recording_trial_Y.wav`: Audio recording from each trial (stimulus + tapping)
- `numerical_data_trial_Y.json`: Raw numerical data from each trial
- `plot_trial_Y.png`: Visualization of trial data
