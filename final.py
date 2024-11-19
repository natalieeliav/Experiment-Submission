"""
Rhythm Experiment Application

Technical Requirements:
    - Python 3.x
    - Required packages: sounddevice, matplotlib, numpy, scipy, pandas, tkinter, repp
    - BlackHole audio driver
    - Two configured audio devices: "experiment input" and "experiment output"

Authors: Natalie Eliav & Adi Adar
"""

import os
import sounddevice as sd
import matplotlib as mpl
import matplotlib.pyplot as plt
import json
import tkinter as tk
from tkinter import ttk, messagebox
import threading
import numpy as np
import scipy.signal
import random
import pandas as pd
import glob

from repp.repp.config import sms_tapping
from repp.repp.stimulus import REPPStimulus
from repp.repp.analysis import REPPAnalysis


def create_participant_analysis_csv(output, analysis_result, is_failed, trial_num, output_dir, stimulus_num,
                                    allocation):
    """
    Create or update a CSV file with analysis metrics for all trials of a participant.

    Parameters:
        output (dict): The output data from REPP analysis containing timing and response information
        analysis_result (dict): The analysis results from REPP analysis containing computed metrics
        is_failed (dict): Information about whether the trial failed and why
        trial_num (int): Current trial number
        output_dir (str): Directory path for participant output
        stimulus_num (int): Current stimulus number (1 or 2)
        allocation (str): Participant's experimental allocation

    Returns:
        dict: Dictionary containing all computed metrics for the trial

    Output Structure:
        The CSV file contains columns for:
        - Trial information (number, stimulus, allocation)
        - Response metrics (total responses, aligned responses)
        - Timing metrics (mean asynchrony, standard deviation)
        - Performance metrics (IOI measurements, marker detection)
    """
    # Calculate metrics from the output data
    metrics = {
        'trial_number': trial_num,
        'stimulus_number': stimulus_num,
        'allocation': allocation,
        'trial_failed': is_failed['failed'],
        'failure_reason': is_failed['reason'],

        # Stimulus metrics
        'total_stimuli': len(output['stim_onsets_input']),
        'detected_stimuli': len([x for x in output['stim_onsets_aligned'] if not np.isnan(x)]),

        # Response metrics
        'total_responses': len(output['resp_onsets_detected']),
        'aligned_responses': len([x for x in output['resp_onsets_aligned'] if not np.isnan(x)]),

        # Timing metrics
        'mean_asynchrony': analysis_result['mean_async_all'],
        'sd_asynchrony': analysis_result['sd_async_all'],
        'percent_responses': analysis_result['ratio_resp_to_stim'],
        'percent_responses_aligned': analysis_result['percent_resp_aligned_all'],

        # IOI metrics
        'mean_stimulus_ioi': np.nanmean([x for x in output['stim_ioi'] if not np.isnan(x)]),
        'mean_response_ioi': np.nanmean([x for x in output['resp_ioi'] if not np.isnan(x)]),

        # Marker metrics
        'num_markers': analysis_result['num_markers_onsets'],
        'detected_markers': analysis_result['num_markers_detected'],
        'marker_detection_rate': analysis_result['markers_status'],
        'max_marker_error': analysis_result['markers_max_difference'],

        # Performance metrics
        'percent_bad_taps': analysis_result['percent_of_bad_taps_all'],

        # Additional metrics for played vs not played onsets
        'mean_async_played': analysis_result['mean_async_played'],
        'sd_async_played': analysis_result['sd_async_played'],
        'percent_resp_played': analysis_result['percent_response_aligned_played'],
        'mean_async_notplayed': analysis_result['mean_async_notplayed'],
        'sd_async_notplayed': analysis_result['sd_async_notplayed'],
        'percent_resp_notplayed': analysis_result['percent_response_aligned_notplayed']
    }

    csv_path = os.path.join(output_dir, 'participant_analysis.csv')

    # If file exists, read it and append new data
    if os.path.exists(csv_path):
        df_existing = pd.read_csv(csv_path)
        df_new = pd.DataFrame([metrics])
        df_combined = pd.concat([df_existing, df_new], ignore_index=True)
    else:
        df_combined = pd.DataFrame([metrics])

    # Sort by stimulus number and trial number
    df_combined = df_combined.sort_values(['stimulus_number', 'trial_number'])

    # Save to CSV
    df_combined.to_csv(csv_path, index=False)

    return metrics


