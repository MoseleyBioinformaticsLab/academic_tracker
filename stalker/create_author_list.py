from json import dumps


authors = {
    # Project 1
    "Bernhard Hennig",  # PI
    "Chunyan Wang",  # Trainee
    "Hunter Moseley",  # Co-I
    "Robert Flight",
    "Christian Powell",
    "Pan Deng",  # Co-I/Trainee
    # Project 2
    "Kevin Pearson",  # PI
    "Hollie Swanson",  # Co-I
    "Brittany Rice",  # Trainee
    # Project 3
    "Dibakar Bhattacharyya",  # PI
    "Zach Hilt",  # Co-I
    "Isabel Escobar",  # Co-I
    "Tom Dziubla",  # Co-I
    "Lindell Ormsbee",  # Co-I
    "John Balk",  # Collaborator
    "Angela Gutierez",  # Trainee
    "Rollie Mills",  # Trainee
    "Spencer Schwab",  # Trainee
    "Rishabh Shah",  # Trainee
    "Molly Frazar",  # Trainee
    "Saiful Islam",  # Trainee
    "Tahiya Tarannum",  # Trainee
    "Yuxia Ji",  # Trainee
    # Project 4
    "Kelly Pennell",  # PI
    "Anna Hoover",  # Co-I
    "Ying Li",  # Trainee
    "Sweta Ojha",  # Trainee
    "Ariel Robinson",  # Trainee
    # Admin
    "Bernhard Hennig",
    "Lindell Ormsbee",
    "Kelly Pennell",
    "Jennifer Moore",  # Staff
    "Emily Koyagi",  # Staff
    # BEACC
    "Andrew Morris",
    "Abdul M Mottaleb",
    "Jianzong Chen",  # Staff
    "Yu Li",  # Staff
    # DMAC
    "Kelly Pennell",
    "Heather Bush",
    "Hunter Moseley",
    "Erin Haynes",
    "Christian Powell",  # Staff
    "Emily Koyagi",  # Staff
    # CEC
    "Dawn Brewer",
    "Gia Mudd-Martin",
    "Ann Koempel",  # Staff (CEC Coordinator)
    # RETCC
    "Zach Hilt",
    "Bernhard Hennig",
    "Angela Gutierez",  # Staff (RETCC Liaison)
}

if __name__ == "__main__":
    with open("../data/authors.json", "w") as f:
        f.write(dumps(list(authors), indent=4))
