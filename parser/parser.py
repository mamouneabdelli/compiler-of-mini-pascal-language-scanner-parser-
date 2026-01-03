from rich import print as rprint
from rich.console import Console
from rich.text import Text
from rich.tree import Tree

console = Console()

class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.position = 0
        self.current_token = None
        self.errors = []
        self.parse_tree = Tree("[bold cyan]Programme[/bold cyan]")
        
        if self.tokens:
            self.current_token = self.tokens[0]
    
    def error(self, message):
        """Enregistrer une erreur de syntaxe"""
        error_msg = f"Erreur de syntaxe à la position {self.position}: {message}"
        if self.current_token:
            error_msg += f"\nToken actuel: {self.current_token[0]} ({self.current_token[1]})"
        self.errors.append(error_msg)
        error_text = Text(error_msg, style="bold red")
        console.print(error_text)
    
    def advance(self):
        """Avancer au prochain token"""
        self.position += 1
        if self.position < len(self.tokens):
            self.current_token = self.tokens[self.position]
        else:
            self.current_token = None
    
    def match(self, expected_value=None, expected_type=None):
        """Vérifier si le token actuel correspond à ce qui est attendu"""
        if self.current_token is None:
            self.error(f"Token attendu: {expected_value or expected_type}, mais fin de fichier atteinte")
            return False
        
        value, token_type = self.current_token
        
        if expected_value and value != expected_value:
            self.error(f"Token attendu: '{expected_value}', trouvé: '{value}'")
            return False
        
        if expected_type and token_type != expected_type:
            self.error(f"Type attendu: {expected_type}, trouvé: {token_type}")
            return False
        
        return True
    
    def consume(self, expected_value=None, expected_type=None):
        """Consommer un token s'il correspond à ce qui est attendu"""
        if self.match(expected_value, expected_type):
            token = self.current_token
            self.advance()
            return token
        return None
    
    def parse(self):
        """Point d'entrée principal du parser"""
        rprint("\n[bold cyan]═══════════════════════════════════════[/bold cyan]")
        rprint("[bold cyan]    ANALYSE SYNTAXIQUE COMMENCÉE      [/bold cyan]")
        rprint("[bold cyan]═══════════════════════════════════════[/bold cyan]\n")
        
        success = self.programme()
        
        if success and self.current_token is not None:
            self.error("Tokens supplémentaires après la fin du programme")
            success = False
        
        rprint("\n[bold cyan]═══════════════════════════════════════[/bold cyan]")
        if success and not self.errors:
            rprint("[bold green]  ✓ ANALYSE SYNTAXIQUE RÉUSSIE !      [/bold green]")
        else:
            rprint("[bold red]  ✗ ANALYSE SYNTAXIQUE ÉCHOUÉE        [/bold red]")
            rprint(f"[bold red]    Nombre d'erreurs: {len(self.errors)}[/bold red]")
        rprint("[bold cyan]═══════════════════════════════════════[/bold cyan]\n")
        
        return success and not self.errors
    
    # ==================== RÈGLES DE GRAMMAIRE ====================
    
    def programme(self):
        """programme → programme IDENT ; partie_declaration partie_instruction"""
        rprint("[yellow]→ Analyse du programme[/yellow]")
        
        if not self.consume("programme", "MOT_CLE"):
            return False
        
        if not self.consume(expected_type="IDENT"):
            self.error("Identifiant du programme attendu")
            return False
        
        if not self.consume(";", "SEPARATEUR"):
            return False
        
        if not self.partie_declaration():
            return False
        
        if not self.partie_instruction():
            return False
        
        rprint("[green]✓ Programme analysé avec succès[/green]")
        return True
    
    def partie_declaration(self):
        """partie_declaration → declaration_constante declaration_variable"""
        rprint("[yellow]→ Analyse de la partie déclaration[/yellow]")
        
        # Les déclarations sont optionnelles
        self.declaration_constante()
        self.declaration_variable()
        
        return True
    
    def declaration_constante(self):
        """declaration_constante → constante liste_declaration_constante | ε"""
        if self.current_token and self.current_token[0] == "constante":
            rprint("[yellow]→ Analyse des constantes[/yellow]")
            self.consume("constante", "MOT_CLE")
            return self.liste_declaration_constante()
        return True
    
    def liste_declaration_constante(self):
        """liste_declaration_constante → IDENT = NOMBRE ; | IDENT = NOMBRE ; liste_declaration_constante"""
        if not self.consume(expected_type="IDENT"):
            self.error("Identifiant de constante attendu")
            return False
        
        if not self.consume("=", "OPERATEUR_RELATIONNEL"):
            return False
        
        if not self.consume(expected_type="NOMBRE"):
            self.error("Valeur numérique attendue")
            return False
        
        if not self.consume(";", "SEPARATEUR"):
            return False
        
        # Vérifier s'il y a d'autres constantes
        if self.current_token and self.current_token[1] == "IDENT":
            # Regarder en avant pour voir si c'est une autre déclaration de constante
            if self.position + 1 < len(self.tokens) and self.tokens[self.position + 1][0] == "=":
                return self.liste_declaration_constante()
        
        return True
    
    def declaration_variable(self):
        """declaration_variable → variable liste_declaration_variable | ε"""
        if self.current_token and self.current_token[0] == "variable":
            rprint("[yellow]→ Analyse des variables[/yellow]")
            self.consume("variable", "MOT_CLE")
            return self.liste_declaration_variable()
        return True
    
    def liste_declaration_variable(self):
        """liste_declaration_variable → liste_ident : type ; | liste_ident : type ; liste_declaration_variable"""
        if not self.liste_ident():
            return False
        
        if not self.consume(":", "SEPARATEUR"):
            return False
        
        if not self.type():
            return False
        
        if not self.consume(";", "SEPARATEUR"):
            return False
        
        # Vérifier s'il y a d'autres variables
        if self.current_token and self.current_token[0] == "variable":
            self.consume("variable", "MOT_CLE")
            return self.liste_declaration_variable()
        elif self.current_token and self.current_token[1] == "IDENT":
            # Regarder en avant pour voir si c'est une autre déclaration de variable
            if self.position + 1 < len(self.tokens) and self.tokens[self.position + 1][0] in [",", ":"]:
                return self.liste_declaration_variable()
        
        return True
    
    def liste_ident(self):
        """liste_ident → IDENT | IDENT , liste_ident"""
        if not self.consume(expected_type="IDENT"):
            self.error("Identifiant attendu")
            return False
        
        if self.current_token and self.current_token[0] == ",":
            self.consume(",", "SEPARATEUR")
            return self.liste_ident()
        
        return True
    
    def type(self):
        """type → entier | reel"""
        if self.current_token and self.current_token[1] == "TYPE":
            self.consume(expected_type="TYPE")
            return True
        
        self.error("Type attendu (entier ou reel)")
        return False
    
    def partie_instruction(self):
        """partie_instruction → debut liste_instruction fin"""
        rprint("[yellow]→ Analyse de la partie instruction[/yellow]")
        
        if not self.consume("debut", "MOT_CLE"):
            return False
        
        if not self.liste_instruction():
            return False
        
        if not self.consume("fin", "MOT_CLE"):
            return False
        
        # Le point final est optionnel
        if self.current_token and self.current_token[0] == ".":
            self.consume(".", "SEPARATEUR")
        
        return True
    
    def liste_instruction(self):
        """liste_instruction → instruction | instruction ; liste_instruction"""
        if not self.instruction():
            return False
        
        # Vérifier s'il y a un point-virgule suivi d'une autre instruction
        if self.current_token and self.current_token[0] == ";":
            self.consume(";", "SEPARATEUR")
            # Vérifier si ce n'est pas la fin
            if self.current_token and self.current_token[0] != "fin":
                return self.liste_instruction()
        
        return True
    
    def instruction(self):
        """instruction → affectation | conditionnelle | iterative"""
        rprint("[yellow]→ Analyse d'une instruction[/yellow]")
        
        if self.current_token is None:
            return True
        
        value, token_type = self.current_token
        
        # Affectation
        if token_type == "IDENT":
            return self.affectation()
        
        # Conditionnelle
        elif value == "si":
            return self.conditionnelle()
        
        # Iterative
        elif value in ["tantque", "repeter", "pour"]:
            return self.iterative()
        
        # Instruction vide (pour gérer les cas de fin)
        elif value == "fin":
            return True
        
        self.error(f"Instruction attendue, trouvé: {value}")
        return False
    
    def affectation(self):
        """affectation → IDENT := expression"""
        rprint("[yellow]  → Affectation[/yellow]")
        
        if not self.consume(expected_type="IDENT"):
            return False
        
        if not self.consume(":=", "OPERATEUR_AFFECTATION"):
            return False
        
        return self.expression()
    
    def conditionnelle(self):
        """conditionnelle → si condition alors liste_instruction [sinon liste_instruction] fin"""
        rprint("[yellow]  → Instruction conditionnelle[/yellow]")
        
        if not self.consume("si", "MOT_CLE"):
            return False
        
        if not self.condition():
            return False
        
        if not self.consume("alors", "MOT_CLE"):
            return False
        
        if not self.liste_instruction():
            return False
        
        # Partie sinon optionnelle
        if self.current_token and self.current_token[0] == "sinon":
            self.consume("sinon", "MOT_CLE")
            if not self.liste_instruction():
                return False
        
        if not self.consume("fin", "MOT_CLE"):
            return False
        
        return True
    
    def iterative(self):
        """iterative → boucle_tantque | boucle_repeter | boucle_pour"""
        if self.current_token and self.current_token[0] == "tantque":
            return self.boucle_tantque()
        elif self.current_token and self.current_token[0] == "repeter":
            return self.boucle_repeter()
        elif self.current_token and self.current_token[0] == "pour":
            return self.boucle_pour()
        return False
    
    def boucle_tantque(self):
        """boucle_tantque → tantque condition faire liste_instruction fin"""
        rprint("[yellow]  → Boucle tantque[/yellow]")
        
        if not self.consume("tantque", "MOT_CLE"):
            return False
        
        if not self.condition():
            return False
        
        if not self.consume("faire", "MOT_CLE"):
            return False
        
        if not self.liste_instruction():
            return False
        
        if not self.consume("fin", "MOT_CLE"):
            return False
        
        return True
    
    def boucle_repeter(self):
        """boucle_repeter → repeter liste_instruction jusqua condition"""
        rprint("[yellow]  → Boucle repeter[/yellow]")
        
        if not self.consume("repeter", "MOT_CLE"):
            return False
        
        if not self.liste_instruction():
            return False
        
        if not self.consume("jusqua", "MOT_CLE"):
            return False
        
        if not self.condition():
            return False
        
        # Point-virgule optionnel
        if self.current_token and self.current_token[0] == ";":
            self.consume(";", "SEPARATEUR")
        
        return True
    
    def boucle_pour(self):
        """boucle_pour → pour IDENT allantde expression a expression [pas expression] faire liste_instruction fin"""
        rprint("[yellow]  → Boucle pour[/yellow]")
        
        if not self.consume("pour", "MOT_CLE"):
            return False
        
        if not self.consume(expected_type="IDENT"):
            self.error("Identifiant de variable de boucle attendu")
            return False
        
        # "allant de" peut être écrit en un ou deux mots dans le scanner
        if self.current_token and self.current_token[0] == "allantde":
            self.consume("allantde", "MOT_CLE")
        else:
            # Sinon, chercher "de" directement
            if not self.consume("de", "MOT_CLE"):
                self.error("'allant de' ou 'de' attendu après l'identifiant")
                return False
        
        if not self.expression():
            return False
        
        if not self.consume("a", "MOT_CLE"):
            return False
        
        if not self.expression():
            return False
        
        # Partie pas optionnelle
        if self.current_token and self.current_token[0] == "pas":
            self.consume("pas", "MOT_CLE")
            if not self.expression():
                return False
        
        if not self.consume("faire", "MOT_CLE"):
            return False
        
        if not self.liste_instruction():
            return False
        
        if not self.consume("fin", "MOT_CLE"):
            return False
        
        return True
    
    def condition(self):
        """condition → expression operateur_relationnel expression"""
        rprint("[yellow]  → Condition[/yellow]")
        
        if not self.expression():
            return False
        
        if not self.consume(expected_type="OPERATEUR_RELATIONNEL"):
            self.error("Opérateur relationnel attendu")
            return False
        
        if not self.expression():
            return False
        
        return True
    
    def expression(self):
        """expression → terme | terme operateur_additif expression"""
        rprint("[yellow]  → Expression[/yellow]")
        
        if not self.terme():
            return False
        
        # Vérifier les opérateurs additifs (+, -, ou)
        while self.current_token:
            value, token_type = self.current_token
            if token_type == "OPERATEUR_ARITHMETIQUE" and value in ["+", "-"]:
                self.consume(expected_type="OPERATEUR_ARITHMETIQUE")
                if not self.terme():
                    return False
            elif token_type == "OPERATEUR_LOGIQUE" and value == "ou":
                self.consume(expected_type="OPERATEUR_LOGIQUE")
                if not self.terme():
                    return False
            else:
                break
        
        return True
    
    def terme(self):
        """terme → facteur | facteur operateur_multiplicatif terme"""
        if not self.facteur():
            return False
        
        # Vérifier les opérateurs multiplicatifs (*, div, mod, et)
        while self.current_token:
            value, token_type = self.current_token
            if token_type == "OPERATEUR_ARITHMETIQUE" and value in ["*", "div", "mod"]:
                self.consume(expected_type="OPERATEUR_ARITHMETIQUE")
                if not self.facteur():
                    return False
            elif token_type == "OPERATEUR_LOGIQUE" and value == "et":
                self.consume(expected_type="OPERATEUR_LOGIQUE")
                if not self.facteur():
                    return False
            else:
                break
        
        return True
    
    def facteur(self):
        """facteur → IDENT | NOMBRE | ( expression )"""
        if self.current_token is None:
            self.error("Facteur attendu")
            return False
        
        value, token_type = self.current_token
        
        if token_type == "IDENT":
            self.consume(expected_type="IDENT")
            return True
        
        elif token_type == "NOMBRE":
            self.consume(expected_type="NOMBRE")
            return True
        
        elif value == "(":
            self.consume("(", "PARENTHESE")
            if not self.expression():
                return False
            if not self.consume(")", "PARENTHESE"):
                return False
            return True
        
        self.error(f"Facteur attendu (IDENT, NOMBRE ou expression entre parenthèses), trouvé: {value}")
        return False


