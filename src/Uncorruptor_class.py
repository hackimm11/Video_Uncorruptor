import numpy as np
import cv2
from scipy.spatial import distance

class Uncorruptor:
    def __init__(self, vid_in, vid_o1, vid_o2):
        self.vid_in = vid_in
        self.vid_o1 = vid_o1
        self.vid_o2 = vid_o2

    def preprocess(self):
        """
        Dans cette methode, on fait un preprocessing des frames de la video donnée, on fait tout d'abord la lecture
        du video et les frames, en créant une liste des frames au niveau grix (afin de manipuler qu'une seule
        intensité par frame), ainsi qu'une liste d'hostogrammes de chaque frame afin de les utiliser dans les 
        prochaines methodes. on applique flatten() au deux listes, car on en besoin de cette forme 1D pour la suite.  

        """
        cap = cv2.VideoCapture(self.vid_in)
        frame_list = []
        histo_list = []
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            else:
                frameg=cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY) # transformer au niveau gris
                frame_list.append(frameg.flatten()) # liste des frames
                histo_list.append(cv2.calcHist([frameg], [0], None, [16], [0, 256]).flatten()) # liste des histogrammes
                
        return frame_list, histo_list

    def cleaner(self, histo_list, frame_list):

        """
        Le but de cette methode est de se debarasser des frames qui n'appartiennent pas à la video originale.
        Pour cela on utilise la caractéristique des histogrammes et trouver leurs correlations avec la mediane,
        du coup on enlève les frames qui sont pas bien corrélées, en définissant un seuil en fonction de l'cart
        intrquartile (IQR). On finit par déminuer la liste des frames (les indices donc changent), mais
        on laisse un vecteur qui porte les vrais indices dans la frames originale. 
        """



        histo_med = np.median(histo_list, axis=0)    # calculer l'histogramme mediane de tous les histogrammes
       
        # la correlation de chaque histogramme avec la mediane 
        correl = [cv2.compareHist(histo_med, histo, cv2.HISTCMP_CORREL) for histo in histo_list] 
        #calculer le threshold en fonction de quartiles
        q1, q3 = np.percentile(correl, 25), np.percentile(correl, 75)
        thresh = q1 - 1.5 * (q3 - q1)
        
        clean_ind=[]
        i = len(frame_list)-1

        #une boucle pour enlever les fausses frames, en calculant en meme temps le vecteur porteur des vrais indices
        # on utilise while en inverse à cause de pop() 
        while i >= 0 :
            if correl[i] < thresh:
               frame_list.pop(i) 
            else:
                clean_ind.append(i)
            
            i = i-1
        
        clean_ind = clean_ind[::-1] # on inverse les elements(indices vrais) de la liste car ils etaient remplies
                                    #inversement dans la boucle
    
        return clean_ind



    def reorderer(self, frame_list):

        """
        Dans cette etape on met en ordre les frames cleans obtenus en dessus (frame_list change en dessus),
        une approche c'est de calculer les distances euclidiennes entre tous les frames, et definir le premier frame
        (ou le dernier) et qui a la somme des distances maximales avec tous les autres frames, aprés on trouve le 
        frame qui a la distance minimale avec le frame premier frame, on refait ça jusqu'à trouver tous l'ordre final
        de tous les frames.

        
        """
        distances = distance.cdist(frame_list, frame_list, 'euclidean') # tableau des distances euclidiennes entre
                                                                        # tous les frames
        start_frame = np.argmax(np.sum(distances, axis=1)) # trouver l'indice du premier frame
                                                       
        ordered_indices = [start_frame]     # c'est le premier element de la liste des indices en ordre 

        for _ in range(len(frame_list) - 1): 
            remaining_frames = set(range(len(frame_list))) - set(ordered_indices) 

            min_distance = float('inf') # initialisation pour la comparaison(avec distance_to_last) 
        
            # cette boucle pour comparer la distance de dernier element dans liste en ordre avec tous les autres
            # frames, et garder l'indice du minimum qui représente la frame plus proche a ce dernier 
            for frame_ind in remaining_frames:  
                distance_to_last = distances[ordered_indices[-1]][frame_ind]  
                if distance_to_last < min_distance:     
                    min_distance = distance_to_last    
                    next_f_ind = frame_ind                           

            # Add the next frame to the ordered list
            ordered_indices.append(next_f_ind)

        true_order=ordered_indices
        return true_order

    def vid_writer(self, video_file_out, true_order, clean_f):
        """
        c'est l'etape finale qui combine les clean frames en bon ordre en utilisant le lien qu'on a laissé (clean_ind)
        qui représente les indices des clean frames dans la liste des frames originale. En gros on doit refaire la
        lecture des frames de la vidéo originale car on une liste des frames gris, en plus c'est plus simple.
        """
        cap = cv2.VideoCapture(self.vid_in)
        fps = cap.get(cv2.CAP_PROP_FPS) # le fps de la video original on doit le garder
        framew = cap.get(cv2.CAP_PROP_FRAME_WIDTH) # le width des frames
        frameh = cap.get(cv2.CAP_PROP_FRAME_HEIGHT) # le height des frames
        fourcc = cv2.VideoWriter_fourcc(*'MP4V') # le codec pour le mp4
        vid = cv2.VideoWriter(video_file_out, fourcc, fps, (int(framew), int(frameh))) # on initialise le writer de
                                                                                     #la nouvelle clean video
         
         #le but est trouver le frame qui correspond a f pour chaque relecture de la video originale 
        for f in true_order: 
            i = 0 # indice pour numeroter les frames de la video originale 
            while True:
                ret, frame = cap.read()
                if not ret:
                    break
                if i == clean_f[f]:  # le matching, si elle verifie ça donc il correspond au bon indice du bon frame
                                                          # dans la vidéo originale
                    vid.write(frame) # on l'ajoute au vidéo reconstruite
                i += 1
            cap.set(cv2.CAP_PROP_POS_FRAMES, 0) # reinitialiser la lecture a 0

    def uncorrupted_vids(self):
        """
        Finalement on combine tous les méthodes précedentes dans cette dernière methode, afin de trouver la version
        incorrompue de la video corrompue. il ne suffit que d'initialiser la class e appeler cette méthode directement
          dans le main
        """
        frame_list, histo_list = self.preprocess()
        clean_ind = self.cleaner(histo_list, frame_list)
        true_order = self.reorderer(frame_list)
        self.vid_writer(self.vid_o1, true_order, clean_ind)
        self.vid_writer(self.vid_o2, true_order[::-1], clean_ind)
