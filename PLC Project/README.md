# 🏭 Sand Plant Energy & Telemetry Monitoring

This project simulates a live Industrial IoT (IIoT) monitoring system for a sand mixing/muller plant. It generates realistic machine telemetry data (matching your real PLC structure), logs it to a local CSV file, and streams it live to InfluxDB Cloud for visualization in Grafana.

---

## 📂 Project Structure

Here is what each file in your project does:

* **`config.py`** — Contains all your connection settings for InfluxDB Cloud (URL, Org, Bucket, Token) and the polling interval (2 seconds).
* **`dummy_plc.py`** & **`dummy_real_plc.py`** — Simulators that act like your real machines. `dummy_real_plc.py` generates data matching your real 22-column sand plant dataset using realistic random-walk algorithms.
* **`csv_logger.py`** — Takes the generated data and saves a local backup copy to the `logs/` folder.
* **`main_real.py`** — The main orchestrator. When you run this, it tells the dummy PLC to generate data every 2 seconds, sends it to the CSV logger, and streams it up to InfluxDB Cloud.
* **`upload_historical.py`** — A utility script we used to upload your old CSV data (from Nov 2025) to InfluxDB Cloud so you had a baseline to look at.
* **`dashboard/grafana/sand_plant_real_dashboard.json`** — The pre-built dashboard layout for Grafana to visualize your data.

---

## 🚀 How to Run the Project in VS Code

Whenever you want to start generating live data, follow these steps:

1. **Open the Project:**
   Open VS Code, go to **File > Open Folder**, and select `C:\Users\Pinak\Desktop\Energy\Demo Project\SandPlantMonitoring`.

2. **Open the Terminal:**
   Go to **Terminal > New Terminal** in the top menu (or press `` Ctrl + ` ``).

3. **Install Dependencies (First Time Only):**
   If you haven't installed the required Python packages on your machine, run this command in the terminal:
   ```bash
   pip install influxdb-client pandas numpy schedule
   ```

4. **Run the Simulator:**
   Type the following command and hit Enter:
   ```bash
   python main_real.py
   ```
   *You will see the console printing out a new cycle every 2 seconds.*

5. **Stop the Simulator:**
   To stop sending data, click inside the terminal and press `Ctrl + C`.

---

## ☁️ How to View Your Data in InfluxDB Cloud

InfluxDB is the time-series database where your data is stored in the cloud.

1. Go to **[https://eu-central-1-1.aws.cloud2.influxdata.com](https://eu-central-1-1.aws.cloud2.influxdata.com)** and log in.
2. Click the **Data Explorer** icon on the left sidebar (it looks like a rising line graph).
3. In the query builder at the bottom of the screen:
   * Select your bucket: **`energy-readings`**
   * Select the measurement: **`SandPlantReal`**
   * Select any field you want to see (e.g., `TOTAL_WATER` or `SAND_TEMP`)
4. Click **Submit** on the right side. You will see a graph of the data you are currently generating from VS Code!

---

## 📊 How to Set Up the Grafana Dashboard

Grafana is the visualization tool that makes the data look beautiful.

### Step 1: Connect Grafana to InfluxDB
1. Open your Grafana instance (either `http://localhost:3000` if installed locally, or your Grafana Cloud URL).
2. Go to **Connections > Add new connection** (or **Data Sources**).
3. Search for **InfluxDB** and click on it.
4. Fill in the following details exactly:
   * **Query Language:** `Flux`
   * **URL:** `https://eu-central-1-1.aws.cloud2.influxdata.com`
   * **Organization:** `jetli-motors-energy`
   * **Token:** `hKtlggJWj_OiEBnPBKG8apArIc9VmPcgttkQHPO2UjA8twd1EOeNBf7FwKadXOsh2OUfquWZhFcrKxsEGvlrTQ==`
   * **Default Bucket:** `energy-readings`
5. Click **Save & Test**. It should say "Data source is working".

### Step 2: Import Your Dashboard
1. On the left sidebar in Grafana, go to **Dashboards > Import** (the `+` sign).
2. Click **Upload JSON file**.
3. Browse to your project folder and select:
   `C:\Users\Pinak\Desktop\Energy\Demo Project\SandPlantMonitoring\dashboard\grafana\sand_plant_real_dashboard.json`
4. On the configuration screen, select your **InfluxDB** data source from the dropdown list.
5. Click **Import**.

### Step 3: Enjoy!
Your dashboard will open immediately. As long as `python main_real.py` is running in your VS Code terminal, you will see the charts, gauges, and alerts updating live every few seconds on your screen.
