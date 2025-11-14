# Baseball Simulator

This Python code simulates the offense of a baseball team, so you can compare different lineups and see which scores best.

## Install 

I recommend using [conda](https://www.anaconda.com/docs/getting-started/miniconda/install#quickstart-install-instructions) 
to create a new virtual environment for this project. In the project directory, run:
``` 
conda create -n baseballsim python=3.10
conda activate baseballsim
pip install -r requirements.txt
```

## How to run
Run the `simulator.py` file.

At the bottom, uncomment either
- `play_one_game` (to see a game printed out play-by-play) or 
- `play_many_games` (to simulate many).


## Possible improvements:
- make double play prob depend on where runners are on base
- make double play prob depend on which runner it is
- make steal probs depend on which runner it is
- actually, make all probabilities depend on which runner it is
- make prob_advance_runner_on_out depend on where runners are on base
- make histogram of scores when many are played


## Citation

If you find this code useful, please cite:

Grooten, Bram. _Baseball Simulator_. GitHub repository. URL: https://github.com/bramgrooten/baseball-simulator, 2022.

LaTeX format:
```
@misc{grooten2022baseball_simulator,
  title = {{Baseball Simulator}},
  author = {Grooten, Bram},
  year = {2022},
  howpublished = {GitHub repository. URL: \url{https://github.com/bramgrooten/baseball-simulator}},
}
```

