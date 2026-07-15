import numpy as np

def trilateration_n_points(points):
    """
    Calcule la position (x, y) pour n points.
    points : liste de triplets (x_i, y_i, r_i)
    """
    n = len(points)
    if n < 3:
        raise ValueError("Il faut au moins 3 points pour la trilatération en 2D.")
        
    # Extraction du dernier point comme référence (point n)
    xn, yn, rn = points[-1]
    
    A = []
    B = []
    
    # Construction des matrices A et B pour les n-1 premiers points
    for i in range(n - 1):
        xi, yi, ri = points[i]
        
        # Ligne pour la matrice A
        A_row = [2 * (xi - xn), 2 * (yi - yn)]
        A.append(A_row)
        
        # Ligne pour le vecteur B
        B_row = (xi**2 - xn**2) + (yi**2 - yn**2) - (ri**2 - rn**2)
        B.append(B_row)
        
    A = np.array(A)
    B = np.array(B)
    
    # Résolution mathématique : X = (A^T * A)^(-1) * A^T * B
    # En Python, la fonction lstsq gère directement la pseudo-inverse de manière stable
    X, residuals, rank, s = np.linalg.lstsq(A, B, rcond=None)
    
    return X[0], X[1]

# --- EXEMPLE D'UTILISATION ---
# Format : (x, y, distance)
donnees_3_points = [(0, 0, 5), (10, 0, 5), (5, 8, 3)]
donnees_4_points = [(0, 400, 45), (400, 400, 35), (0, 0, 55), (400, 0, 50)]
donnees_5_points = [(0, 0, 5), (10, 0, 5), (5, 8, 3), (2, 4, 1.41), (8, 4, 4.24)]

print("Position avec 3 points :", trilateration_n_points(donnees_3_points))
print("Position avec 4 points :", trilateration_n_points(donnees_4_points))
print("Position avec 5 points :", trilateration_n_points(donnees_5_points))