def lire_tokens(fichier):
    """Lire les tokens depuis le fichier de résultats du scanner"""
    tokens = []
    try:
        with open(fichier, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            
        lecture_tokens = False
        for line in lines:
            line = line.strip()
            
            if line == "TOKENS:":
                lecture_tokens = True
                continue
            
            if line == "TABLE SYMBOLES:":
                lecture_tokens = False
                break
            
            if lecture_tokens and line and ':' in line:
                # Format: "value : type"
                parts = line.split(':', 1)
                if len(parts) == 2:
                    value = parts[0].strip()
                    token_type = parts[1].strip()
                    tokens.append((value, token_type))
        
        return tokens
    
    except FileNotFoundError:
        error_text = Text(f"Erreur: fichier '{fichier}' non trouvé", style="bold red")
        console.print(error_text)
        return []
    except Exception as e:
        error_text = Text(f"Erreur lors de la lecture du fichier: {e}", style="bold red")
        console.print(error_text)
        return []


def ecrire_rapport_parsing(fichier, parser, success):
    """Écrire le rapport d'analyse syntaxique dans un fichier"""
    with open(fichier, 'w', encoding='utf-8') as f:
        f.write("═" * 60 + "\n")
        f.write("          RAPPORT D'ANALYSE SYNTAXIQUE\n")
        f.write("═" * 60 + "\n\n")
        
        if success:
            f.write("✓ RÉSULTAT: ANALYSE RÉUSSIE\n\n")
            f.write("Le programme est syntaxiquement correct.\n")
            f.write("Toutes les règles de grammaire sont respectées.\n")
        else:
            f.write("✗ RÉSULTAT: ANALYSE ÉCHOUÉE\n\n")
            f.write(f"Nombre d'erreurs détectées: {len(parser.errors)}\n\n")
            
            if parser.errors:
                f.write("ERREURS DÉTECTÉES:\n")
                f.write("-" * 60 + "\n")
                for i, error in enumerate(parser.errors, 1):
                    f.write(f"\n{i}. {error}\n")
        
        f.write("\n" + "═" * 60 + "\n")
        f.write(f"Tokens analysés: {len(parser.tokens)}\n")
        f.write(f"Position finale: {parser.position}\n")
        f.write("═" * 60 + "\n")


if __name__ == "__main__":
    # Lire les tokens depuis le fichier de résultats du scanner
    tokens = lire_tokens("resultats.txt")
    
    if not tokens:
        error_text = Text("Aucun token trouvé. Veuillez d'abord exécuter le scanner.", style="bold red")
        console.print(error_text)
    else:
        rprint(f"\n[bold cyan]Nombre de tokens lus: {len(tokens)}[/bold cyan]")
        
        # Créer le parser et analyser
        parser = Parser(tokens)
        success = parser.parse()
        
        # Écrire le rapport
        ecrire_rapport_parsing("rapport_parsing.txt", parser, success)
        
        rprint(f"\n[bold cyan]Rapport d'analyse écrit dans 'rapport_parsing.txt'[/bold cyan]")