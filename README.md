# xMargin: Expected Point Margin Model for Curling

$xMargin$ is a predictive model built to calculate a curling team's expected point margin during a game.

For each end played, performance metric differentials against the opposing team are used to calculate $xMargin_end$, the predicted result for or against the target team during the end.

These $xMargin_{end}$ values are summed to calculate $xMargin$, the cumulative expected point margin throughout the game. 

## Installation

```bash
git clone https://github.com/jmi06/xMargin
cd xMargin
pip install -r requirements.txt
```

## Usage
Start by running the `curlingio.py` file to fetch all the game data and build the datasets.

The `train_model.ipynb` notebook contains the code for testing the model and exporting it to a json file