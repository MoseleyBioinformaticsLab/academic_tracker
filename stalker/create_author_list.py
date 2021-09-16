from json import dumps

project_1 = {
    "Bernhard Hennig": {  # PI
        "email": "bhennig@uky.edu",
        "current": True,
        "role(s)": {"project leader"},
        "orcid": "0000-0002-7200-302X",
    },
    "Pan Deng": {  # Co-I
        "email": "panda4177@gmail.com",
        "current": True,
        "role(s)": {"project co-leader"},
        "mentor(s)": {"Bernhard Hennig"},
        "orcid": "0000-0003-2974-7389",
    },

    "Hunter Moseley": {  # Co-I
        "email": "hunter.moseley@gmail.com",
        "current": True,
        "role(s)": {"project co-leader"},
        "orcid": "0000-0003-3995-5368",
    },
    "Christian Powell": {  # Trainee (Moseley)
        "email": "christian.powell@uky.edu",
        "current": True,
        "role(s)": {"trainee"},
        "mentor(s)": {"Hunter Moseley", "Kelly Pennell"},
        "orcid": "0000-0002-4242-080X"
    },
}

project_2 = {
    "Kevin Pearson": {  # PI
        "email": "kevin.pearson@uky.edu",
        "current": True,
        "role(s)": {"project co-leader"},
    },
    "Brittany Rice": {  # Trainee (Pearson)"
        "email": "b.rice@uky.edu",
        "current": True,
        "role(s)": {"trainee"},
        "mentor(s)": {"Kevin Pearson"},
    },

    "Hollie Swanson": {  # Co-I
        "email": "hswan@uky.edu",
        "current": True,
        "role(s)": {"project co-leader"}
    },
}

project_3 = {
    "Dibakar Bhattacharyya": {  # PI
        "email": "db@uky.edu",
        "current": True,
        "role(s)": {"project leader"},
    },
    "Kevin Baldridge": {
        "email": "k.b@uky.edu",
        "current": True,
        "role(s)": {"post-doc", "trainee"},
        "mentor(s)": {"Dibakar Bhattacharyya"},
    },
    "Yuxia Ji": {
        "email": "yuxia.ji@uky.edu",
        "current": True,
        "role(s)": {"post-doc", "trainee"},
        "mentor(s)": {"Dibakar Bhattacharyya"},
    },
    "Francisco Leniz": {
        "email": "francisco.leniz@uky.edu",
        "current": True,
        "role(s)": {"trainee"},
        "mentor(s)": {"Dibakar Bhattacharyya"},
    },
    "Rollie Mills": {
        "email": "rolliegmills@uky.edu",
        "current": True,
        "role(s)": {"trainee"},
        "mentor(s)": {"Dibakar Bhattacharyya"},
    },
    "Saiful Islam": {
        "email": "",
        "current": False,
        "role(s)": {"trainee"},
        "mentor(s)": {"Dibakar Bhattacharyya"},
    },

    "Zach Hilt": {  # PI
        "email": "zach.hilt@uky.edu",
        "current": True,
        "role(s)": {"project leader"},
    },
    "Molly Frazar": {
        "email": "molly.frazar@uky.edu",
        "current": True,
        "role(s)": {"trainee"},
        "mentor(s)": {"Zach Hilt"},
    },
    "Victoria Klaus": {
        "email": "mxklaus@uky.edu",
        "current": True,
        "role(s)": {"trainee"},
        "mentor(s)": {"Zach Hilt"},
    },
    "Pranto Paul": {
        "email": "ppa322@uky.edu",
        "current": True,
        "role(s)": {"trainee"},
        "mentor(s)": {"Zach Hilt"},
    },
    "Md Shahriar Rahman": {
        "email": "shahriar.rahman@uky.edu",
        "current": True,
        "role(s)": {"trainee"},
        "mentor(s)": {"Zach Hilt"},
    },
    "Angela Gutierrez": {
        "email": "amgu232@g.uky.edu",
        "current": True,
        "role(s)": {"post-doc"},
        "mentor(s)": {"Zach Hilt", "Kelly Pennell"},
    },
    "Dustin Savage": {
        "email": "",
        "current": False,
        "role(s)": {"trainee"},
        "mentor(s)": {"Zach Hilt"},
    },
    "Rishabh Shah": {
        "email": "",
        "current": False,
        "role(s)": {"trainee"},
        "mentor(s)": {"Zach Hilt"},
    },

    "Lindell Ormsbee": {  # Co-l
        "email": "lindell.ormsbee@uky.edu",
        "current": True,
        "role(s)": {"project co-leader"},
    },
    "Tahiya Tarannum": {
        "email": "t.tarannum@uky.edu",
        "current": False,
        "role(s)": {"trainee"},
        "mentor(s)": {"Lindell Ormsbee"},
    },

    "Isabel Escobar": {  # Co-l
        "email": "isabel.escobar@uky.edu",
        "current": True,
        "role(s)": {"project co-leader"},
    },

    "Tom Dziubla": {  # Co-l
        "email": "thomas.dziubla@uky.edu",
        "current": True,
        "role(s)": {"project co-leader"},
    },

    "T John Balk": {  # Staff
        "email": "john.balk@uky.edu",
        "current": True,
        "role(s)": {"staff"},
    },
}

