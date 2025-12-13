from rich import print as rprint
from rich.console import Console
from rich.text import Text

console = Console()

position = 0
char_courant = ''
contenu = ""
table_symboles = []
tokens = []
current_token = ""

def is_letter(c):
    return c.isalpha()

def is_digit(c):
    return c.isdigit()

def lire_fichier(fichier):
    global contenu, char_courant, position
    with open(fichier, 'r', encoding='utf-8') as f:
        contenu = f.read()
    position = 0
    char_courant = contenu[0] if contenu else '\0'

def avancer():
    global position, char_courant
    position += 1
    if position < len(contenu):
        char_courant = contenu[position]
    else:
        char_courant = '\0'

def ignorer_espaces():
    while char_courant in ' \t\n\r':
        avancer()

def add_token(val, typ):
    tokens.append((val, typ))
    if typ == "IDENT" and val not in table_symboles:
        table_symboles.append(val)

def state_0():
    global current_token
    ignorer_espaces()
    if char_courant == '\0':
        return None
    
    current_token = ""
    
    if char_courant == 'p':
        current_token += 'p'
        avancer()
        return state_1
    elif char_courant == 'c':
        current_token += 'c'
        avancer()
        return state_17
    elif char_courant == 'v':
        current_token += 'v'
        avancer()
        return state_26
    elif char_courant == 'd':
        current_token += 'd'
        avancer()
        return state_34
    elif char_courant == 'f':
        current_token += 'f'
        avancer()
        return state_45
    elif char_courant == 's':
        current_token += 's'
        avancer()
        return state_52
    elif char_courant == 'a':
        current_token += 'a'
        avancer()
        return state_60
    elif char_courant == 't':
        current_token += 't'
        avancer()
        return state_70
    elif char_courant == 'r':
        current_token += 'r'
        avancer()
        return state_79
    elif char_courant == 'j':
        current_token += 'j'
        avancer()
        return state_90
    elif char_courant == 'e':
        current_token += 'e'
        avancer()
        return state_98
    elif char_courant == 'o':
        current_token += 'o'
        avancer()
        return state_107
    elif char_courant == 'm':
        current_token += 'm'
        avancer()
        return state_110
    elif is_letter(char_courant):
        current_token += char_courant
        avancer()
        return state_10
    elif is_digit(char_courant):
        current_token += char_courant
        avancer()
        return state_11
    elif char_courant == ':':
        avancer()
        return state_114
    elif char_courant == '<':
        avancer()
        return state_116
    elif char_courant == '>':
        avancer()
        return state_119
    elif char_courant == '=':
        add_token("=", "OPERATEUR_RELATIONNEL")
        avancer()
        return state_0
    elif char_courant in '+-*':
        add_token(char_courant, "OPERATEUR_ARITHMETIQUE")
        avancer()
        return state_0
    elif char_courant in '()':
        add_token(char_courant, "PARENTHESE")
        avancer()
        return state_0
    elif char_courant in '.,;':
        add_token(char_courant, "SEPARATEUR")
        avancer()
        return state_0
    else:
        error_text = Text(f"Erreur: caractère '{char_courant}' non reconnu (position {position})", style="bold red")
        console.print(error_text)
        avancer()
        return state_0


def state_10():
    global current_token
    has_digit = False
    
    while is_digit(char_courant) or is_letter(char_courant):
        if is_digit(char_courant):
            has_digit = True
        current_token += char_courant
        avancer()
    
    # UPDATED: "allantde" is now a single keyword (but will be recognized from "allant de")
    mots_cles = ['programme', 'constante', 'variable', 'debut', 'fin', 'si', 'sinon', 
               'alors', 'tantque', 'repeter', 'jusqua', 'pour', 'faire', 'entier', 
                'reel', 'et', 'ou', 'mod', 'div', 'pas', 'de', 'allantde', 'a']
    
    if current_token in mots_cles:
        add_token(current_token, "MOT_CLE")
    else:
        if has_digit:
            add_token(current_token, "IDENT")
        else:
            error_text = Text(f"Erreur: identifiant '{current_token}' doit contenir au moins un chiffre (position {position})", style="bold red")
            console.print(error_text)
    return state_0

# États nombres
def state_11():
    global current_token
    while is_digit(char_courant):
        current_token += char_courant
        avancer()
    if char_courant == '.':
        current_token += char_courant
        avancer()
        return state_12
    elif char_courant == ',':
        error_text = Text(f"Erreur: virgule non autorisée dans le nombre '{current_token}' (position {position})", style="bold red")
        console.print(error_text)
        return state_0
    add_token(current_token, "NOMBRE")
    return state_0

