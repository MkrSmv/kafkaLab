# KafkaLab - Training Metrics Dashboard

This project provides a real-time dashboard for monitoring the metrics of a machine learning model trained with **XGBoost**. The dashboard is built using **Streamlit** and integrates with **Kafka** to receive training metrics such as log loss, RMSE, MAE, error, and AUC.

## Requirements

Before you start, make sure you have Docker installed and running on your machine. You can download Docker from [here](https://www.docker.com/products/docker-desktop).

### Clone the repository

1. Clone this repository to your local machine:
   ```bash
   git clone https://github.com/MkrSmv/kafkaLab
2. Navigate into the project directory:
    ```bash
    cd kafkaLab

# Build and Start the Docker Containers
1. Build and start the required Docker containers:
    ```bash
    docker-compose up -d --build

# Access the Dashboard
Once the containers are up and running, you can access the training metrics dashboard on:

http://localhost:8501/

and wait 2-3 minutes

# Features

- **Real-time Monitoring**: The dashboard shows real-time updates of various model metrics, including:
  - **Log Loss**
  - **RMSE (Root Mean Squared Error)**
  - **MAE (Mean Absolute Error)**
  - **Error**
  - **AUC (Area Under Curve)**

- **Kafka Integration**: The model training metrics are sent via Kafka, and the Streamlit dashboard consumes this data to update the metrics dynamically.

## How It Works

1. **Kafka** is used for streaming model training metrics.
2. **Streamlit** is used to display these metrics in real-time on the web-based dashboard.
3. The dashboard provides separate graphs for each metric (Log Loss, RMSE, MAE, Error, AUC), and updates them continuously as new data is consumed from Kafka.
