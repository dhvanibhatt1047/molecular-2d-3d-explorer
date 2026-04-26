from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
import base64
from io import BytesIO
import sqlite3 # New: for database connectivity

# The "Dataset Resolver"
import pubchempy as pcp 

# The "Drawing Engine"
# UPDATED: Core imports for similarity calculation
from rdkit import Chem, DataStructs
# CORRECTION: Simplified imports to ensure Pylance can track them
from rdkit.Chem import Draw, Descriptors, AllChem, Lipinski, Crippen, QED

app = Flask(__name__)
CORS(app)

# Helper function to interact with SQLite
def save_to_db(data):
    conn = sqlite3.connect('molecules.db')
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO history (name, search_query, smiles, weight, logp, qed, h_donors, h_acceptors, image_2d, mol_3d, status)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (data['name'], data['search_query'], data['smiles'], data['weight'], data['logp'], data['qed'], 
          data['h_donors'], data['h_acceptors'], data['image_2d'], data['mol_3d'], data['status']))
    conn.commit()
    conn.close()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/history', methods=['GET'])
def get_history():
    conn = sqlite3.connect('molecules.db')
    cursor = conn.cursor()
    # UPDATED: Select search_query and name for dual display in history
    cursor.execute('SELECT id, search_query, name, smiles FROM history ORDER BY timestamp DESC LIMIT 10')
    rows = cursor.fetchall()
    conn.close()
    return jsonify([{"id": r[0], "search_query": r[1], "iupac": r[2], "smiles": r[3]} for r in rows])

# NEW: Similarity Engine logic restricted to LOCAL DISCOVERY HISTORY ONLY
def get_similar_suggestions(target_smiles):
    suggestions = []
    try:
        target_mol = Chem.MolFromSmiles(target_smiles)
        if not target_mol: return []
        
        # Prepare target molecule for fingerprinting
        Chem.SanitizeMol(target_mol)
        target_fp = AllChem.GetMorganFingerprintAsBitVect(target_mol, 2, nBits=1024)

        # LOCAL HISTORY SEARCH ONLY
        conn = sqlite3.connect('molecules.db')
        cursor = conn.cursor()
        # Fetch all molecules except the current one being analyzed
        cursor.execute('SELECT DISTINCT search_query, smiles, name FROM history WHERE smiles != ?', (target_smiles,))
        history_rows = cursor.fetchall()
        conn.close()

        for s_query, sm, iupac in history_rows:
            mol = Chem.MolFromSmiles(sm)
            if mol:
                Chem.SanitizeMol(mol)
                fp = AllChem.GetMorganFingerprintAsBitVect(mol, 2, nBits=1024)
                
                # FIXED: Using FingerprintSimilarity which is more stable in RDKit
                similarity = DataStructs.FingerprintSimilarity(target_fp, fp)
                
                # Threshold of 30% match to show significant local analogs
                if similarity > 0.3: 
                    suggestions.append({
                        "name": s_query, 
                        "iupac": iupac,
                        "smiles": sm, 
                        "source": "Local History"
                    })

    except Exception as e:
        print(f"Similarity Engine Error: {e}")
        
    return suggestions[:6] # Top 6 local suggestions

# NEW: Reusable function for the new scientific criteria
def get_detailed_explanations(logp, qed_score):
    # LOGP CRITERIA
    if logp < 1: lp_exp = "Highly hydrophilic 💧"
    elif 1 <= logp <= 3: lp_exp = "Ideal balance (drug-like) ✅"
    elif 3 < logp <= 5: lp_exp = "Lipophilic ⚠️"
    else: lp_exp = "Poor (low solubility) ❌"

    # QED CRITERIA
    if qed_score > 0.67: qed_exp = "Highly drug-like 🌟"
    elif 0.34 <= qed_score <= 0.67: qed_exp = "Moderately drug-like ✅"
    else: qed_exp = "Low drug-likeness ❌"
    
    return lp_exp, qed_exp

