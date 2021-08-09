# Go Game with Classic AI Agents; ENSEIRB-MATMECA 2020-2021
Contributors:
    -KHATTAB Omar
    -FETTOUHI Abdelkodousse (Groupe 2 (Machine 1))
    -MECHACH Hamza

## Introduction
A version of Go game in Python3 with some AI Agents;


The following AI Agents are provided:
* Random agent : randomPlayer
* AlphaBeta agent with/without CNN prediction model : abPlayer
* Monte Carlo Tree Search agent with/without prediction model: MCTSAgent/MCTSAgent2 - Montecarlo

All these agents have a interieur class which is myPlayer.

## Requirements

Install dependencies: `tensorflow` `keras` `numpy`
For graphic interface (not needed): `pygame`

## Usage

To play the main player with itself:
    > Use localGame.py

To Start a Match:
    > Examples:
        **mainPlayer** vs. **mainPlayer**: `python3 namedGame.py`

        **random agent** (BLACK) vs. **mainPlayer** (WHITE): `namedGame.py random`

        **AlphaBeta Agent** (BLACK) vs. **random Agent** (WHITE): `namedGame.py abPlayer randomPlayer

        **MCTS Agent** (BLACK) vs. **gnugo Agent** (WHITE): `namedGame.py MCTSAgent gnugoPlayer`

To use Graphic interface, replace namedGame.py with GUI.py

Files namedGame, GUI, and localGame containt the full environment to play a match

Goban.py: the full backend of this Go game, with all logic needed in the game.

## Techniques utilisées dans Monte Carlo TS:
    En général, l'algorithme se base sur 4 étapes:
        > UCTSEARCH : Rechercher en terme du temps sur les fils du noeud. 
            On utilise Upper Confidence Bound pour les rewards.
            Dans MCTSAgent, On utilise le modèle CNN pour directement trouver 
            la probabilité qu'un joueur gagne sur une état.
        > TREEPOLICY : Determine les règles de l'exploitation et l'exploration.
        > PREDICTPOLICY/DEFAULTPOLICY : Determine comment se fait le calcule du poids d'une noeud.
            PREDICT: renvoie la prédiction du modèle.
            DEFAULT: descend avec random jusqu'à une état terminal
        > BACKUP: Pour faire monter le reward vers le parent.
    L'agent est contrôlé par le temps (7.5s).
    L'agent choisit lors des 5 premiers tours une move dans le carrée au centre

## Limitations pour AlphaBeta:
    L'Agent AlphaBeta est limité aussi par le temps.
    De plus, il est limite parfois par le nombre de mouvement à explorer si trop d'options
        se présentent pour mieux exploiter des noeuds.
    