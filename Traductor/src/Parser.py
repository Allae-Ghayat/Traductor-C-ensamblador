import sys
import os
from AnalizadorSintactico import AnalizadorSintactico, AnalizadorLexico, AST

if __name__ == '__main__':
    analizadorLexico = AnalizadorLexico()
    analizadorSintactico = AnalizadorSintactico()
    debug = False

    if len(sys.argv) != 2:
        print("YOU NEED TO PASS THE PROGRAM FILE TO EXECUTE AS A PARAMETER.")
        print("For example: 'python Parser.py codigoPrueba.c'")
        sys.exit()

    inputFile = sys.argv[1]
    if not os.path.isfile(inputFile):
        print("INPUT FILE DOES NOT EXIST.")
        print("Input file: '{}'".format(inputFile))
        sys.exit()

    with open(inputFile, 'r', encoding="utf8") as exampleFile:
        codeText = exampleFile.read()
        if debug:
            print("TOKENS\n-------------------")
            for token in analizadorLexico.tokenize(codeText):
                print(token)
            print("\nOutput del programa va entre las 2 lineas.\n-------------------")
        
        ast = AST(analizadorSintactico.parse(analizadorLexico.tokenize(codeText)))
        ast.execute(debug)