def state_12():
    global current_token
    if not is_digit(char_courant):
        error_text = Text(f"Erreur: chiffre attendu après '.' dans le nombre '{current_token}' (position {position})", style="bold red")
        console.print(error_text)
        return None
    while is_digit(char_courant):
        current_token += char_courant
        avancer()
    if char_courant == ',':
        error_text = Text(f"Erreur: virgule non autorisée dans le nombre '{current_token}' (position {position})", style="bold red")
        console.print(error_text)
        return state_0
    add_token(current_token, "NOMBRE")
    return state_0

# programme: p→r→o→g→r→a→m→m→e
def state_1():
    global current_token
    if char_courant == 'r':
        current_token += 'r'
        avancer()
        return state_2
    elif char_courant == 'o':
        current_token += 'o'
        avancer()
        return state_6
    elif char_courant == 'a':
        current_token += 'a'
        avancer()
        return state_8
    return state_10()

def state_2():
    global current_token
    if char_courant == 'o':
        current_token += 'o'
        avancer()
        return state_3
    return state_10()

def state_3():
    global current_token
    if char_courant == 'g':
        current_token += 'g'
        avancer()
        return state_4
    return state_10()

def state_4():
    global current_token
    if char_courant == 'r':
        current_token += 'r'
        avancer()
        return state_5
    return state_10()

def state_5():
    global current_token
    if char_courant == 'a':
        current_token += 'a'
        avancer()
        return state_13
    return state_10()

def state_13():
    global current_token
    if char_courant == 'm':
        current_token += 'm'
        avancer()
        return state_14
    return state_10()

def state_14():
    global current_token
    if char_courant == 'm':
        current_token += 'm'
        avancer()
        return state_15
    return state_10()

def state_15():
    global current_token
    if char_courant == 'e':
        current_token += 'e'
        avancer()
        if not (is_letter(char_courant) or is_digit(char_courant)):
            add_token('programme', 'MOT_CLE')
            return state_0
    return state_10()

# pour: p→o→u→r
def state_6():
    global current_token
    if char_courant == 'u':
        current_token += 'u'
        avancer()
        return state_7
    return state_10()

def state_7():
    global current_token
    if char_courant == 'r':
        current_token += 'r'
        avancer()
        if not (is_letter(char_courant) or is_digit(char_courant)):
            add_token('pour', 'MOT_CLE')
            return state_0
    return state_10()

# pas: p→a→s
def state_8():
    global current_token
    if char_courant == 's':
        current_token += 's'
        avancer()
        if not (is_letter(char_courant) or is_digit(char_courant)):
            add_token('pas', 'MOT_CLE')
            return state_0
    return state_10()

# constante: c→o→n→s→t→a→n→t→e
def state_17():
    global current_token
    if char_courant == 'o':
        current_token += 'o'
        avancer()
        return state_18
    return state_10()

def state_18():
    global current_token
    if char_courant == 'n':
        current_token += 'n'
        avancer()
        return state_19
    return state_10()

def state_19():
    global current_token
    if char_courant == 's':
        current_token += 's'
        avancer()
        return state_20
    return state_10()

def state_20():
    global current_token
    if char_courant == 't':
        current_token += 't'
        avancer()
        return state_21
    return state_10()

def state_21():
    global current_token
    if char_courant == 'a':
        current_token += 'a'
        avancer()
        return state_22
    return state_10()

def state_22():
    global current_token
    if char_courant == 'n':
        current_token += 'n'
        avancer()
        return state_23
    return state_10()

def state_23():
    global current_token
    if char_courant == 't':
        current_token += 't'
        avancer()
        return state_24
    return state_10()

def state_24():
    global current_token
    if char_courant == 'e':
        current_token += 'e'
        avancer()
        if not (is_letter(char_courant) or is_digit(char_courant)):
            add_token('constante', 'MOT_CLE')
            return state_0
    return state_10()

# variable: v→a→r→i→a→b→l→e
def state_26():
    global current_token
    if char_courant == 'a':
        current_token += 'a'
        avancer()
        return state_27
    return state_10()

def state_27():
    global current_token
    if char_courant == 'r':
        current_token += 'r'
        avancer()
        return state_28
    return state_10()

def state_28():
    global current_token
    if char_courant == 'i':
        current_token += 'i'
        avancer()
        return state_29
    return state_10()

def state_29():
    global current_token
    if char_courant == 'a':
        current_token += 'a'
        avancer()
        return state_30
    return state_10()

def state_30():
    global current_token
    if char_courant == 'b':
        current_token += 'b'
        avancer()
        return state_31
    return state_10()

