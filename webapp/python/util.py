def printResultDWave(result):
    global aPrintear
    aPrintear = ""
    for variable in result.first.sample:
        aPrintear = aPrintear + "x" + str(
            variable) + "," + str(
            result.first.sample[variable]) + ";"
    aPrintear = aPrintear + "/SUCCESS/" + str(
        result.first.energy)

    return aPrintear

def printQiskit(result):
    global aPrintear, atributo
    aPrintear = ""
    for atributo in result.variables_dict:
        aPrintear = aPrintear + str(
            atributo) + "," + str(
            result.variables_dict[atributo]) + ";"
    aPrintear = aPrintear + "/" + str(
        result.status.name) + "/" + str(
        result.fval)

    return aPrintear