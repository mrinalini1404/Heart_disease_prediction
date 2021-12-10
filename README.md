# Heart disease prediction

In this project, we created a user-friendly application that deploys two machine learning models. One takes user info and predicts the criticality of heart disease by random forest and the other takes ECG signal files and pre-processes them using wfdb and uses CNN to predict the type of arrhythmia. The website was made using HTML/CSS and the server used python. 
<br/>Link to the jupyter notebook: https://colab.research.google.com/drive/1sQ6nI1bCw_i0pqxvte2x-llC3HWH0Lga?usp=sharing 


## Installation

Clone the project

```bash
git clone https://github.com/mrinalini1404/Heart_disease_prediction.git
```

Install the requirements
```bash
pip install -r /path/to/requirements.txt
```

## Setting up the database

1. Create a database called healthtracker
2. Restore the database using the healthtracker.dump
```bash
mysql -u [user] -p [database_name] < [filename].sql.
```

Clone the project

```bash
git clone https://github.com/mrinalini1404/Heart_disease_prediction.git
```

Install the requirements
```bash
pip install -r /path/to/requirements.txt
```

## Running the server

Go to the project folder and run the command to start the server

```bash
python3 ecg_api.py
```

Go to a  web browser and access the [Localhost](http://localhost:8080/)

## Contributing
Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

Please make sure to update tests as appropriate.

## License
[MIT](https://choosealicense.com/licenses/mit/)