def state_31():
    global current_token
    if char_courant == 'l':
        current_token += 'l'
        avancer()
        return state_32
    return state_10()

def state_32():
    global current_token
    if char_courant == 'e':
        current_token += 'e'
        avancer()
        if not (is_letter(char_courant) or is_digit(char_courant)):
            add_token('variable', 'MOT_CLE')
            return state_0
    return state_10()

# debut/de/div: d→...
def state_34():
    global current_token
    if char_courant == 'e':
        current_token += 'e'
        avancer()
        return state_35
    elif char_courant == 'i':
        current_token += 'i'
        avancer()
        return state_42
    return state_10()

def state_35():
    global current_token
    if char_courant == 'b':
        current_token += 'b'
        avancer()
        return state_36
    elif not (is_letter(char_courant) or is_digit(char_courant)):
        add_token('de', 'MOT_CLE')
        return state_0
    return state_10()

def state_36():
    global current_token
    if char_courant == 'u':
        current_token += 'u'
        avancer()
        return state_37
    return state_10()

def state_37():
    global current_token
    if char_courant == 't':
        current_token += 't'
        avancer()
        if not (is_letter(char_courant) or is_digit(char_courant)):
            add_token('debut', 'MOT_CLE')
            return state_0
    return state_10()

def state_42():
    global current_token
    if char_courant == 'v':
        current_token += 'v'
        avancer()
        if not (is_letter(char_courant) or is_digit(char_courant)):
            add_token('div', 'OPERATEUR_ARITHMETIQUE')
            return state_0
    return state_10()

# fin/faire: f→...
def state_45():
    global current_token
    if char_courant == 'i':
        current_token += 'i'
        avancer()
        return state_46
    elif char_courant == 'a':
        current_token += 'a'
        avancer()
        return state_48
    return state_10()

def state_46():
    global current_token
    if char_courant == 'n':
        current_token += 'n'
        avancer()
        if not (is_letter(char_courant) or is_digit(char_courant)):
            add_token('fin', 'MOT_CLE')
            return state_0
    return state_10()

def state_48():
    global current_token
    if char_courant == 'i':
        current_token += 'i'
        avancer()
        return state_49
    return state_10()

def state_49():
    global current_token
    if char_courant == 'r':
        current_token += 'r'
        avancer()
        return state_50
    return state_10()

def state_50():
    global current_token
    if char_courant == 'e':
        current_token += 'e'
        avancer()
        if not (is_letter(char_courant) or is_digit(char_courant)):
            add_token('faire', 'MOT_CLE')
            return state_0
    return state_10()

# si/sinon: s→i/s→i→n→o→n
def state_52():
    global current_token
    if char_courant == 'i':
        current_token += 'i'
        avancer()
        return state_53
    return state_10()

def state_53():
    global current_token
    if char_courant == 'n':
        current_token += 'n'
        avancer()
        return state_54
    elif not (is_letter(char_courant) or is_digit(char_courant)):
        add_token('si', 'MOT_CLE')
        return state_0
    return state_10()

def state_54():
    global current_token
    if char_courant == 'o':
        current_token += 'o'
        avancer()
        return state_55
    return state_10()

def state_55():
    global current_token
    if char_courant == 'n':
        current_token += 'n'
        avancer()
        if not (is_letter(char_courant) or is_digit(char_courant)):
            add_token('sinon', 'MOT_CLE')
            return state_0
    return state_10()

# alors/allant/a: a→...
def state_60():
    global current_token
    if char_courant == 'l':
        current_token += 'l'
        avancer()
        return state_61
    elif not (is_letter(char_courant) or is_digit(char_courant)):
        add_token('a', 'MOT_CLE')
        return state_0
    return state_10()

def state_61():
    global current_token
    if char_courant == 'o':
        current_token += 'o'
        avancer()
        return state_62
    elif char_courant == 'l':
        current_token += 'l'
        avancer()
        return state_68
    return state_10()

def state_62():
    global current_token
    if char_courant == 'r':
        current_token += 'r'
        avancer()
        return state_63
    return state_10()

def state_63():
    global current_token
    if char_courant == 's':
        current_token += 's'
        avancer()
        if not (is_letter(char_courant) or is_digit(char_courant)):
            add_token('alors', 'MOT_CLE')
            return state_0
    return state_10()

# allant: a→l→l→a→n→t
def state_68():
    global current_token
    if char_courant == 'a':
        current_token += 'a'
        avancer()
        return state_69
    return state_10()

def state_69():
    global current_token
    if char_courant == 'n':
        current_token += 'n'
        avancer()
        return state_120
    return state_10()

