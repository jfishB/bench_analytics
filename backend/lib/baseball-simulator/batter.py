from numpy.random import choice


def compute_probs_from_dataset(dataset, batter_id):
    """
    Computes probabilities for options like walk, hit, homerun, etc.
    :param dataset: a pandas dataframe imported from Excel file from
                        http://baseballguru.com/bbdata1.html
    :param batter_id: the player id as in the first column of the Excel file
    :return: a list of probs
    """
    df = dataset.loc[dataset["playerID"] == batter_id].iloc[0]
    # options = ["strike-out", "in-play-out", "walk",
    #            "single", "double", "triple", "homerun"]
    probs = []
    plate_appears = df["tap"]

    strike_outs = df["SO"] / plate_appears
    outs = (plate_appears - df["SO"] - df["BB"] - df["H"]) / plate_appears
    walks = df["BB"] / plate_appears
    singles = (df["H"] - df["db"] - df["tr"] - df["HR"]) / plate_appears
    doubles = df["db"] / plate_appears
    triples = df["tr"] / plate_appears
    homeruns = df["HR"] / plate_appears

    probs.append(strike_outs)
    probs.append(outs)
    probs.append(walks)
    probs.append(singles)
    probs.append(doubles)
    probs.append(triples)
    probs.append(homeruns)

    name = f"{df['nameFirst']} {df['nameLast']}"
    return probs, name


class Batter:
    def __init__(self, probabilities=None, name="Joe Default", player_id=None, dataset=None):
        """
        One of these arguments needs to be not-None:
        :param probabilities: must sum up to one
        :param player_id: should be like in the Excel sheet
        :param name: only necessary if not from Excel, otherwise will be taken
        """
        if probabilities is None:
            self.probs, self.name = compute_probs_from_dataset(dataset, player_id)
        else:
            self.probs = probabilities
            self.name = name
        self.options = [
            "strike-out",
            "in-play-out",
            "walk",
            "single",
            "double",
            "triple",
            "homerun",
        ]

    def swing(self):
        """
        Batter takes a swing
        :return: the result (may actually be everything, also a walk)
        """
        return choice(self.options, p=self.probs)

    def print_probabilities(self):
        print(
            f"strike-out: {self.probs[0]:.3f} \t "
            f"in-play-out: {self.probs[1]:.3f} \t "
            f"walk: {self.probs[2]:.3f} \t "
            f"single: {self.probs[3]:.3f} \t "
            f"double: {self.probs[4]:.3f} \t "
            f"triple: {self.probs[5]:.3f} \t "
            f"homerun: {self.probs[6]:.3f}"
        )
