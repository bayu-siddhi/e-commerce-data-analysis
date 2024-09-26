# Dicoding Final Project: "Learn Data Analysis with Python"
- `Name`: Bayu Siddhi Mukti

## Project Description
This repository is the final project of the Dicoding class "Learn Data Analysis with Python". This project attempts to analyze the E-Commerce Public Dataset data provided by Dicoding or through the source [Kaggle](https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce) with the title **Brazilian E-Commerce Public Dataset by Olist**. The purpose of this analysis is to explore and get to know the dataset, as well as find some interesting insights from the dataset to answer business questions.

## Main Project Structure
- `./data`: Contains all datasets in `.csv` format used in the `Data_Analysis_Project.ipynb` notebook.
- `./dashboard`: Contains all files and codes used to build the data analysis dashboard using Streamlit.
- `Data_Analysis_Project.ipynb`: Interactive Python Notebook (`.ipynb`) file where the entire data analysis process is carried out.

## Install and Run Dashboard
1. Clone the repository to the local computer using the following command.
   ```commandline
   git clone https://github.com/bayu-siddhi/e-commerce-data-analysis.git
   ```

2. Once inside the root directory of this project on your local computer, create a virtual environment (e.g. with the name `.venv`) to install all the dependencies needed to run the notebook and dashboard.
   ```commandline
   python -m venv .venv
   ```

3. Activate the `.venv` virtual environment by running the following command.
   ```commandline
   .\.venv\Scripts\activate
   ```

4. After the virtual environment is active, the next step is to install the project dependencies by running the following command.
   ```commandline
   pip install -r requirements.txt
   ```

5. After all dependencies have been successfully installed, the dashboard can be run using the following command.
   ```commandline
   streamlit run .\dashboard\main.py
   ```

## Alternative Method
If steps 4 and 5 do not work in the virtual environment `.venv` in step 3, then use the method of calling the virtual environment manually as follows.
> Make sure the position of the current working directory is at the root of the project directory.

4. Alternative step number 4.
   ```commandline
   .\.venv\Scripts\python.exe -m pip install -r requirements.txt
   ```

5. Alternative step number 5.
   ```commandline
   .\.venv\Scripts\python.exe -m streamlit run .\dashboard\main.py
   ```

## Screenshots

Here are some screenshots of the dashboard that was successfully run.

<img src="images/tab-1.png" alt="Dashboard Tab 1" width="720">
<img src="images/tab-2.png" alt="Dashboard Tab 2" width="720">
<img src="images/tab-3.png" alt="Dashboard Tab 3" width="720">
<img src="images/tab-4.png" alt="Dashboard Tab 4" width="720">
<img src="images/tab-5.png" alt="Dashboard Tab 5" width="720">
