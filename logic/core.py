import os
import pymupdf
import cv2
import numpy as np
from scipy.spatial.distance import directed_hausdorff
from utils.tools import Tools

class PDFProcessor:
    """Classe gérant le traitement des PDF : découpage et détection de surlignage."""

    def __init__(self, input_dir, output_dir, pattern, debug):
        self.input_dir = input_dir
        self.output_dir = output_dir
        pattern_data = Tools().get_pattern(pattern)
        self.pattern = pattern_data["motif"] if pattern_data and "motif" in pattern_data else []
        self.debug = debug
        self.delete_source = pattern_data.get('delete_source', False) if pattern_data else False

    def process(self):
        """Lance le traitement sur tous les fichiers PDF du dossier source."""
        for filename in os.listdir(self.input_dir):
            if filename.lower().endswith(".pdf"):
                pdf_path = os.path.join(self.input_dir, filename)
                self.split_pdf(pdf_path, self.output_dir)
                # Supprimer le fichier source si l'option est activée
                if self.delete_source:
                    try:
                        os.remove(pdf_path)
                        print(f"✅ Fichier source supprimé : {pdf_path}")
                    except Exception as e:
                        print(f"❌ Erreur lors de la suppression du fichier source : {e}")

    def split_pdf(self, pdf_path, output_dir):
        doc = pymupdf.open(pdf_path)

        # Indices où découper le PDF (pages contenant un surligneur)
        split_indices = []
        for i in range(len(doc)):
            page = doc.load_page(i)
            mat = pymupdf.Matrix(2, 2)
            rect = page.rect
            clip_top_right = pymupdf.Rect(rect.width - 100, 0, rect.width, 100)
            clip_bas_left = pymupdf.Rect(0, rect.height - 100, 100, rect.height)
            if self.detect_highlighter(page.get_pixmap(alpha=True, dpi=300, matrix=mat, clip=clip_top_right), pattern=self.pattern, debug=self.debug) or \
                    self.detect_highlighter(page.get_pixmap(alpha=True, matrix=mat, clip=clip_bas_left), pattern=self.pattern, debug=self.debug):
                split_indices.append(i)

        split_indices = sorted(set(split_indices))
        split_indices.append(len(doc))

        if len(split_indices) == 1:
            print(f"Aucun stabilo détecté, le fichier {pdf_path} ne sera pas découpé.")
            return

        start = 0
        for idx, end in enumerate(split_indices):
            if start < end:
                new_doc = pymupdf.open()  # Nouveau document PDF
                for page_num in range(start, end):
                    new_doc.insert_pdf(doc, from_page=page_num, to_page=page_num)  # Ajouter la page au nouveau document
                output_path = os.path.join(output_dir, f"split_{idx + 1}.pdf")
                new_doc.save(output_path)  # Sauvegarder le nouveau fichier PDF
                print(f"PDF enregistré: {output_path}")
                start = end

    def detect_highlighter(self, image, pattern, debug=True):
        channels = image.n
        img_np = np.frombuffer(image.samples, dtype=np.uint8)
        if channels == 4:
            img_np = img_np.reshape(image.height, image.width, 4)[:, :, :3]
        elif channels == 3:
            img_np = img_np.reshape(image.height, image.width, 3)
        else:
            raise ValueError("Format d'image non pris en charge")
        if debug:
            img_np = img_np.copy()

        # Conversion en HSV et détection du stabilo
        hsv = cv2.cvtColor(img_np, cv2.COLOR_RGB2HSV)

        # Plage de couleurs pour le surlignage
        lowerColor = np.array([21, 60, 90])
        upperColor = np.array([48, 255, 255])
        mask = cv2.inRange(hsv, lowerColor, upperColor)

        # Réduction des contours détectés en lignes minces (squelette)
        mask = self.thin_contour(mask)

        # Détection des contours après affinage
        contours_detect, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        if debug:
            overlay = img_np.copy()
            # Affichage des contours détectés
            cv2.namedWindow("Dessinez une forme")
            cv2.setMouseCallback("Dessinez une forme", pattern)
            while True:
                temp_overlay = overlay.copy()

                # Affichage des contours détectés en vert
                cv2.drawContours(temp_overlay, contours_detect, -1, (0, 255, 0), 2)

                # Affichage du dessin utilisateur en bleu
                if pattern:
                    cv2.polylines(temp_overlay, [np.array(pattern)], isClosed=False, color=(255, 0, 0),
                                  thickness=2)  # Bleu

                cv2.imshow("Dessinez une forme", temp_overlay)
                key = cv2.waitKey(1)

                if key == 13:  # Touche "Entrée" pour valider
                    break

            cv2.destroyAllWindows()

        # Comparaison avec la forme dessinée par l'utilisateur
        if pattern:
            pattern_np = np.array(pattern, dtype=np.int32).reshape((-1, 1, 2))

            for detected_contour in contours_detect:
                detected_contour_np = detected_contour.reshape((-1, 2))

                hausdorff, match = self.compare_shapes(pattern_np.reshape((-1, 2)), detected_contour_np)
                print(f"Distance de Hausdorff: {hausdorff}, Score de similarité OpenCV: {match}")

                if hausdorff < 0.40:  # Seuils ajustables
                    print("Forme similaire détectée ! ✅")
                    return True
                else:
                    print("Forme différente ❌")
                    return False

    def hausdorff_distance(self, contour1, contour2):
        return max(directed_hausdorff(contour1, contour2)[0], directed_hausdorff(contour2, contour1)[0])

    def normalize_contour(self, contour):
        """Centre et normalise la taille du contour pour comparaison."""
        contour = np.array(contour, dtype=np.float32).reshape(-1, 2)

        # Centrer autour du centre de gravité
        centroid = np.mean(contour, axis=0)
        contour -= centroid

        # Mise à l'échelle pour normaliser la taille
        max_dist = np.max(np.linalg.norm(contour, axis=1))
        if max_dist > 0:
            contour /= max_dist

        return contour

    def compare_shapes(self, contour1, contour2):
        """Compare deux contours normalisés."""
        norm_contour1 = self.normalize_contour(contour1)
        norm_contour2 = self.normalize_contour(contour2)

        hausdorff_dist = self.hausdorff_distance(norm_contour1, norm_contour2)
        shape_match = cv2.matchShapes(norm_contour1, norm_contour2, cv2.CONTOURS_MATCH_I1, 0)

        return hausdorff_dist, shape_match

    def thin_contour(self, mask):
        kernel = np.ones((3, 3), np.uint8)
        thin = cv2.morphologyEx(mask, cv2.MORPH_HITMISS, kernel)
        return thin
