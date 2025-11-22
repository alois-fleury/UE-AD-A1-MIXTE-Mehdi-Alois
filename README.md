# UE-AD-A1-MIXTE - Mehdi BAGHDADI et Aloïs Fleury

[Lien du TP](https://helene-coullon.fr/pages/ue-ad-fil-25-26/tp-mixte/)

## Initialisation et lancement du projet

### Premier lancement du projet (exemple sur Windows)

1. Créer et lancer un environnement virtuel Python en faisant

    python3 -m venv venv
    .\venv\Scripts\activate

2. Installer les packages nécessaires au projet (attention à bien être dans l'environnement virtuel)

    pip install -r requirements.txt

### Lancement d'un projet déjà initialisé

#### MongoDB

Avant de lancer le projet, il faut choisir si on veut utiliser comme base de données les fichiers JSON présents dans les différents dossier ou une base MongoDB.

Pour cela, changer la variable `USING_MONGO` à true ou false selon le choix.

MongoDB charge les fichiers JSON respectifs pour les bases de données au démarrage (attention, si le conteneur est arrêté et redémarré, il est possible que Mongo ait persisté les données, même sans usage explicite de volume dans le `docker-compose.yml`).

**Attention**, si `USING_MONGO` est initialisé à __true__, il faut s'assurer qu'un conteneur MongoDB est lancé (il se lance par défaut dans la configuration docker).

#### Sans Docker

1. Lancer seulement un conteneur MongoDB :

    docker-compose up -d --build mongo

2. Lancer chaque microservice : se placer dans le dossier et exécuter le fichier du même nom avec Python. Exemple sur Windows :
```bash
cd .\booking\
python .\booking.py
```

**Attention**, il faut bien veiller à ce que tous les services  et MongoDB (si utilisé) soient lancés (certaines requêtes font appel à d'autres services). Il faut que le conteneur MongoDB soit démarré avant de démarrer les services.

#### Avec Docker

Il faut se placer à la racine du projet et faire la commande

    docker-compose up -d --build

Par défaut on lance tout les services ainsi qu'un conteneur MongoDB. Pour ne pas lancer le conteneur MongoDB, on peut effectuer la commande suivante : 

    docker-compose up -d --build booking movie schedule user

## Architecture utilisée

L'architecture suivie est en microservices et son schéma est le suivant : 

![Schéma de l'architecture du projet](./images/ARCHI-MIXTE.png)

### Spécificités du projet

*  Chaque dossier contient un fichier `db.py` qui se charge d'appeler le fichier JSON ou la base Mongo en fonction de ce qui a été choisi dans les variables d'environnement.
* Dans [./booking](./booking), le fichier `grpcScheduleClient` donne un exemple de client gRPC faisant appel au service Schedule. Il contient également la fonction `get_schedule_by_date` qui sert au service Booking pour appeler Schedule.
* Le fichier [.env](./.env) :
    * Contient les variables d'environnement utiles au projet (liens des différents services, leur permettant de communiquer et lien de connexion à la base de données)
    * Seule `USING_MONGO` ('true' ou 'false') a besoin d'être changée pour une utilisation normale du projet
    * Chaque service charge les variables au démarrage si besoin
    * Le fonctionnement est détaillé dans le schéma. Mais voici ce qui est spécifique :
        - **Movie** contient également une base d'acteurs. Si un film est supprimé, il est supprimé de la liste de chaque acteur ayant joué dedans. Lorsqu'on affiche un acteur (ou tous les acteurs), on affiche le détail des films dans lequel il a joué.
        - **User** a une route `/user/isadmin/<user_id>` permettant de vérifier si un utilisateur est administrateur ou non (un attribut booléen admin a été ajouté aux utilisateurs). Cette route est appelée par la fonction `checkAdmin` (voir [./checkAdmin.py](./checkAdmin.py)) qui renvoie vrai si l'utilisateur est administrateur, faux dans tous les autres cas (y compris si la requête vers le service utilisateur a échouée).
        - **Chaque microservice** intègre une vérification d'identité via le paramètre `uid` à intégrer dans la requête (il faut y préciser le nom d'utilisateur de la personne qui effectue la requête, pour simuler une connexion). On vérifie les permissions de la façon suivante :
            - Il n'y a pas besoin de préciser le `uid` pour les opérations de lecture (ou GET)
            - Un utilisateur peut ajouter et supprimer sa propre réservation (le uid est le même que le user id précisé dans le body)
            - N'importe qui peut créer un utilisateur qui n'est **pas** administrateur, il faut préciser le `uid` sinon
            - Un utilisateur peut vérifier pour lui-même s'il est admin ou non
            - Il faut être administrateur dans les autres cas (ajout, modification, suppression de réservations, films et utilisateurs)

## Tests et exemples

Les tests ont été réalisés sur Insomnia (voir dossier [./insomnia](./insomnia)). Il y a un fichier de test par microservice. Certains tests renvoient des cas d'erreur (leur titre est explicite ou précise une spécificité de la requête comme 'pas admin' ou 'unknown film'). Une variable d'environnement Insomnia `baselink` permet de ne pas recopier le lien sur chaque requête, elle est importée avec chaque fichier.

Dans la base d'utilisateurs par défaut, seuls `michael_scott` et `dwight_schrute` sont administrateurs (dans tous les autres cas, on teste pour un utilisateur non administrateur, ou qui n'existe pas).