# --- NEW FEATURE: ADVANCED MOLECULAR CLASSIFIER ---
def get_molecular_insights(mol):
    if not mol: return {}
    
    # 1. Create a copy
    mol_copy = Chem.Mol(mol)
    
    # 2. Pylance-Friendly update
    try:
        mol_copy.UpdatePropertyCache()
    except:
        pass

    # 3. Standard Descriptors
    mw = round(Descriptors.MolWt(mol), 2)
    logp = round(Crippen.MolLogP(mol), 2)
    h_donors = Lipinski.NumHDonors(mol)
    h_acceptors = Lipinski.NumHAcceptors(mol)
    
    lipinski_pass = all([mw <= 500, logp <= 5, h_donors <= 5, h_acceptors <= 10])

    # 4. Classification
    is_aromatic = any(atom.GetIsAromatic() for atom in mol.GetAtoms())
    is_cyclic = mol.GetRingInfo().NumRings() > 0
    
    if is_aromatic: struct_type = "Aromatic 🟢"
    elif is_cyclic: struct_type = "Cyclic 🔵"
    else: struct_type = "Aliphatic ⚪"

    return {
        "lipinski_checks": {
            "mw": mw <= 500,
            "logp": logp <= 5,
            "hbd": h_donors <= 5,
            "hba": h_acceptors <= 10,
            "final": "Pass ✅ (Good candidate)" if lipinski_pass else "Fail ❌"
        },
        "classification": struct_type
    }

# Inside your app.py - ensure these fields are mapped exactly like this:

@app.route('/get_mol/<int:mol_id>', methods=['GET'])
def get_mol(mol_id):
    conn = sqlite3.connect('molecules.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM history WHERE id = ?', (mol_id,))
    r = cursor.fetchone()
    conn.close()
    if r:
        mol = Chem.MolFromSmiles(r[3])
        insights = get_molecular_insights(mol)
        lp_exp, qed_exp = get_detailed_explanations(r[5], r[6])
        return jsonify({
            "success": True, 
            "name": r[1], 
            "search_query": r[2], 
            "smiles_1d": r[3], 
            "weight": r[4],
            "logp": r[5], 
            "qed": r[6], 
            "h_donors": r[7],      # <--- DATABASE MAPPING
            "h_acceptors": r[8],   # <--- DATABASE MAPPING
            "image_2d": r[9], 
            "mol_3d": r[10],
            "status": r[11],
            "logp_explanation": lp_exp,
            "qed_explanation": qed_exp,
            "suggestions": get_similar_suggestions(r[3]), 
            "insights": insights
        })
    return jsonify({"success": False})

def render_structure(mol):
    if not mol: return None
    img = Draw.MolToImage(mol, size=(600, 600))
    buffered = BytesIO()
    img.save(buffered, format="PNG")
    return base64.b64encode(buffered.getvalue()).decode()

@app.route('/analyze', methods=['POST'])
def analyze():
    query = request.json.get('name', '').strip()
    try:
        # --- FEATURE: PRIORITY LOGIC ---
        mol = Chem.MolFromSmiles(query)
        status = "Approximate"
        display_name = query
        smiles = query

        if mol:
            try:
                results = pcp.get_compounds(query, 'smiles')
                if len(results) > 0:
                    status = "Verified"
                    display_name = results[0].iupac_name if results[0].iupac_name else query
            except:
                pass 
        else:
            results = pcp.get_compounds(query, 'name')
            if len(results) > 0:
                compound = results[0]
                smiles = compound.canonical_smiles
                mol = Chem.MolFromSmiles(smiles)
                display_name = compound.iupac_name if compound.iupac_name else query
                status = "Verified"
            else:
                return jsonify({"success": False, "error": f"'{query}' not found in database or invalid SMILES."})

        if mol:
            # Generate Classification insights (Bond counting removed)
            insights = get_molecular_insights(mol)

            mol_3d = Chem.AddHs(mol)
            AllChem.EmbedMolecule(mol_3d, AllChem.ETKDG())
            AllChem.MMFFOptimizeMolecule(mol_3d)
            mol_block_3d = Chem.MolToMolBlock(mol_3d)

            weight = round(Descriptors.MolWt(mol), 2)
            logp = round(Crippen.MolLogP(mol), 2)
            h_donors = Lipinski.NumHDonors(mol)
            h_acceptors = Lipinski.NumHAcceptors(mol)
            qed_score = round(QED.qed(mol), 2)
            
            lp_exp, qed_exp = get_detailed_explanations(logp, qed_score)
            img_b64 = render_structure(mol)
            suggestions = get_similar_suggestions(smiles)

            final_data = {
                "success": True,
                "name": display_name,
                "search_query": query, 
                "smiles": smiles, "smiles_1d": smiles,
                "image_2d": img_b64, "mol_3d": mol_block_3d,
                "weight": weight, "logp": logp,
                "h_donors": h_donors, "h_acceptors": h_acceptors,
                "qed": qed_score,
                "logp_explanation": lp_exp,
                "qed_explanation": qed_exp,
                "status": status,
                "suggestions": suggestions,
                "insights": insights # Insights object remains but without 'bonds'
            }
            save_to_db(final_data)
            return jsonify(final_data)
        else:
            return jsonify({"success": False, "error": "RDKit failed to generate structure."})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

if __name__ == '__main__':
    app.run(debug=True, port=5000)