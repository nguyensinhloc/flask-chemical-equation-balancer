from flask import Flask, request, jsonify
import numpy as np
import numpy.linalg as lin 
import re
import sympy
import itertools

app = Flask(__name__)

def join(l, sep):
  
    out_str = ''
    for i, el in enumerate(l):
        out_str += '{}{}'.format(el, sep)
    return out_str[:-len(sep)]

def removeNums(l):
   return [value for value in l if not value.isdigit()]

def removeBlanks(l):
   return [value for value in l if value != '']
 
def findalphs(string, removenums=False, removeblanks=False):
    if len(string) == 1:
        return list(string)

    separates = re.split('(\d+)', string)
    
    if removenums == True:
        separates = removeNums(separates)
    if removeblanks == True:
        separates = removeBlanks(separates)
    
    return separates


def solveEquation(equation):

    splitter = equation.split(" -> ")
    lhs = splitter[0]
    rhs = splitter[1]

    lsplits = lhs.split(" + ")
    ltermnum = len(lsplits)

    rsplits = rhs.split(" + ")
    rtermnum = len(rsplits)

    vars = np.zeros((1, (rtermnum + ltermnum)))

    allelements = []

    #find how many elements there are
    for term in lsplits:
        alphs = findalphs(term, removeblanks=True, removenums=True)
        allelements = allelements + alphs
    
    uniqueelements = list(set(allelements))
    elementdict = {key: val for val, key in enumerate(uniqueelements)}

    elementamt = len(uniqueelements)
    
    if True:
        lhsvectors = []
        rhsvectors = [] 

        for term in lsplits:

            vec = np.zeros((elementamt, 1))

            combos = findalphs(term, removeblanks=True, removenums=False)

            termelems = [] 
            for i in range(0, len(combos), 2):
                currentelem = combos[i]
                currentamt = int(combos[i + 1])
                termelems.append((currentelem, currentamt))

            for combo in termelems:
                vec[elementdict[combo[0]]] = combo[1]

            lhsvectors.append(vec)

        # now, rhs
        for term in rsplits:

            vec = np.zeros((elementamt, 1))
            combos = findalphs(term, removeblanks=True, removenums=False)
            termelems = [] 

            for i in range(0, len(combos), 2):
                currentelem = combos[i]
                currentamt = int(combos[i + 1])
                termelems.append((currentelem, currentamt))
                
            for combo in termelems:
                vec[elementdict[combo[0]]] = combo[1]

            rhsvectors.append((-1*vec))
            

        
        from sympy import Matrix
        A = Matrix( (np.concatenate((lhsvectors + rhsvectors), axis=1)) )

        b = Matrix( np.zeros((np.shape(A)[0], 1)) )
        
        x = A.nullspace()
        N  = ((np.array(x)).transpose().astype('float'))
        print(N)

        varnum = np.shape(N)[1]

        trynums = list(range(1, 20))
        alltries = trynums*varnum

        combinations = list(itertools.combinations(alltries, varnum))
        
        candidateVectors = []
        for vars in combinations:
            isDec = None
            x = np.asarray(vars).reshape((varnum, 1))
            vector = np.dot(N, x)

            for item in vector:
                item = item[0]

                if not (item).is_integer():
                    isDec = True
                    break
            
            if isDec == True:
                continue 
            else:
                candidateVectors.append(vector)

        
        bestvector = [lin.norm(candidateVectors[0]), candidateVectors[0]]
        for vec in candidateVectors:
            norm = lin.norm(vec)

            if norm < bestvector[0]:
                bestvector[0] = norm
                bestvector[1] = vec
    

    coefficients = (bestvector[1].flatten().astype('int32')).tolist()


    valinbest = 0

    lsplitsstatic = lsplits.copy()

    for term in lsplitsstatic:
        insertterm = lsplits.index(term)
        coefficient =  int(str(coefficients[valinbest]))
        lsplits.insert(insertterm, coefficient)
        valinbest += 1
    
    rsplitsstatic = rsplits.copy()
    for term in rsplitsstatic:
        insertterm = rsplits.index(term)
        coefficient =  int(str(coefficients[valinbest]))
        rsplits.insert(insertterm, coefficient)
        valinbest += 1
    

    lcompounds = []
    for compound in range(0, len(lsplits), 2):
        lcompounds.append(str(lsplits[compound]) + " " + str(lsplits[compound + 1]))

    rcompounds = []
    for compound in range(0, len(rsplits), 2):
        rcompounds.append(str(rsplits[compound]) + " " + str(rsplits[compound + 1]))

    return (join(lcompounds, ' + '), " -> ", join(rcompounds, ' + '))

@app.route('/solve', methods=['POST'])
def solve():
    data = request.get_json()
    equation = data.get('equation')
    if not equation:
        return jsonify({'error': 'No equation provided'}), 400
    try:
        result = solveEquation(equation)
        return jsonify({'result': result}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500