def state_120():
    global current_token, position, char_courant
    if char_courant == 't':
        current_token += 't'
        avancer()
        if not (is_letter(char_courant) or is_digit(char_courant)):
            # We found "allant", now we need to check if it's followed by "de"
            # Save current state and check for "de" after spaces
            old_position = position
            old_char_courant = char_courant
            
            # Skip any spaces
            while char_courant in ' \t\n\r':
                avancer()
            
            # Check if the next word is "de"
            if char_courant == 'd':
                # Check for "de"
                temp_position = position
                temp_char = char_courant
                temp_token = 'd'
                avancer()
                if char_courant == 'e':
                    temp_token += 'e'
                    avancer()
                    # Check that "de" is not part of a longer word
                    if not (is_letter(char_courant) or is_digit(char_courant)):
                        # We have "allant de" → treat as "allantde"
                        add_token('allantde', 'MOT_CLE')
                        return state_0
                    else:
                        # "de" is part of a longer word, restore and just add "allant"
                        position = old_position
                        char_courant = old_char_courant
                        add_token('allant', 'MOT_CLE')
                        return state_0
                else:
                    # Not "de", restore and just add "allant"
                    position = old_position
                    char_courant = old_char_courant
                    add_token('allant', 'MOT_CLE')
                    return state_0
            else:
                # Not followed by "de", just add "allant"
                position = old_position
                char_courant = old_char_courant
                add_token('allant', 'MOT_CLE')
                return state_0
        else:
            # "allant" is part of a longer word, let state_10 handle it
            return state_10()
    return state_10()

# tantque: t→a→n→t→q→u→e
def state_70():
    global current_token
    if char_courant == 'a':
        current_token += 'a'
        avancer()
        return state_71
    return state_10()

def state_71():
    global current_token
    if char_courant == 'n':
        current_token += 'n'
        avancer()
        return state_72
    return state_10()

def state_72():
    global current_token
    if char_courant == 't':
        current_token += 't'
        avancer()
        return state_73
    return state_10()

def state_73():
    global current_token
    if char_courant == 'q':
        current_token += 'q'
        avancer()
        return state_74
    return state_10()

def state_74():
    global current_token
    if char_courant == 'u':
        current_token += 'u'
        avancer()
        return state_75
    return state_10()

def state_75():
    global current_token
    if char_courant == 'e':
        current_token += 'e'
        avancer()
        if not (is_letter(char_courant) or is_digit(char_courant)):
            add_token('tantque', 'MOT_CLE')
            return state_0
    return state_10()

# repeter/reel: r→e→...
def state_79():
    global current_token
    if char_courant == 'e':
        current_token += 'e'
        avancer()
        return state_80
    return state_10()

def state_80():
    global current_token
    if char_courant == 'p':
        current_token += 'p'
        avancer()
        return state_81
    elif char_courant == 'e':
        current_token += 'e'
        avancer()
        return state_87
    return state_10()

def state_81():
    global current_token
    if char_courant == 'e':
        current_token += 'e'
        avancer()
        return state_82
    return state_10()

def state_82():
    global current_token
    if char_courant == 't':
        current_token += 't'
        avancer()
        return state_83
    return state_10()

def state_83():
    global current_token
    if char_courant == 'e':
        current_token += 'e'
        avancer()
        return state_84
    return state_10()

def state_84():
    global current_token
    if char_courant == 'r':
        current_token += 'r'
        avancer()
        if not (is_letter(char_courant) or is_digit(char_courant)):
            add_token('repeter', 'MOT_CLE')
            return state_0
    return state_10()

def state_87():
    global current_token
    if char_courant == 'l':
        current_token += 'l'
        avancer()
        if not (is_letter(char_courant) or is_digit(char_courant)):
            add_token('reel', 'TYPE')
            return state_0
    return state_10()

# jusqu'a: j→u→s→q→u→'→a
def state_90():
    global current_token
    if char_courant == 'u':
        current_token += 'u'
        avancer()
        return state_91
    return state_10()

def state_91():
    global current_token
    if char_courant == 's':
        current_token += 's'
        avancer()
        return state_92
    return state_10()

def state_92():
    global current_token
    if char_courant == 'q':
        current_token += 'q'
        avancer()
        return state_93
    return state_10()

def state_93():
    global current_token
    if char_courant == 'u':
        current_token += 'u'
        avancer()
        return state_94
    return state_10()

def state_94():
    global current_token
    if char_courant == '\'':
        current_token += '\''
        avancer()
        return state_95
    return state_10()