project_4 = {
    "Kelly Pennell": {  # PI
        "email": "kellypennell@uky.edu",
        "current": True,
        "role(s)": {"project leader"},
    },
    "Ying Li": {  # Staff (Pennell)
        "email": "ying.li@uky.edu",
        "current": True,
        "role(s)": {"research engineer", "trainee"},
        "mentor(s)": {"Kelly Pennell"},
    },
    "Sweta Ojha": {  # Trainee (Pennell)
        "email": "sweta.ojha@uky.edu",
        "current": True,
        "role(s)": {"trainee"},
        "mentor(s)": {"Kelly Pennell"},
    },
    "Nader Rezaei": {  # Staff (Pennell)
        "email": "naderrezaei@uky.edu",
        "current": True,
        "role(s)": {"post-doc", "trainee"},
        "mentor(s)": {"Kelly Pennell"},
    },
    "Ariel Robinson": {  # Trainee (Pennell)
        "email": "ariel.robinson19@uky.edu",
        "current": True,
        "role(s)": {"trainee"},
        "mentor(s)": {"Kelly Pennell"},
    },
    "Hong Cheng Tay": {  # Trainee (Pennell)
        "email": "hermantay9675@uky.edu",
        "current": True,
        "role(s)": {"trainee"},
        "mentor(s)": {"Kelly Pennell"},
    },

    "Anna Hoover": {  # Co-I
        "email": "Anna.Hoover@uky.edu",
        "current": True,
        "role(s)": {"project co-leader"},
    },
}

BEACC = {
    "Andrew Morris": {  # PI
        "email": "a.j.morris@uky.edu",
        "current": True,
        "role(s)": {"project leader"},
    },
    "M Abdul Mottaleb": {  # Co-I
        "email": "m.a.mottaleb@uky.edu",
        "current": True,
        "role(s)": {"project co-leader"},
        "mentor(s)": {"Andrew Morris"}
    },
    "Jianzhong Chen": {  # staff
        "email": "chenjz1977@uky.edu",
        "current": True,
        "role(s)": {"staff"},
        "mentor(s)": {"Andrew Morris"}
    },
    "Yu Li": {  # staff
        "email": "yuli1120@uky.edu",
        "current": True,
        "role(s)": {"staff"},
        "mentor(s)": {"Andrew Morris"}
    },
}


authors = {
    "Spencer Schwab",  # Trainee

    # BEACC
    "Andrew Morris",
    "Abdul Mottaleb",
    "Jianzong Chen",  # Staff
    "Yu Li",  # Staff
    # DMAC
    "Heather Bush",
    "Erin Haynes",
    # CEC
    "Dawn Brewer",
    "Gia Mudd-Martin",
    "Ann Koempel",  # Staff (CEC Coordinator)
}

if __name__ == "__main__":
    with open("../data/authors.json", "w") as f:
        f.write(dumps(list(authors), indent=4))
