# TP IA; ENSEIRB-MATMECA

## Contributeurs: Etudiants au 2ieme année Informatique
    FETTOUHI Abdelkodousse> (Groupe 2 (Machine 1))
    KHATTAB Omar>
    MECHACH Hamza>

### Description des objectifs et travail réalisé:
    *Déployer des methodes d'apprentissage automatique permettant d'évaluer la qualité de plateaux de GO.
    *Identification du problème: problème de regression.
    *Description du problème: Identifier la probabilité que le joueur Noir gagne une partie du jeu.
    *Travail divisé en 3 étapes:
        1- Compréhension des données de chaque entrée du Data Set.
        2- Définir les données en entrée et en sortie du modèle final de prédiction
        3- Réalisation du modèle:
            -Transformation des données en arrays de numpy:
                *Les arrays sont de taille (data length, board size, board size, 2) afin de représenter
                les tableaux des deux joueurs
                *Agrandissement des données par des rotations de 90 degrée et des symmetries.
            -Construction du modèle neuronal et entrainnement:
                *Utilisation des couches BatchNormalisation avec Conv2D, et Dropout afin de éviter l'overfitting de l'entrainement.
                *Loss function: MAE: calcule de l'erreur absolue entre la valeur de prédiction et la valeur réelle.
                *Fonction d'optimisation: Adam.
        4- Génération d'un fichier de prédictions apartir d'une nouvelle dataSet.

#### Usage
    > Le modèle est enregistrer dans le fichier "model-final.json"
        les poids sont décrit dans le fichier "model-TP-IA.h5"
    > Le fichier tp-ml-go.ipynb contient le Code de l'entrainement avec plus de détaille sur l'implementation
    > DataSets d'entrainement et de vérification: 
        `positions-to-evaluate-9x9.json.gz`,
        `samples-9x9.json.gz`
    