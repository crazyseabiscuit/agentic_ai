# AI-Powered Anomaly Detection Demonstrations

This project provides two practical examples of anomaly detection using Python and common machine learning libraries.

## Project Overview

The goal is to demonstrate two primary approaches to anomaly detection:

1.  **Unsupervised Anomaly Detection:** Using K-Means clustering to identify unusual patterns in unlabeled time-series data.
2.  **Supervised Anomaly Detection:** Using a RandomForestClassifier to identify fraudulent transactions from a labeled dataset.

## File Structure

-   `anomaly_detection.py`: Script for the unsupervised K-Means approach.
-   `supervised_anomaly_detection.py`: Script for the supervised RandomForest approach.
-   `NAB_dataset.csv`: The time-series dataset used for the unsupervised example.
-   `creditcard_sample.zip`: A zipped, 1000-row sample of a credit card fraud dataset used for the supervised example.
-   `requirements.txt`: Required Python libraries for this project.
-   `presentation.md`: A slide deck explaining the concepts and results.

## Getting Started

### Prerequisites

Ensure you have Python 3 installed.

### Installation

1.  Clone the repository:
    ```bash
    git clone <your-repo-url>
    cd <your-repo-directory>
    ```

2.  Install the required Python libraries:
    ```bash
    pip install -r requirements.txt
    ```

## How to Run the Demos

### 1. Unsupervised Anomaly Detection

This script runs a K-Means clustering algorithm on the `NAB_dataset.csv` to find unusual data points in the time series.

To run it, execute the following command in your terminal:
```bash
python anomaly_detection.py
```
This will generate a plot named `anomaly_detection_plot_kmeans.png` showing the normal data points and the detected anomalies.

### 2. Supervised Anomaly Detection

This script trains a `RandomForestClassifier` on the `creditcard_sample.zip` dataset to distinguish between normal and fraudulent transactions.

**Note:** This script uses a 1000-row sample of the original dataset for demonstration purposes to keep the repository size small.

To run it, execute the following command:
```bash
python supervised_anomaly_detection.py
```
This will train the model, print a classification report to the console, and save a plot named `supervised_fraud_detection_plot.png` visualizing the results on the test data.
