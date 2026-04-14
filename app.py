from flask import Flask, jsonify, request, render_template, redirect, url_for
from flask_cors import CORS
from chemistry_data_file import *

app = Flask(__name__)
CORS(app)


@app.route("/questions/atomic_structure", methods=["GET"] )
def get_atomicons():
    return jsonify({
        "status": "success",
        "total": len(atomic_structure),
        "questions": atomic_structure
    })


@app.route("/questions/electron_config", methods=["GET"] )
def get_electrons():
    return jsonify({
        "status": "success",
        "total": len(electron_config),
        "questions": electron_config
    })


@app.route("/questions/periodic_chemistry", methods=["GET"] )
def get_periodic():
    return jsonify({
        "status": "success",
        "total": len(periodic_chemistry),
        "questions": periodic_chemistry
    })


@app.route("/questions/hybridization", methods=["GET"] )
def get_hybridization():
    return jsonify({
        "status": "success",
        "total": len(hybridization),
        "questions": hybridization

       })


@app.route("/questions/chemical_bonding", methods=["GET"] )
def get_bondings():
    return jsonify({
        "status": "success",
        "total": len(chemical_bonding),
        "questions": chemical_bonding

       })

@app.route("/questions/mole_concept", methods=["GET"] )
def mole():
    return jsonify({
        "status": "success",
        "total": len(mole_concept),
        "questions": mole_concept

       })


@app.route("/questions/state_of_matter", methods=["GET"] )
def getstatequestions():
    return jsonify({
        "status": "success",
        "total": len(state_of_matter),
        "questions": state_of_matter

       })


@app.route("/questions/energy_and_energy_changes", methods=["GET"] )
def get_energy():
    return jsonify({
        "status": "success",
        "total": len(energy_and_energy_changes),
        "questions": energy_and_energy_changes

       })



@app.route("/questions/acids_bases_salts", methods=["GET"] )
def get_acidquestions():
    return jsonify({
        "status": "success",
        "total": len(acids_bases_salts),
        "questions": acids_bases_salts

       })



@app.route("/questions/solubility", methods=["GET"] )
def get_solubibilityquestions():
    return jsonify({
        "status": "success",
        "total": len(solubility),
        "questions": solubility

       })



@app.route("/questions/rate", methods=["GET"] )
def get_ratequestions():
    return jsonify({
        "status": "success",
        "total": len(rate),
        "questions": rate

       })




@app.route("/questions/equilibrium", methods=["GET"] )
def get_equilquestions():
    return jsonify({
        "status": "success",
        "total": len(equilibrium),
        "questions": equilibrium

       })





@app.route("/questions/redox", methods=["GET"] )
def get_redoxquestions():
    return jsonify({
        "status": "success",
        "total": len(redox),
        "questions": redox

       })


@app.route("/questions/electrochemical_cells", methods=["GET"] )
def get_electrochemical():
    return jsonify({
        "status": "success",
        "total": len(electrochemical_cells),
        "questions": electrochemical_cells

       })

@app.route("/questions/electrolysis", methods=["GET"] )
def get_electrolysis():
    return jsonify({
        "status": "success",
        "total": len(electrolysis),
        "questions": electrolysis

       })



@app.route("/questions/chemistry_and_industry", methods=["GET"] )
def get_industryquestions():
    return jsonify({
        "status": "success",
        "total": len(chemistry_and_industry),
        "questions": chemistry_and_industry

       })


@app.route("/questions/alkanes", methods=["GET"] )
def get_alkanesquestions():
    return jsonify({
        "status": "success",
        "total": len(alkanes),
        "questions": alkanes

       })



@app.route("/questions/alkenes", methods=["GET"] )
def get_alkenesquestions():
    return jsonify({
        "status": "success",
        "total": len(alkenes),
        "questions": alkenes

       })



@app.route("/questions/alkynes", methods=["GET"] )
def get_alkynequestions():
    return jsonify({
        "status": "success",
        "total": len(alkynes),
        "questions": alkynes

       })

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/about")
def about():
    return render_template("aboutpage.html")

@app.route("/page3")
def page3():
    return render_template("page3.html")



@app.route("/announcement")
def announcement():
  return render_template('announcement_page.html')


@app.route("/form")
def form():
    return render_template('form_page.html')



@app.route("/contact")
def contact():
  return render_template('contactpage.html')



@app.route("/submit", methods=["POST"])
def submit():
    name = request.form["name"]
    student_class = request.form["class"]
    phone = request.form["phone"]
  
    return redirect(url_for('quiz',
                            name=name,
                            student_class=student_class,
                            phone=phone))


@app.route('/quiz', methods=["POST"])
def quiz():
    name = request.args.get('name')
    student_class = request.args.get('student_class')
    phone = request.args.get('phone')

    return render_template('quiz_screen2.html',
                           name=name,
                           student_class=student_class,
                           phone=phone)

