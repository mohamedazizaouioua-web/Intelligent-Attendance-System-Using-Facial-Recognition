# gui_app.py (Version 4.7 - Correction de l'Erreur Silencieuse)

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import cv2
import pickle
import numpy as np
import time
import datetime
import sqlite3
import os
import shutil
from deepface import DeepFace
from PIL import Image, ImageTk
import ttkbootstrap as ttk

class AttendanceApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Système de Pointage ")
        self.root.geometry("1400x900")
        self.DB_FILE = "societe.db"; self.FACE_DB_PKL = "face_database.pkl"; self.FACES_FOLDER = "database"
        self.RECOGNITION_THRESHOLD = 0.60; self.ATTENDANCE_TIMER_SECONDS = 6; self.GRACE_PERIOD_SECONDS = 3
        self.DETECTOR_BACKEND = "ssd"; self.MODEL_NAME = "ArcFace"
        self.camera_is_running = False; self.history_window = None
        self.face_database = self.load_face_database()
        self.notebook = ttk.Notebook(self.root, bootstyle="primary")
        self.notebook.pack(pady=10, padx=10, fill="both", expand=True)
        self.tab_attendance = ttk.Frame(self.notebook); self.tab_management = ttk.Frame(self.notebook); self.tab_dashboard = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_attendance, text='Système de Pointage'); self.notebook.add(self.tab_management, text='Gestion des Employés'); self.notebook.add(self.tab_dashboard, text='Tableau de Bord')
        self.setup_attendance_tab(); self.setup_management_tab(); self.setup_dashboard_tab()

    def setup_attendance_tab(self):
        # ... (code inchangé)
        main_frame = ttk.Frame(self.tab_attendance, padding="10"); main_frame.pack(fill=tk.BOTH, expand=True)
        video_frame = ttk.LabelFrame(main_frame, text="Flux Caméra", bootstyle="info"); video_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=10)
        self.video_label = ttk.Label(video_frame); self.video_label.pack()
        controls_frame = ttk.Frame(main_frame, width=350); controls_frame.pack(side=tk.RIGHT, fill=tk.Y, padx=10, pady=10)
        self.start_button = ttk.Button(controls_frame, text="Démarrer la Caméra", command=self.start_camera, bootstyle="success"); self.start_button.pack(fill=tk.X, pady=5)
        self.stop_button = ttk.Button(controls_frame, text="Arrêter la Caméra", command=self.stop_camera, state=tk.DISABLED, bootstyle="danger"); self.stop_button.pack(fill=tk.X, pady=5)
        self.history_button = ttk.Button(controls_frame, text="Afficher l'Historique (Fenêtre)", command=self.open_history_window, bootstyle="secondary"); self.history_button.pack(fill=tk.X, pady=20)
        status_label_frame = ttk.LabelFrame(controls_frame, text="Statut", bootstyle="info"); status_label_frame.pack(fill=tk.X, pady=10)
        self.status_label = ttk.Label(status_label_frame, text="Prêt", font=("Helvetica", 12, "bold")); self.status_label.pack(pady=5)
        log_frame = ttk.LabelFrame(controls_frame, text="Pointages du Jour (Live)", bootstyle="info"); log_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        self.log_listbox = tk.Listbox(log_frame); self.log_listbox.pack(fill=tk.BOTH, expand=True)
        self.logged_today = set(); self.current_candidate_name = None; self.total_accumulated_time = 0.0; self.last_seen_time = None; self.cap = None

    def setup_management_tab(self):
        # ... (code inchangé)
        main_frame = ttk.Frame(self.tab_management, padding="10"); main_frame.pack(fill=tk.BOTH, expand=True)
        list_frame = ttk.LabelFrame(main_frame, text="Liste des Employés", bootstyle="info"); list_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=10)
        columns = ('id', 'name'); self.employee_treeview = ttk.Treeview(list_frame, columns=columns, show='headings', bootstyle="primary")
        self.employee_treeview.heading('id', text='ID'); self.employee_treeview.heading('name', text='Nom Complet')
        self.employee_treeview.column('id', width=50); self.employee_treeview.pack(fill=tk.BOTH, expand=True)
        actions_frame = ttk.Frame(main_frame, width=400); actions_frame.pack(side=tk.RIGHT, fill=tk.Y, padx=10, pady=10)
        add_frame = ttk.LabelFrame(actions_frame, text="Ajouter un Nouvel Employé", bootstyle="info"); add_frame.pack(fill=tk.X, pady=10)
        ttk.Label(add_frame, text="Nom de l'employé:").pack(padx=5, pady=5)
        self.new_employee_name_entry = ttk.Entry(add_frame, bootstyle="primary"); self.new_employee_name_entry.pack(fill=tk.X, padx=5, pady=5)
        ttk.Button(add_frame, text="Ajouter via Caméra", command=self.add_employee_from_camera, bootstyle="primary").pack(fill=tk.X, padx=5, pady=5)
        ttk.Button(add_frame, text="Ajouter via Dossier", command=self.add_employee_from_folder, bootstyle="primary").pack(fill=tk.X, padx=5, pady=5)
        delete_frame = ttk.LabelFrame(actions_frame, text="Supprimer un Employé", bootstyle="info"); delete_frame.pack(fill=tk.X, pady=10)
        ttk.Button(delete_frame, text="Supprimer l'Employé Sélectionné", command=self.delete_employee, bootstyle="danger").pack(fill=tk.X, padx=5, pady=5)
        update_frame = ttk.LabelFrame(actions_frame, text="Mise à Jour de la Base de Reconnaissance", bootstyle="info"); update_frame.pack(fill=tk.X, pady=20)
        self.update_button = ttk.Button(update_frame, text="METTRE À JOUR MAINTENANT", command=self.update_face_database, bootstyle="warning")
        self.update_button.pack(fill=tk.X, padx=5, pady=5)
        self.populate_employee_list()

    def setup_dashboard_tab(self):
        # ... (code inchangé)
        main_frame = ttk.Frame(self.tab_dashboard, padding="10"); main_frame.pack(fill=tk.BOTH, expand=True)
        filter_frame = ttk.LabelFrame(main_frame, text="Filtres de recherche", bootstyle="info"); filter_frame.pack(fill=tk.X, padx=10, pady=10)
        ttk.Label(filter_frame, text="Employé :").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.dashboard_employee_combo = ttk.Combobox(filter_frame, bootstyle="primary"); self.dashboard_employee_combo.grid(row=0, column=1, padx=5, pady=5, sticky="ew")
        date_format = "%Y-%m-%d"
        ttk.Label(filter_frame, text="Date de début :").grid(row=1, column=0, padx=5, pady=5, sticky="w")
        self.dashboard_start_date = ttk.DateEntry(filter_frame, bootstyle="primary", dateformat=date_format); self.dashboard_start_date.grid(row=1, column=1, padx=5, pady=5, sticky="ew")
        ttk.Label(filter_frame, text="Date de fin :").grid(row=1, column=2, padx=5, pady=5, sticky="w")
        self.dashboard_end_date = ttk.DateEntry(filter_frame, bootstyle="primary", dateformat=date_format); self.dashboard_end_date.grid(row=1, column=3, padx=5, pady=5, sticky="ew")
        ttk.Button(filter_frame, text="Rechercher", command=self.search_attendance, bootstyle="success").grid(row=1, column=4, padx=20, pady=5)
        filter_frame.columnconfigure(1, weight=1); filter_frame.columnconfigure(3, weight=1)
        results_frame = ttk.Frame(main_frame); results_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        stats_frame = ttk.LabelFrame(results_frame, text="Statistiques", bootstyle="info"); stats_frame.pack(fill=tk.X, pady=5)
        self.dashboard_stats_label = ttk.Label(stats_frame, text="Sélectionnez un employé et une période pour voir les statistiques.", font=("Helvetica", 10)); self.dashboard_stats_label.pack(padx=10, pady=10)
        tree_frame = ttk.LabelFrame(results_frame, text="Résultats des pointages", bootstyle="info"); tree_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        columns = ('id', 'name', 'timestamp'); self.dashboard_treeview = ttk.Treeview(tree_frame, columns=columns, show='headings', bootstyle="primary")
        self.dashboard_treeview.heading('id', text='ID Pointage'); self.dashboard_treeview.heading('name', text='Nom Employé'); self.dashboard_treeview.heading('timestamp', text='Date et Heure')
        self.dashboard_treeview.column('id', width=100); self.dashboard_treeview.column('name', width=200)
        self.dashboard_treeview.pack(fill=tk.BOTH, expand=True)
        self.populate_employee_combobox()

    # --- LA CORRECTION EST DANS LES FONCTIONS SUIVANTES ---
    
    def update_frame(self):
        if not self.camera_is_running: return
        ret, frame = self.cap.read()
        if not ret:
            self.root.after(10, self.update_frame)
            return
        
        found_person_in_frame = None
        try:
            # On utilise .represent() directement car il est plus complet et gère les erreurs en interne.
            # On demande à ne pas planter si aucun visage n'est trouvé.
            face_objs = DeepFace.represent(img_path=frame, 
                                           model_name=self.MODEL_NAME, 
                                           detector_backend=self.DETECTOR_BACKEND, 
                                           enforce_detection=False)
            
            # DeepFace.represent renvoie une liste d'objets, un par visage trouvé
            for face_obj in face_objs:
                # Si le visage n'est pas valide (trop petit, etc.), la clé 'embedding' peut manquer.
                if 'embedding' in face_obj:
                    target_embedding = face_obj['embedding']
                    facial_area = face_obj['facial_area']
                    x, y, w, h = facial_area.values()
                    
                    best_match_name, min_distance = self.find_best_match(target_embedding)
                    
                    display_name = "Unknown"
                    if min_distance < self.RECOGNITION_THRESHOLD:
                        display_name = best_match_name
                        if found_person_in_frame is None:
                            found_person_in_frame = best_match_name
                    
                    color = (0, 255, 0) if display_name != "Unknown" else (0, 0, 255)
                    cv2.rectangle(frame, (x, y), (x + w, y + h), color, 2)
                    cv2.putText(frame, f"{display_name} ({min_distance:.2f})", (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)

        except Exception as e:
            # On affiche l'erreur dans le terminal pour le débogage, mais l'app ne plante pas.
            print(f"ERREUR dans la boucle de détection: {e}")
            
        self.process_attendance(found_person_in_frame)
        
        img = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        img = Image.fromarray(img)
        imgtk = ImageTk.PhotoImage(image=img)
        self.video_label.imgtk = imgtk
        self.video_label.configure(image=imgtk)
        self.root.after(10, self.update_frame)

    # ... (le reste du code est inchangé)
    def populate_employee_combobox(self):
        # ...
        try:
            conn = sqlite3.connect(self.DB_FILE); cursor = conn.cursor()
            cursor.execute("SELECT name FROM employees ORDER BY name")
            employee_names = [row[0] for row in cursor.fetchall()]
            conn.close()
            self.dashboard_employee_combo['values'] = ["Tous les employés"] + employee_names
        except Exception as e: print(f"Erreur chargement combobox: {e}")

    def search_attendance(self):
        # ...
        employee_name = self.dashboard_employee_combo.get()
        start_date_str = self.dashboard_start_date.entry.get()
        end_date_str = self.dashboard_end_date.entry.get()
        if not employee_name or not start_date_str or not end_date_str:
            messagebox.showwarning("Filtre incomplet", "Veuillez sélectionner un employé et une période de date valide.")
            return
        for item in self.dashboard_treeview.get_children(): self.dashboard_treeview.delete(item)
        self.dashboard_stats_label.config(text="")
        try:
            conn = sqlite3.connect(self.DB_FILE); cursor = conn.cursor()
            base_query = "SELECT attendance.id, employees.name, attendance.timestamp FROM attendance JOIN employees ON attendance.employee_id = employees.id"
            conditions = ["date(attendance.timestamp) BETWEEN ? AND ?"]
            params = [start_date_str, end_date_str]
            if employee_name != "Tous les employés":
                conditions.append("employees.name = ?")
                params.append(employee_name)
            base_query += " WHERE " + " AND ".join(conditions) + " ORDER BY attendance.timestamp DESC"
            cursor.execute(base_query, tuple(params))
            records = cursor.fetchall()
            conn.close()
            if employee_name == "Tous les employés":
                self.dashboard_treeview['displaycolumns'] = ('id', 'name', 'timestamp')
            else:
                self.dashboard_treeview['displaycolumns'] = ('id', 'timestamp')
            for record in records:
                self.dashboard_treeview.insert('', tk.END, values=record)
            stats_text = f"Employé: {employee_name} | Période: du {start_date_str} au {end_date_str}\n"
            stats_text += f"Nombre total de pointages trouvés : {len(records)}"
            self.dashboard_stats_label.config(text=stats_text)
        except Exception as e:
            messagebox.showerror("Erreur de recherche", f"Une erreur est survenue : {e}")
            
    def populate_employee_list(self):
        for item in self.employee_treeview.get_children(): self.employee_treeview.delete(item)
        conn = sqlite3.connect(self.DB_FILE); cursor = conn.cursor()
        cursor.execute("SELECT id, name FROM employees ORDER BY name")
        for row in cursor.fetchall(): self.employee_treeview.insert('', tk.END, values=row)
        conn.close()
        self.populate_employee_combobox()

    def add_employee_from_folder(self):
        name = self.new_employee_name_entry.get().strip();
        if not name: messagebox.showerror("Erreur", "Veuillez entrer un nom."); return
        destination_folder = os.path.join(self.FACES_FOLDER, name)
        if os.path.exists(destination_folder): messagebox.showerror("Erreur", f"Le dossier '{name}' existe déjà."); return
        conn = sqlite3.connect(self.DB_FILE); cursor = conn.cursor()
        cursor.execute("SELECT id FROM employees WHERE name = ?", (name,))
        if cursor.fetchone(): messagebox.showerror("Erreur", f"Le nom '{name}' existe déjà dans la DB."); conn.close(); return
        conn.close()
        folder_path = filedialog.askdirectory(title="Sélectionnez le dossier")
        if not folder_path: return
        os.makedirs(destination_folder)
        image_count = 0
        for filename in os.listdir(folder_path):
            if filename.lower().endswith(('.png', '.jpg', '.jpeg')):
                shutil.copy(os.path.join(folder_path, filename), destination_folder); image_count += 1
        if image_count == 0: os.rmdir(destination_folder); messagebox.showwarning("Avertissement", "Aucune image valide."); return
        try:
            conn = sqlite3.connect(self.DB_FILE); cursor = conn.cursor()
            cursor.execute("INSERT INTO employees (name) VALUES (?)", (name,)); conn.commit(); conn.close()
            self.populate_employee_list()
            messagebox.showinfo("Succès", f"Employé '{name}' ajouté.\nN'oubliez pas de 'Mettre à Jour'.")
        except sqlite3.IntegrityError: messagebox.showerror("Erreur", f"Erreur d'intégrité DB pour '{name}'.")

    def add_employee_from_camera(self):
        name = self.new_employee_name_entry.get().strip()
        if not name: messagebox.showerror("Erreur", "Veuillez entrer un nom."); return
        destination_folder = os.path.join(self.FACES_FOLDER, name)
        if os.path.exists(destination_folder): messagebox.showerror("Erreur", f"Un dossier pour '{name}' existe déjà."); return
        conn_check = sqlite3.connect(self.DB_FILE); cursor_check = conn_check.cursor()
        cursor_check.execute("SELECT id FROM employees WHERE name = ?", (name,));
        if cursor_check.fetchone(): messagebox.showerror("Erreur", f"Le nom '{name}' existe déjà."); conn_check.close(); return
        conn_check.close()
        
        capture_window = tk.Toplevel(self.root); capture_window.title(f"Capture pour {name}"); capture_window.grab_set()
        video_label = ttk.Label(capture_window); video_label.pack(pady=10, padx=10)
        cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
        if not cap.isOpened(): cap = cv2.VideoCapture(0)
        if not cap.isOpened(): messagebox.showerror("Erreur", "Impossible d'ouvrir la caméra.", parent=capture_window); capture_window.destroy(); return
        instructions = ["Regardez droit devant", "Tête à gauche", "Tête à droite", "Regardez en haut", "Souriez !"]; captured_frames = []
        
        def update_display_loop():
            if not cap.isOpened(): return
            ret, frame = cap.read()
            if ret:
                display_frame = frame.copy(); photo_count = len(captured_frames)
                if photo_count < len(instructions):
                    cv2.putText(display_frame, f"Instruction: {instructions[photo_count]}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 255), 2)
                    cv2.putText(display_frame, f"Appuyez sur 'ESPACE' ({photo_count + 1}/{len(instructions)})", (10, 70), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
                img = cv2.cvtColor(display_frame, cv2.COLOR_BGR2RGB); img = Image.fromarray(img); imgtk = ImageTk.PhotoImage(image=img)
                video_label.imgtk = imgtk; video_label.configure(image=imgtk)
            capture_window.after(10, update_display_loop)
            
        def take_picture(event=None):
            if len(captured_frames) < len(instructions):
                ret, frame = cap.read()
                if ret:
                    captured_frames.append(frame); print(f"Photo {len(captured_frames)} capturée.")
                    if len(captured_frames) == len(instructions): process_and_save()

        def process_and_save():
            on_close(); os.makedirs(destination_folder)
            for i, frame in enumerate(captured_frames): cv2.imwrite(os.path.join(destination_folder, f"{name}_{i+1}.jpg"), frame)
            try:
                conn = sqlite3.connect(self.DB_FILE); cursor = conn.cursor()
                cursor.execute("INSERT INTO employees (name) VALUES (?)", (name,)); conn.commit(); conn.close()
                self.populate_employee_list(); messagebox.showinfo("Succès", f"Employé '{name}' ajouté.\nN'oubliez pas de 'Mettre à Jour'.")
            except sqlite3.IntegrityError: shutil.rmtree(destination_folder); messagebox.showerror("Erreur", f"Le nom '{name}' existe déjà dans la DB.")
            
        def on_close():
            if cap.isOpened(): cap.release()
            capture_window.destroy()
            
        capture_window.bind('<space>', take_picture); capture_window.protocol("WM_DELETE_WINDOW", on_close); update_display_loop()

    def delete_employee(self):
        selected_item = self.employee_treeview.selection()
        if not selected_item: messagebox.showerror("Erreur", "Veuillez sélectionner un employé."); return
        employee_id = self.employee_treeview.item(selected_item, "values")[0]
        employee_name = self.employee_treeview.item(selected_item, "values")[1]
        if messagebox.askyesno("Confirmation", f"Êtes-vous sûr de vouloir supprimer '{employee_name}' ?"):
            conn = sqlite3.connect(self.DB_FILE); cursor = conn.cursor()
            cursor.execute("DELETE FROM attendance WHERE employee_id = ?", (employee_id,)); cursor.execute("DELETE FROM employees WHERE id = ?", (employee_id,)); conn.commit(); conn.close()
            folder_path = os.path.join(self.FACES_FOLDER, employee_name)
            if os.path.exists(folder_path): shutil.rmtree(folder_path)
            self.populate_employee_list()
            messagebox.showinfo("Succès", f"Employé '{employee_name}' supprimé.\nN'oubliez pas de 'Mettre à Jour'.")

    def update_face_database(self):
        messagebox.showinfo("Mise à jour", "La mise à jour va commencer. Veuillez patienter.")
        self.root.update_idletasks()
        database = {}
        for person_name in os.listdir(self.FACES_FOLDER):
            person_folder_path = os.path.join(self.FACES_FOLDER, person_name)
            if not os.path.isdir(person_folder_path): continue
            database[person_name] = []
            for image_name in os.listdir(person_folder_path):
                image_path = os.path.join(person_folder_path, image_name)
                try:
                    embedding_obj = DeepFace.represent(img_path=image_path, model_name=self.MODEL_NAME, detector_backend=self.DETECTOR_BACKEND, enforce_detection=True)
                    database[person_name].append(embedding_obj[0]["embedding"])
                except: pass
        with open(self.FACE_DB_PKL, "wb") as f: pickle.dump(database, f)
        self.face_database = self.load_face_database()
        messagebox.showinfo("Mise à jour terminée", "La base de reconnaissance a été mise à jour avec succès !")

    def load_face_database(self):
        if os.path.exists(self.FACE_DB_PKL):
            with open(self.FACE_DB_PKL, "rb") as f: return pickle.load(f)
        return {}
    
    def open_history_window(self):
        if self.history_window and self.history_window.winfo_exists(): self.history_window.lift(); return
        self.history_window = tk.Toplevel(self.root); self.history_window.title("Historique des Pointages"); self.history_window.geometry("600x400")
        tree_frame = ttk.Frame(self.history_window); tree_frame.pack(pady=10, padx=10, fill=tk.BOTH, expand=True)
        columns = ('id', 'name', 'timestamp'); self.history_treeview = ttk.Treeview(tree_frame, columns=columns, show='headings')
        self.history_treeview.heading('id', text='ID Pointage'); self.history_treeview.heading('name', text='Nom de l\'Employé'); self.history_treeview.heading('timestamp', text='Heure du Pointage')
        self.history_treeview.column('id', width=80); self.history_treeview.column('name', width=200); self.history_treeview.column('timestamp', width=250)
        self.history_treeview.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=self.history_treeview.yview); self.history_treeview.configure(yscroll=scrollbar.set); scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        refresh_button = ttk.Button(self.history_window, text="Actualiser", command=self.populate_history_treeview); refresh_button.pack(pady=10)
        self.populate_history_treeview()

    def populate_history_treeview(self):
        if not (self.history_window and self.history_window.winfo_exists()): return
        for item in self.history_treeview.get_children(): self.history_treeview.delete(item)
        try:
            conn = sqlite3.connect(self.DB_FILE); cursor = conn.cursor()
            cursor.execute("""SELECT attendance.id, employees.name, attendance.timestamp FROM attendance JOIN employees ON attendance.employee_id = employees.id ORDER BY attendance.timestamp DESC""")
            for record in cursor.fetchall(): self.history_treeview.insert('', tk.END, values=record)
            conn.close()
        except Exception as e: messagebox.showerror("Erreur Base de Données", f"Impossible de lire l'historique: {e}")

    def log_attendance(self, name):
        timestamp = datetime.datetime.now(); conn = sqlite3.connect(self.DB_FILE); cursor = conn.cursor()
        cursor.execute("SELECT id FROM employees WHERE name = ?", (name,))
        result = cursor.fetchone()
        if result:
            employee_id = result[0]
            cursor.execute("INSERT INTO attendance (employee_id, timestamp) VALUES (?, ?)", (employee_id, timestamp.strftime("%Y-%m-%d %H:%M:%S")))
            conn.commit(); log_entry = f"{name} - {timestamp.strftime('%H:%M:%S')}"; self.log_listbox.insert(tk.END, log_entry)
            messagebox.showinfo("Pointage Réussi", f"Pointage enregistré pour {name} à {timestamp.strftime('%H:%M:%S')}")
            self.logged_today.add(name); self.populate_history_treeview()
        conn.close()

    def start_camera(self):
        self.cap = cv2.VideoCapture(0);
        if not self.cap.isOpened(): messagebox.showerror("Erreur Caméra", "Impossible d'accéder à la caméra."); return
        self.camera_is_running = True; self.start_button.config(state=tk.DISABLED); self.stop_button.config(state=tk.NORMAL)
        self.status_label.config(text="Caméra active..."); self.update_frame()

    def stop_camera(self):
        self.camera_is_running = False; self.start_button.config(state=tk.NORMAL); self.stop_button.config(state=tk.DISABLED)
        self.status_label.config(text="Caméra arrêtée");
        if self.cap: self.cap.release()
        self.video_label.config(image='')

    def find_best_match(self, target_embedding):
        best_match_name = "Unknown"; min_distance = float('inf')
        if not self.face_database: return best_match_name, min_distance
        for name, embeddings_list in self.face_database.items():
            for known_embedding in embeddings_list:
                source_rep = np.array(target_embedding, dtype=np.float32); test_rep = np.array(known_embedding, dtype=np.float32)
                a = np.matmul(np.transpose(source_rep), test_rep); b = np.sum(np.multiply(source_rep, source_rep)); c = np.sum(np.multiply(test_rep, test_rep))
                dist = 1 - (a / (np.sqrt(b) * np.sqrt(c)))
                if dist < min_distance: min_distance = dist; best_match_name = name
        return best_match_name, min_distance

    def process_attendance(self, found_person):
        if found_person and found_person not in self.logged_today:
            if found_person == self.current_candidate_name:
                self.total_accumulated_time += time.time() - self.last_seen_time
            else:
                self.current_candidate_name = found_person; self.total_accumulated_time = 0
            self.last_seen_time = time.time()
            if self.total_accumulated_time >= self.ATTENDANCE_TIMER_SECONDS:
                self.log_attendance(self.current_candidate_name); self.current_candidate_name = None; self.total_accumulated_time = 0
        else:
            if self.current_candidate_name and (time.time() - self.last_seen_time > self.GRACE_PERIOD_SECONDS):
                self.status_label.config(text=f"Vérif. annulée pour {self.current_candidate_name}"); self.current_candidate_name = None; self.total_accumulated_time = 0
        if self.current_candidate_name: self.status_label.config(text=f"Vérification: {self.current_candidate_name} ({int(self.total_accumulated_time)}s)")

if __name__ == "__main__":
    if not os.path.exists("database"):
        os.makedirs("database")
    root = ttk.Window(themename="superhero")
    app = AttendanceApp(root)
    root.mainloop()