class RhythmExperimentGUI:
    """
    Main class for the rhythm experiment GUI application.
    
    This class handles the complete experimental flow including:
    - Participant registration
    - Audio device setup
    - Stimulus presentation
    - Response recording
    - Data analysis and storage
    
    Experiment Structure:
    1. Random assignment to conditions (complexity, ear, sequence)
    2. Practice phase (2 listening trials)
    3. Testing phase (12 trials per rhythm)
    4. Breaks (15s after 6 trials, 120s between rhythms)
    """

    def __init__(self, master):
        """
        Initialize the experiment GUI and setup configurations.

        Parameters:
            master: tkinter root window
        """
        self.master = master
        master.title("Rhythm Experiment")
        master.geometry("500x400")

        # Initialize variables
        self.participant_id = tk.StringVar()
        self.current_step = 0
        self.ear = None
        self.current_stimulus = 1
        self.playback_count = 0
        self.current_trial = 0

        # Setup experiment configuration (which now includes audio setup)
        try:
            self.setup_experiment()
            # Then setup GUI
            self.setup_gui()
        except RuntimeError as e:
            messagebox.showerror("Setup Error", str(e))
            self.master.destroy()

    def setup_experiment(self):
        """
        Setup experiment configuration and parameters.
        
        Initializes:
        - Rhythm patterns (simple and complex)
        - Random condition assignments
        - Audio device configuration
        
        Raises:
            RuntimeError: If audio device setup fails
        """
        self.config = sms_tapping

        # Define rhythms
        self.simple_rhythms = [
            [0, 520, 520, 520, 260, 260, 520, 520],  # Simple rhythm pattern 1
            [0, 520, 260, 260, 520, 260, 260, 520, 520]  # Simple rhythm pattern 2
        ]
        self.complex_rhythms = [
            [0, 130, 260, 390, 260, 130, 260, 390, 260],  # Complex rhythm pattern 1
            [0, 390, 130, 260, 520, 260, 130, 390]  # Complex rhythm pattern 2
        ]

        # Random assignments
        self.complexity = random.choice(['complex', 'simple'])
        self.ear = random.choice(['right', 'left'])
        self.sequence_order = random.choice([0, 1])

        # Set rhythms based on complexity
        self.rhythms = self.simple_rhythms if self.complexity == 'simple' else self.complex_rhythms

        # Setup audio devices
        if not self.setup_audio_devices():
            raise RuntimeError("Audio device setup failed")

    def setup_audio_devices(self):
        """
        Set up and configure audio devices for the experiment.
        
        Requirements:
        - BlackHole virtual audio device
        - Input device named "experiment input"
        - Output device named "experiment output"
        
        Returns:
            bool: True if setup successful, False otherwise
        
        Side Effects:
            Sets up the following attributes:
            - blackhole_device
            - mic_device
            - output_device
        """
        try:
            devices = sd.query_devices()

            # Initialize all device variables
            self.blackhole_device = None
            self.mic_device = None
            self.output_device = None

            print("\nAvailable audio devices:")
            for i, device in enumerate(devices):
                print(
                    f"{i}: {device['name']} (inputs: {device['max_input_channels']}, outputs: {device['max_output_channels']})")

                # Find BlackHole
                if 'blackhole' in device['name'].lower():
                    self.blackhole_device = i

                # find input device
                elif device['max_input_channels'] > 0 and 'experiment input' in device['name'].lower():
                    self.mic_device = i

                # Find output device
                elif (device['max_output_channels'] > 0 and
                      'experiment output' in device['name'].lower()):
                    self.output_device = i

            if self.blackhole_device is None:
                messagebox.showerror("Audio Setup Error",
                                     "BlackHole device not found. Please install and enable BlackHole.")
                return False

            if self.mic_device is None:
                messagebox.showerror("Audio Setup Error",
                                     "Built-in microphone not found. Please check your audio settings.")
                return False

            if self.output_device is None:
                messagebox.showerror("Audio Setup Error",
                                     "Output device not found. Please check your audio settings.")
                return False

            # Store original settings
            self.original_device = sd.default.device
            self.original_channels = sd.default.channels

            # Initial setup for ear check (using built-in mic)
            sd.default.device = (self.mic_device, self.output_device)
            sd.default.channels = (1, 2)  # Mono input, stereo output

            print(f"\nInitial audio setup complete:")
            print(f"BlackHole device: {self.blackhole_device}")
            print(f"Microphone device: {self.mic_device}")
            print(f"Output device: {self.output_device}")
            print(f"Current settings: {sd.default.device}, Channels: {sd.default.channels}")

            return True

        except Exception as e:
            messagebox.showerror("Audio Setup Error",
                                 f"Error setting up audio devices: {str(e)}\nPlease check your audio settings.")
            return False

    def setup_gui(self):
        """
        Set up the graphical user interface components.
        """
        self.frame = ttk.Frame(self.master, padding="10")
        self.frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        welcome_text = """
        This experiment investigates rhythm perception and synchronization abilities.

        Your participation will take approximately 15 minutes. You will hear rhythmic patterns through headphones and tap along with them.

        Your data will be saved anonymously using a participant ID. You may stop participating at any time by closing this window.

        By clicking 'Start', you agree to participate in this experiment.

        Thank you for your time

        Adi and Natalie"""

        self.label = ttk.Label(self.frame, text=welcome_text, wraplength=400)
        self.label.grid(row=0, column=0, pady=10)

        self.entry = ttk.Entry(self.frame, textvariable=self.participant_id)
        self.entry.grid(row=1, column=0, pady=5)
        self.entry.grid_remove()

        self.next_button = ttk.Button(self.frame, text="Start", command=self.start_experiment)
        self.next_button.grid(row=3, column=0, pady=10)

    def start_experiment(self):
        """
        Initial step to start the experiment.
        """
        self.label.config(text="Please enter your participant ID (9 digits):")
        self.entry.grid()  # Show the entry box
        self.next_button.config(text="Submit", command=self.validate_participant_id)

    def validate_participant_id(self):
        """
        Validate the participant ID and create output directory structure.
        
        Checks:
        - ID is 9 digits
        - Creates output directory structure
        - Saves allocation information
        """
        pid = self.participant_id.get()
        if not (pid.isdigit() and len(pid) == 9):
            messagebox.showerror("Error", "Please enter a valid 9-digit ID")
            return

        # Create output directory
        self.output_dir = os.path.join('output', self.participant_id.get())
        os.makedirs(self.output_dir, exist_ok=True)

        # Save allocation
        allocation = f"{self.complexity}-stimulus{self.sequence_order + 1}-{self.ear}ear"
        with open(os.path.join(self.output_dir, 'allocation.txt'), 'w') as f:
            f.write(allocation)

        self.entry.grid_remove()  # Remove the entry box
        self.show_initial_instructions()

    def show_initial_instructions(self):
        """
        Display initial experiment instructions to the participant.
        """
        instructions = """In this experiment, you will hear and tap along with 2 different rhythms.

    1. First, each rhythm will be played twice for practice - just listen, no tapping needed.
    2. Then, you will tap along with each rhythm for multiple trials.
    3. Use your right hand index finger to tap in sync with the beats.
    4. The rhythms will be played through one ear at a time.
    5. Each rhythm starts and ends with 3 marker beats - you don't need to tap these."""

        self.label.config(text=instructions)
        self.next_button.config(text="Next", command=self.show_tapping_instructions)

    def show_tapping_instructions(self):
        """
        Display specific tapping instructions to the participant.
        """
        instructions = """Important tapping instructions:

    1. Use ONLY your right hand's index finger
    2. Tap on the laptop surface next to the touchpad
    3. Tap gently but firmly with your fingertip
    4. DO NOT tap on:
    - Keys
    - Mouse buttons
    - Touchpad"""

        self.label.config(text=instructions)
        self.next_button.config(command=self.start_headphone_check)

    def start_headphone_check(self):
        """
        Begin the headphone orientation check procedure.
        """
        self.label.config(text="""Right Earbud Check:

    At first, please make sure to insert your earbuds properly.
    1. You will hear a single beat
    2. Tap once when you hear it
    3. The sound should come from your RIGHT ear
    4. If you hear it in your LEFT ear, please switch your earbuds""")
        self.next_button.config(text="Start Check", command=self.check_right_ear)

    def check_right_ear(self):
        """
        Perform right ear audio check.
        """
        self.next_button.grid_remove()
        self.perform_ear_check('right')

    def check_left_ear(self):
        """
        Setup for left ear audio check.
        """
        self.label.config(text="Left Earbud Check\n"
                               "You will hear a beat. Please tap when you hear it.\n")
        self.next_button.config(text="Start Check", command=self.perform_left_check)
        self.next_button.grid()

    def perform_left_check(self):
        """
        Execute left ear check procedure.
        """
        self.next_button.grid_remove()
        self.perform_ear_check('left')

    def perform_ear_check(self, ear):
        """
        Perform audio check for specified ear.
        
        Parameters:
            ear (str): Which ear to check ('left' or 'right')
            
        Process:
        1. Generates test sound
        2. Plays sound in specified ear
        3. Records and analyzes response
        4. Proceeds to next step or retries based on detection
        """
        try:
            # Verify we have the device information
            if not hasattr(self, 'mic_device') or not hasattr(self, 'output_device'):
                messagebox.showerror("Setup Error", "Audio devices not properly initialized")
                return

            duration = 1.5
            fs = 44100
            t = np.linspace(0, duration, int(fs * duration))
            test_sound = np.sin(2 * np.pi * 440 * t)

            silence = np.zeros(int(0.75 * fs))
            full_audio = np.concatenate((silence, test_sound, silence))

            if ear == 'left':
                stereo_audio = np.vstack((full_audio, np.zeros_like(full_audio)))
            else:  # right ear
                stereo_audio = np.vstack((np.zeros_like(full_audio), full_audio))

            recording = sd.playrec(stereo_audio.T, fs, channels=1)
            sd.wait()

            tap_detected = self.detect_tap(recording.flatten(), fs)

            if tap_detected:
                if ear == 'right':
                    self.check_left_ear()
                else:
                    self.start_rhythm_practice()
            else:
                self.label.config(text=f"No tap detected for {ear} ear. Please try again with a firmer tap.")
                if ear == 'right':
                    self.next_button.config(text="Retry Right Check", command=self.check_right_ear)
                else:
                    self.next_button.config(text="Retry Left Check", command=self.perform_left_check)
                self.next_button.grid()

        except Exception as e:
            messagebox.showerror("Audio Error", f"Error during ear check: {str(e)}")
            self.next_button.config(text="Retry", command=lambda: self.perform_ear_check(ear))
            self.next_button.grid()

    def detect_tap(self, audio, fs):
        """
        Analyze audio recording to detect tapping events.
        
        Parameters:
            audio (numpy.ndarray): Raw audio data
            fs (int): Sampling frequency
            
        Returns:
            bool: True if tap detected, False otherwise
        """
        # High-pass filter to remove low frequency noise
        nyq = 0.5 * fs
        high = 30 / nyq
        b, a = scipy.signal.butter(4, high, btype='high')
        filtered_audio = scipy.signal.filtfilt(b, a, audio)
        analytic_signal = scipy.signal.hilbert(filtered_audio)
        envelope = np.abs(analytic_signal)
        window_size = int(0.05 * fs)
        envelope_smooth = np.convolve(envelope, np.ones(window_size) / window_size, mode='same')

        # Find peaks
        peaks, _ = scipy.signal.find_peaks(envelope_smooth,
                                           height=0.01,
                                           distance=int(0.05 * fs))

        # Wider time window for valid peaks
        beat_time = 0.5
        valid_peaks = peaks[(peaks > int((beat_time - 0.5) * fs)) &
                            (peaks < int((beat_time + 2.5) * fs))]  

        return len(valid_peaks) > 0

    def start_rhythm_practice(self):
        """
        Initialize rhythm practice phase.
        
        Process:
        1. Configure audio devices for practice
        2. Set up rhythm based on current stimulus
        3. Prepare REPP stimulus
        4. Display practice instructions
        """
        if self.current_stimulus != 1:
            self.ear = 'left' if self.ear == 'right' else 'right'
        rhythm = self.rhythms[self.sequence_order if self.current_stimulus == 1 else 1 - self.sequence_order]

        practice_text = f"""You will now hear Rhythm {self.current_stimulus} of 2.

        1. The rhythm will play twice for practice
        2. Just LISTEN during practice - do not tap yet
        3. Notice the 3 marker beats at the start and end
        4. After practice is finished, you'll tap along this rhythm for 12 trials

        Press 'Start Practice' when ready."""

        self.label.config(text=practice_text)
        self.current_repp_stimulus = REPPStimulus(f"rhythm_{self.current_stimulus}", config=self.config)
        stim_onsets = self.current_repp_stimulus.make_onsets_from_ioi(rhythm)
        self.stim_prepared, self.stim_info, _ = self.current_repp_stimulus.prepare_stim_from_onsets(stim_onsets)

        self.next_button.config(text="Start Practice", command=self.play_practice)
        self.next_button.grid()

    def play_practice(self):
        """
        Execute 2 practice trials for the current rhythm.
        """
        self.next_button.grid_remove()

        def play_twice():
            for i in range(2):
                self.label.config(text=f"""Playing practice for the  {i + 1}/2 time.
                    Just LISTEN during practice - do not tap yet
                    Notice the 3 marker beats at the start and end""")
                sd.play(self.stim_prepared, self.config.FS)
                sd.wait()
                if i == 0:
                    self.master.after(1000)  # 1 second delay between plays

            self.master.after(1000, self.start_trials)

        threading.Thread(target=play_twice).start()

    def start_trials(self):
        """
        Initialize the experimental trials phase.
        """
        self.current_trial = 0
        # Initial setup for ear check (using built-in mic)
        sd.default.device = (self.mic_device, self.output_device)

        self.label.config(text=f"""Ready to start Rhythm {self.current_stimulus} trials.

        1. Tap along as accurately as possible with EACH beat
        2. The rhythm will be played only in your {self.ear.upper()} ear
        3. Remember to ignore the 3 marker beats at start/end
        4. Please remember to tap with your right index finger
        5. This is trial 1 of 12

        Press 'Start Recording' when ready.""")

        self.next_button.config(text="Start Recording", command=self.run_trial)
        self.next_button.grid()

    def run_trial(self):
        """
        Execute a single experimental trial.
        
        Process:
        1. Configure audio channels
        2. Create trial directory
        3. Present stimulus and record response
        4. Save recordings and analyze data
        5. Progress to next trial or break
        
        Technical details:
        - Records 3 channels of audio
        - Saves combined recording
        - Performs REPP analysis
        """
        self.next_button.grid_remove()
        sd.default.channels = (3, 2)  # Mono input, stereo output

        if self.current_trial < 12:
            self.label.config(text=f"""Recording trial {self.current_trial + 2}/12

            1. Tap along as accurately as possible with EACH beat
            2. Remember to ignore the 3 marker beats at start/end
            3. remember to tap with your right index finger

            you will have a 15 sec break after the 6th trial""")

            try:
                # Create directory for this trial
                trial_dir = os.path.join(self.output_dir, f'stimulus_{self.current_stimulus}',
                                         f'trial_{self.current_trial + 1}')
                os.makedirs(trial_dir, exist_ok=True)

                # Create ear-specific stereo audio
                stereo_stim = np.zeros((len(self.stim_prepared), 2))

                # Put the stimulus in the correct ear
                if self.ear == 'right':
                    stereo_stim[:, 1] = self.stim_prepared.flatten()
                else:
                    stereo_stim[:, 0] = self.stim_prepared.flatten()

                # Record response
                recording = sd.playrec(stereo_stim, self.config.FS, channels=3)
                sd.wait()

                # Process recordings
                mic_rec = recording[:, 0]  # First channel (microphone)
                loopback_rec = recording[:, 1] if (self.ear=='left') else recording[:, 2]

                def safe_normalize(signal):
                    max_val = np.max(np.abs(signal))
                    if max_val > 0:
                        return signal / max_val
                    return signal

                # Normalize and combine recordings
                mic_signal = safe_normalize(mic_rec)
                loopback_signal = safe_normalize(loopback_rec)
                combined_recording = safe_normalize(mic_signal + loopback_signal)

                # Save combined recording
                combined_path = os.path.join(trial_dir, f'recording_trial_{self.current_trial + 1}.wav')
                REPPStimulus.to_wav(combined_recording.reshape(-1, 1), combined_path, self.config.FS)

                # Perform REPP analysis
                try:
                    # Initialize and run analysis
                    analysis = REPPAnalysis(config=self.config)
                    output, analysis_result, is_failed = analysis.do_analysis(
                        self.stim_info,
                        combined_path,
                        f"trial_{self.current_trial + 1}",
                        os.path.join(trial_dir, f'plot_trial_{self.current_trial + 1}.png')
                    )

                    # Save analysis results
                    with open(os.path.join(trial_dir, f'numerical_data_trial_{self.current_trial + 1}.json'), 'w') as f:
                        json.dump(output, f)

                    # Get allocation information
                    with open(os.path.join(self.output_dir, 'allocation.txt'), 'r') as f:
                        allocation = f.read().strip()

                    # Create/update analysis CSV
                    create_participant_analysis_csv(
                        output=output,
                        analysis_result=analysis_result,
                        is_failed=is_failed,
                        trial_num=self.current_trial + 1,
                        output_dir=self.output_dir,
                        stimulus_num=self.current_stimulus,
                        allocation=allocation
                    )

                    # Progress to next trial or break
                    self.current_trial += 1
                    self.update_progress()

                    if self.current_trial == 6:
                        self.master.after(100, lambda: self.take_break(15))
                    elif self.current_trial == 12:
                        if self.current_stimulus == 1:
                            self.master.after(100, lambda: self.take_break(120))
                        else:
                            self.master.after(100, self.experiment_complete)
                    else:
                        self.master.after(1000, self.run_trial)

                except Exception as e:
                    print(f"Analysis error: {str(e)}")
                    error_msg = f"Analysis error in trial {self.current_trial + 1}: {str(e)}"
                    with open(os.path.join(trial_dir, 'error_log.txt'), 'w') as f:
                        f.write(error_msg)

                    messagebox.showerror("Analysis Error",
                                         "There was an error analyzing the trial. Please check the microphone levels and try again.")

                    self.next_button.config(text="Retry Trial", command=self.run_trial)
                    self.next_button.grid()

            except Exception as e:
                print(f"Recording error: {str(e)}")
                error_msg = f"Recording error in trial {self.current_trial + 1}: {str(e)}"
                with open(os.path.join(trial_dir, 'error_log.txt'), 'w') as f:
                    f.write(error_msg)

                messagebox.showerror("Recording Error",
                                     "There was an error with the audio recording. Please check your audio settings and try again.")

                self.next_button.config(text="Retry Trial", command=self.run_trial)
                self.next_button.grid()

    def take_break(self, duration):
        """
        Initialize and manage break period between trials.
        
        Parameters:
            duration (int): Break duration in seconds
        """
        self.remaining_time = duration
        self.update_break_timer()
        self.next_button.config(text="Continue", command=self.continue_after_break)
        self.next_button.grid()

    def continue_after_break(self):
        """
        Handle continuation after a break period.
        """
        if hasattr(self, 'timer_id'):
            self.master.after_cancel(self.timer_id)

        if self.current_trial == 6:
            self.next_button.grid_remove()
            self.label.config(text=f"""Recording trial 7/12

                    1. Tap along as accurately as possible with EACH beat
                    2. Remember to ignore the 3 marker beats at start/end
                    3. remember to tap with your right index finger""")
            self.master.after(100, self.run_trial)
        else:  # After stimulus 1
            self.current_stimulus = 2
            self.start_rhythm_practice()

    def update_break_timer(self):
        """
        Update break timer countdown display.
        """
        if self.remaining_time > 0:
            self.label.config(text=f"Break time remaining: {self.remaining_time} seconds\n"
                                   f"Press 'Continue' to skip timer")
            self.remaining_time -= 1
            self.timer_id = self.master.after(1000, self.update_break_timer)
        else:
            self.continue_after_break()

    def experiment_complete(self):
        """
        Handle experiment completion.
        """
        completion_text = """Experiment Complete!

        Thank you for your participation.

        You may now close this window.

        Your data has been saved successfully."""

        self.progress.grid_remove()  # Hide progress bar
        self.label.config(text=completion_text)
        self.next_button.config(text="Close", command=self.master.destroy)
        self.next_button.grid()


def main():
    """
    Main entry point for the experiment application.
    
    Creates and runs the main tkinter window with the experiment GUI.
    """
    root = tk.Tk()
    app = RhythmExperimentGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