def state_95():
    global current_token
    if char_courant == 'a':
        current_token += 'a'
        avancer()
        if not (is_letter(char_courant) or is_digit(char_courant)):
            add_token('jusqua', 'MOT_CLE')
            return state_0
    return state_10()

# entier/et: e→...
def state_98():
    global current_token
    if char_courant == 'n':
        current_token += 'n'
        avancer()
        return state_99
    elif char_courant == 't':
        current_token += 't'
        avancer()
        if not (is_letter(char_courant) or is_digit(char_courant)):
            add_token('et', 'OPERATEUR_LOGIQUE')
            return state_0
    return state_10()

def state_99():
    global current_token
    if char_courant == 't':
        current_token += 't'
        avancer()
        return state_100
    return state_10()

def state_100():
    global current_token
    if char_courant == 'i':
        current_token += 'i'
        avancer()
        return state_101
    return state_10()

def state_101():
    global current_token
    if char_courant == 'e':
        current_token += 'e'
        avancer()
        return state_102
    return state_10()

def state_102():
    global current_token
    if char_courant == 'r':
        current_token += 'r'
        avancer()
        if not (is_letter(char_courant) or is_digit(char_courant)):
            add_token('entier', 'TYPE')
            return state_0
    return state_10()

# ou: o→u
def state_107():
    global current_token
    if char_courant == 'u':
        current_token += 'u'
        avancer()
        if not (is_letter(char_courant) or is_digit(char_courant)):
            add_token('ou', 'OPERATEUR_LOGIQUE')
            return state_0
    return state_10()

# mod: m→o→d
def state_110():
    global current_token
    if char_courant == 'o':
        current_token += 'o'
        avancer()
        return state_111
    return state_10()

def state_111():
    global current_token
    if char_courant == 'd':
        current_token += 'd'
        avancer()
        if not (is_letter(char_courant) or is_digit(char_courant)):
            add_token('mod', 'OPERATEUR_ARITHMETIQUE')
            return state_0
    return state_10()

# Opérateur :=
def state_114():
    if char_courant == '=':
        add_token(":=", "OPERATEUR_AFFECTATION")
        avancer()
    else:
        add_token(":", "SEPARATEUR")
    return state_0

# Opérateurs < <= <>
def state_116():
    if char_courant == '=':
        add_token("<=", "OPERATEUR_RELATIONNEL")
        avancer()
    elif char_courant == '>':
        add_token("<>", "OPERATEUR_RELATIONNEL")
        avancer()
    else:
        add_token("<", "OPERATEUR_RELATIONNEL")
    return state_0

# Opérateurs > >=
def state_119():
    if char_courant == '=':
        add_token(">=", "OPERATEUR_RELATIONNEL")
        avancer()
    else:
        add_token(">", "OPERATEUR_RELATIONNEL")
    return state_0


def analyser():
    state = state_0
    while state is not None:
        state = state()
        if char_courant == '\0':
            break

def ecrire_resultats(fichier):
    with open(fichier, 'w', encoding='utf-8') as f:
        f.write("TOKENS:\n")
        for t in tokens:
            f.write(f"{t[0]:20} : {t[1]}\n")
        f.write("\nTABLE SYMBOLES:\n")
        for i, s in enumerate(table_symboles, 1):
            f.write(f"{i}. {s}\n")

if __name__ == "__main__":
    # Keep the test code with "allant de" (with space)
    test = """programme exemple;
constante PI = 3.14;
variable x1, y2 : entier;
variable z3a : reel;
debut
    x1 := 5;
    si x1 > 0 alors
        y2 := x1 + 10
    sinon
        y2 := 0
    fin;
    tantque x1 < 100 faire
        x1 := x1 div 2
        
    fin;
    repeter
        y2 := y2 - 1
    jusqu'a y2 <= 0;
    pour i allant de 1 a 10 pas 2 faire
        z3a := z3a mod 3
    fin
    et 
    ou
    a
    pas
fin."""
    
    with open("test.txt", "w", encoding='utf-8') as f:
        f.write(test)
    
    lire_fichier("test.txt")
    analyser()
    ecrire_resultats("resultats.txt")
    
    # Use Rich for colored output
    rprint("\n[bold cyan]TOKENS:[/bold cyan]")
    for t in tokens:
        rprint(f"[green]{t[0]:20}[/green] : [yellow]{t[1]}[/yellow]")
    
    rprint("\n[bold cyan]TABLE SYMBOLES:[/bold cyan]")
    for i, s in enumerate(table_symboles, 1):
        rprint(f"[blue]{i}.[/blue] [magenta]{s}[/magenta]")