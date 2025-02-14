import json
import os

# Obtenir le chemin absolu du dossier du projet
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# Construire le chemin absolu vers le fichier patterns.json
PATTERN_FILE = os.path.join(BASE_DIR, "assets", "patterns.json")
DEFAULT_PATTERN = "DEFAULT"  # Clé du pattern par défaut


class Tools:
    def __init__(self):
        self.pattern_file = PATTERN_FILE
        # Créer le dossier assets s'il n'existe pas
        os.makedirs(os.path.dirname(self.pattern_file), exist_ok=True)
        
        # Créer un pattern par défaut si le fichier n'existe pas
        if not os.path.exists(self.pattern_file):
            default_patterns = {
                DEFAULT_PATTERN: {
                    "motif": [ [ 63, 56 ], [ 64, 56 ], [ 64, 57 ], [ 65, 58 ], [ 66, 58 ], [ 66, 59 ], [ 66, 60 ], [ 67, 60 ], [ 67, 61 ], [ 68, 62 ], [ 68, 63 ], [ 69, 63 ], [ 70, 64 ], [ 70, 65 ], [ 70, 66 ], [ 71, 67 ], [ 71, 68 ], [ 72, 69 ], [ 73, 70 ], [ 74, 71 ], [ 76, 72 ], [ 77, 74 ], [ 78, 75 ], [ 80, 77 ], [ 82, 78 ], [ 83, 80 ], [ 85, 81 ], [ 86, 82 ], [ 87, 83 ], [ 89, 85 ], [ 90, 86 ], [ 92, 88 ], [ 94, 90 ], [ 95, 92 ], [ 98, 94 ], [ 99, 96 ], [ 101, 97 ], [ 102, 99 ], [ 104, 101 ], [ 106, 102 ], [ 107, 104 ], [ 109, 105 ], [ 110, 108 ], [ 111, 109 ], [ 113, 110 ], [ 114, 112 ], [ 115, 113 ], [ 116, 115 ], [ 118, 116 ], [ 119, 117 ], [ 120, 118 ], [ 122, 119 ], [ 122, 121 ], [ 124, 122 ], [ 125, 124 ], [ 127, 125 ], [ 128, 126 ], [ 130, 128 ], [ 131, 129 ], [ 132, 130 ], [ 132, 131 ], [ 134, 133 ], [ 134, 134 ], [ 136, 135 ], [ 136, 136 ], [ 137, 137 ], [ 138, 137 ], [ 139, 139 ], [ 140, 140 ], [ 140, 141 ], [ 142, 142 ], [ 142, 143 ], [ 144, 144 ], [ 144, 145 ], [ 145, 146 ], [ 147, 146 ], [ 148, 148 ], [ 149, 148 ], [ 149, 149 ], [ 151, 150 ], [ 152, 152 ], [ 153, 152 ], [ 153, 153 ], [ 154, 154 ], [ 156, 155 ], [ 157, 156 ], [ 158, 157 ], [ 159, 158 ], [ 159, 159 ], [ 161, 160 ], [ 162, 161 ], [ 163, 162 ], [ 164, 163 ], [ 165, 163 ], [ 166, 164 ], [ 167, 165 ], [ 168, 166 ], [ 168, 167 ], [ 169, 167 ], [ 169, 168 ], [ 170, 168 ], [ 171, 168 ], [ 171, 170 ], [ 172, 171 ], [ 172, 172 ], [ 173, 172 ], [ 174, 172 ], [ 174, 173 ], [ 175, 173 ], [ 176, 174 ], [ 177, 175 ], [ 178, 175 ], [ 179, 177 ], [ 179, 178 ], [ 179, 179 ], [ 180, 179 ], [ 180, 180 ], [ 181, 180 ], [ 182, 181 ], [ 182, 182 ], [ 183, 182 ] ],
                    "input_dir": "",
                    "output_dir": ""
                }
            }
            self.save_patterns(default_patterns)

    def load_patterns(self):
        """Charge tous les patterns depuis le fichier JSON."""
        if os.path.exists(self.pattern_file):
            try:
                with open(self.pattern_file, "r") as file:
                    return json.load(file)
            except json.JSONDecodeError:
                print("❌ Erreur : Le fichier JSON est mal formaté.")
        return {}

    def save_patterns(self, patterns):
        """Enregistre les patterns dans le fichier JSON en conservant un backup en cas d'erreur."""
        backup_file = self.pattern_file + ".bak"
        try:
            # Sauvegarde temporaire avant l'écriture
            if os.path.exists(self.pattern_file):
                os.rename(self.pattern_file, backup_file)

            with open(self.pattern_file, "w") as file:
                json.dump(patterns, file, indent=4)

            print("✅ Patterns sauvegardés avec succès.")

            # Suppression du backup après succès
            if os.path.exists(backup_file):
                os.remove(backup_file)

        except Exception as e:
            print(f"❌ Erreur lors de l'enregistrement : {e}")
            # Restaurer le fichier original en cas d'échec
            if os.path.exists(backup_file):
                os.rename(backup_file, self.pattern_file)

    def get_pattern(self, pattern_id):
        """Récupère un pattern par ID, sinon retourne le pattern par défaut."""
        patterns = self.load_patterns()
        pattern_id = str(pattern_id)

        if pattern_id in patterns and len(patterns[pattern_id]["motif"]) != 0:
            return patterns[pattern_id]
        elif DEFAULT_PATTERN in patterns and len(patterns[DEFAULT_PATTERN]["motif"]) != 0:
            print(f"⚠️ Pattern '{pattern_id}' introuvable ou vide. Utilisation du pattern par défaut.")
            return patterns[DEFAULT_PATTERN]
        else:
            print(f"❌ Aucun pattern valide trouvé, ni '{pattern_id}' ni '{DEFAULT_PATTERN}'.")
            return None

    def set_pattern(self, pattern_id, **kwargs):
        """Ajoute ou met à jour partiellement un pattern.
        - Accepte un nombre dynamique de champs à mettre à jour.
        - Vérifie le type des données pour éviter les erreurs.
        """
        patterns = self.load_patterns()
        pattern_id = str(pattern_id)

        # Charger l'ancien pattern ou initialiser des valeurs par défaut
        old_pattern = patterns.get(pattern_id, {"motif":[]})

        # Mise à jour dynamique avec les valeurs fournies dans kwargs
        patterns[pattern_id] = {**old_pattern, **kwargs}

        self.save_patterns(patterns)

"""
# ==== Exemple d'utilisation ====
tools = Tools()

# Ajouter un pattern
tools.set_pattern(1, motif="[(10, 20), (30, 40), (50, 60)]", src="input1.pdf", out="output1.pdf")
tools.set_pattern(DEFAULT_PATTERN, src="default_src.pdf", out="default_out.pdf")

# Récupérer un pattern existant
pattern = tools.get_pattern("1")
print(f"✅ Pattern récupéré : {pattern}")

# Récupérer un pattern inexistant (doit renvoyer DEFAULT)
pattern = tools.get_pattern("42")
print(f"✅ Pattern récupéré : {pattern}")
"""
