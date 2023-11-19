Welcome to BabyExo! The UABiomed Club's submission in natHACKS 2023.
- BabyExo is a project intended to control an RC car through BCI. Its main purpose though is to be a proof of concept for a lower extremity exoskeleton the UABiomed Club is developing.

How does BabyExo work?
- BabyExo uses the Brainflow library to collect and filter EEG data gathered by our OpenBCI headset. It uses 4 channels, each channel connected to a different electrode to gather the data.

Step 1: Data Collection
- Collect data in the form of a time-series. We used EEG for our project.

Step 2: Signal Processing
- The time-series goes through a few filters to remove noise and is converted into the frequency domain. The data can be read by frequency and their corresponding magnitudes.

Step 3: Implement with the RC car
- The commands for the RC car are the frequencies and magnitudes collected previously.
  
To run code:
- Open a Python Version 3.10 Virtual Environment
- Install all the required libraries using the "requirements.txt" file
  - One of the libraries you may need to install yourself --> "-U scikit-learn"
 
Credits:
- UABiomed Team

   

