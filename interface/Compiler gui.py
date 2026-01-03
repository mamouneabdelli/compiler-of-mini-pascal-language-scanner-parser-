"""
Mini Pascal Compiler - GUI Interface
Created with PyQt5
"""

import sys
import os
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QTextEdit, QPlainTextEdit, QPushButton, QLabel, QFileDialog, QMessageBox,
    QSplitter, QTabWidget, QStatusBar, QMenuBar, QMenu, QAction,
    QToolBar, QFrame
)
from PyQt5.QtCore import Qt, QRect, QSize, pyqtSignal
from PyQt5.QtGui import (
    QFont, QColor, QPainter, QTextFormat, QSyntaxHighlighter,
    QTextCharFormat, QIcon, QPalette
)
import re

# Import scanner and parser modules
import scaner_last as scanner
import parser as parser_module


class MiniPascalHighlighter(QSyntaxHighlighter):
    """Syntax highlighter for Mini Pascal language"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # Define highlighting rules
        self.highlighting_rules = []
        
        # Keywords format
        keyword_format = QTextCharFormat()
        keyword_format.setForeground(QColor("#569CD6"))
        keyword_format.setFontWeight(QFont.Bold)
        
        keywords = [
            'programme', 'constante', 'variable', 'debut', 'fin',
            'si', 'alors', 'sinon', 'tantque', 'faire', 'repeter',
            'jusqua', 'pour', 'allantde', 'a', 'pas', 'de'
        ]
        
        for word in keywords:
            pattern = r'\b' + word + r'\b'
            self.highlighting_rules.append((re.compile(pattern), keyword_format))
        
        # Types format
        type_format = QTextCharFormat()
        type_format.setForeground(QColor("#4EC9B0"))
        type_format.setFontWeight(QFont.Bold)
        
        types = ['entier', 'reel']
        for word in types:
            pattern = r'\b' + word + r'\b'
            self.highlighting_rules.append((re.compile(pattern), type_format))
        
        # Operators format
        operator_format = QTextCharFormat()
        operator_format.setForeground(QColor("#D4D4D4"))
        
        operators = [
            ':=', '<=', '>=', '<>', '=', '<', '>',
            r'\+', '-', r'\*', 'div', 'mod', 'et', 'ou'
        ]
        
        for op in operators:
            pattern = r'\b' + op + r'\b' if op.isalpha() else op
            self.highlighting_rules.append((re.compile(pattern), operator_format))
        
        # Numbers format
        number_format = QTextCharFormat()
        number_format.setForeground(QColor("#B5CEA8"))
        self.highlighting_rules.append((re.compile(r'\b\d+\.?\d*\b'), number_format))
        
        # Identifiers format
        identifier_format = QTextCharFormat()
        identifier_format.setForeground(QColor("#9CDCFE"))
        self.highlighting_rules.append((re.compile(r'\b[a-zA-Z][a-zA-Z0-9]*\b'), identifier_format))
        
        # Comments format (if any)
        comment_format = QTextCharFormat()
        comment_format.setForeground(QColor("#6A9955"))
        comment_format.setFontItalic(True)
        self.highlighting_rules.append((re.compile(r'//.*'), comment_format))
    
    def highlightBlock(self, text):
        """Apply syntax highlighting to a block of text"""
        for pattern, format in self.highlighting_rules:
            for match in pattern.finditer(text):
                start = match.start()
                length = match.end() - start
                self.setFormat(start, length, format)


class LineNumberArea(QWidget):
    """Widget for displaying line numbers"""
    
    def __init__(self, editor):
        super().__init__(editor)
        self.code_editor = editor
    
    def sizeHint(self):
        return QSize(self.code_editor.line_number_area_width(), 0)
    
    def paintEvent(self, event):
        self.code_editor.line_number_area_paint_event(event)


class CodeEditor(QPlainTextEdit):
    """Code editor with line numbers"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # Set font
        font = QFont("Consolas", 11)
        font.setStyleHint(QFont.Monospace)
        self.setFont(font)
        
        # Create line number area
        self.line_number_area = LineNumberArea(self)
        
        # Connect signals
        self.blockCountChanged.connect(self.update_line_number_area_width)
        self.updateRequest.connect(self.update_line_number_area)
        
        self.update_line_number_area_width(0)
        
        # Set colors for dark theme
        self.setStyleSheet("""
            QPlainTextEdit {
                background-color: #1E1E1E;
                color: #D4D4D4;
                border: 1px solid #3C3C3C;
                selection-background-color: #264F78;
            }
        """)
    
    def line_number_area_width(self):
        """Calculate width needed for line numbers"""
        digits = len(str(max(1, self.blockCount())))
        space = 10 + self.fontMetrics().horizontalAdvance('9') * digits
        return space
    
    def update_line_number_area_width(self, _):
        """Update the width of line number area"""
        self.setViewportMargins(self.line_number_area_width(), 0, 0, 0)
    
    def update_line_number_area(self, rect, dy):
        """Update line number area on scroll"""
        if dy:
            self.line_number_area.scroll(0, dy)
        else:
            self.line_number_area.update(0, rect.y(), 
                                        self.line_number_area.width(), 
                                        rect.height())
        
        if rect.contains(self.viewport().rect()):
            self.update_line_number_area_width(0)
    
    def resizeEvent(self, event):
        """Handle resize event"""
        super().resizeEvent(event)
        
        cr = self.contentsRect()
        self.line_number_area.setGeometry(
            QRect(cr.left(), cr.top(), 
                  self.line_number_area_width(), cr.height())
        )
    
    def line_number_area_paint_event(self, event):
        """Paint line numbers"""
        painter = QPainter(self.line_number_area)
        painter.fillRect(event.rect(), QColor("#252526"))
        
        block = self.firstVisibleBlock()
        block_number = block.blockNumber()
        top = self.blockBoundingGeometry(block).translated(self.contentOffset()).top()
        bottom = top + self.blockBoundingRect(block).height()
        
        while block.isValid() and top <= event.rect().bottom():
            if block.isVisible() and bottom >= event.rect().top():
                number = str(block_number + 1)
                painter.setPen(QColor("#858585"))
                painter.drawText(0, int(top), self.line_number_area.width() - 5, 
                               self.fontMetrics().height(),
                               Qt.AlignRight, number)
            
            block = block.next()
            top = bottom
            bottom = top + self.blockBoundingRect(block).height()
            block_number += 1


class CompilerGUI(QMainWindow):
    """Main window for the Mini Pascal Compiler"""
    
    def __init__(self):
        super().__init__()
        self.current_file = None
        self.init_ui()
    
    def init_ui(self):
        """Initialize the user interface"""
        self.setWindowTitle("Mini Pascal Compiler")
        self.setGeometry(100, 100, 1400, 900)
        
        # Create central widget and main layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        
        # Create main splitter (need to create editor first)
        splitter = QSplitter(Qt.Horizontal)
        
        # Left side - Code Editor
        editor_widget = QWidget()
        editor_layout = QVBoxLayout(editor_widget)
        editor_layout.setContentsMargins(5, 5, 5, 5)
        
        # Editor label
        editor_label = QLabel("📝 Code Editor")
        editor_label.setFont(QFont("Segoe UI", 10, QFont.Bold))
        editor_label.setStyleSheet("color: #569CD6; padding: 5px;")
        editor_layout.addWidget(editor_label)
        
        # Code editor
        self.code_editor = CodeEditor()
        self.highlighter = MiniPascalHighlighter(self.code_editor.document())
        editor_layout.addWidget(self.code_editor)
        
        # Button panel
        button_layout = QHBoxLayout()
        
        self.run_btn = QPushButton("▶ Compile & Run")
        self.run_btn.setStyleSheet("""
            QPushButton {
                background-color: #0E639C;
                color: white;
                border: none;
                padding: 8px 20px;
                font-weight: bold;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #1177BB;
            }
            QPushButton:pressed {
                background-color: #0D5A8F;
            }
        """)
        self.run_btn.clicked.connect(self.run_compiler)
        
        self.clear_btn = QPushButton("🗑 Clear")
        self.clear_btn.setStyleSheet("""
            QPushButton {
                background-color: #3C3C3C;
                color: white;
                border: none;
                padding: 8px 20px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #4C4C4C;
            }
        """)
        self.clear_btn.clicked.connect(self.clear_editor)
        
        button_layout.addWidget(self.run_btn)
        button_layout.addWidget(self.clear_btn)
        button_layout.addStretch()
        
        editor_layout.addLayout(button_layout)
        
        # Right side - Output Tabs
        self.output_tabs = QTabWidget()
        self.output_tabs.setStyleSheet("""
            QTabWidget::pane {
                border: 1px solid #3C3C3C;
                background-color: #1E1E1E;
            }
            QTabBar::tab {
                background-color: #2D2D30;
                color: #D4D4D4;
                padding: 8px 20px;
                border: 1px solid #3C3C3C;
            }
            QTabBar::tab:selected {
                background-color: #1E1E1E;
                border-bottom: 2px solid #0E639C;
            }
        """)
        
        # Tokens tab
        self.tokens_output = QTextEdit()
        self.tokens_output.setReadOnly(True)
        self.tokens_output.setFont(QFont("Consolas", 10))
        self.tokens_output.setStyleSheet("""
            background-color: #1E1E1E;
            color: #D4D4D4;
            border: none;
        """)
        self.output_tabs.addTab(self.tokens_output, "🔤 Tokens")
        
        # Symbols tab
        self.symbols_output = QTextEdit()
        self.symbols_output.setReadOnly(True)
        self.symbols_output.setFont(QFont("Consolas", 10))
        self.symbols_output.setStyleSheet("""
            background-color: #1E1E1E;
            color: #D4D4D4;
            border: none;
        """)
        self.output_tabs.addTab(self.symbols_output, "📋 Symbol Table")
        
        # Parser output tab
        self.parser_output = QTextEdit()
        self.parser_output.setReadOnly(True)
        self.parser_output.setFont(QFont("Consolas", 10))
        self.parser_output.setStyleSheet("""
            background-color: #1E1E1E;
            color: #D4D4D4;
            border: none;
        """)
        self.output_tabs.addTab(self.parser_output, "🔍 Parser Results")
        
        # Console tab
        self.console_output = QTextEdit()
        self.console_output.setReadOnly(True)
        self.console_output.setFont(QFont("Consolas", 10))
        self.console_output.setStyleSheet("""
            background-color: #1E1E1E;
            color: #D4D4D4;
            border: none;
        """)
        self.output_tabs.addTab(self.console_output, "💻 Console")
        
        # Add widgets to splitter
        splitter.addWidget(editor_widget)
        splitter.addWidget(self.output_tabs)
        splitter.setSizes([700, 700])
        
        main_layout.addWidget(splitter)
        
        # Create menu bar and toolbar AFTER editor is created
        self.create_menu_bar()
        self.create_toolbar()
        
        # Status bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Ready")
        
        # Set dark theme
        self.set_dark_theme()
        
        # Load example code
        self.load_example_code()
    
    def create_menu_bar(self):
        """Create menu bar"""
        menubar = self.menuBar()
        
        # File menu
        file_menu = menubar.addMenu("File")
        
        new_action = QAction("New", self)
        new_action.setShortcut("Ctrl+N")
        new_action.triggered.connect(self.new_file)
        file_menu.addAction(new_action)
        
        open_action = QAction("Open", self)
        open_action.setShortcut("Ctrl+O")
        open_action.triggered.connect(self.open_file)
        file_menu.addAction(open_action)
        
        save_action = QAction("Save", self)
        save_action.setShortcut("Ctrl+S")
        save_action.triggered.connect(self.save_file)
        file_menu.addAction(save_action)
        
        save_as_action = QAction("Save As...", self)
        save_as_action.setShortcut("Ctrl+Shift+S")
        save_as_action.triggered.connect(self.save_file_as)
        file_menu.addAction(save_as_action)
        
        file_menu.addSeparator()
        
        exit_action = QAction("Exit", self)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # Edit menu
        edit_menu = menubar.addMenu("Edit")
        
        undo_action = QAction("Undo", self)
        undo_action.setShortcut("Ctrl+Z")
        undo_action.triggered.connect(self.code_editor.undo)
        edit_menu.addAction(undo_action)
        
        redo_action = QAction("Redo", self)
        redo_action.setShortcut("Ctrl+Y")
        redo_action.triggered.connect(self.code_editor.redo)
        edit_menu.addAction(redo_action)
        
        edit_menu.addSeparator()
        
        cut_action = QAction("Cut", self)
        cut_action.setShortcut("Ctrl+X")
        cut_action.triggered.connect(self.code_editor.cut)
        edit_menu.addAction(cut_action)
        
        copy_action = QAction("Copy", self)
        copy_action.setShortcut("Ctrl+C")
        copy_action.triggered.connect(self.code_editor.copy)
        edit_menu.addAction(copy_action)
        
        paste_action = QAction("Paste", self)
        paste_action.setShortcut("Ctrl+V")
        paste_action.triggered.connect(self.code_editor.paste)
        edit_menu.addAction(paste_action)
        
        # Run menu
        run_menu = menubar.addMenu("Run")
        
        compile_action = QAction("Compile & Run", self)
        compile_action.setShortcut("F5")
        compile_action.triggered.connect(self.run_compiler)
        run_menu.addAction(compile_action)
        
        # Help menu
        help_menu = menubar.addMenu("Help")
        
        about_action = QAction("About", self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)
    
    def create_toolbar(self):
        """Create toolbar"""
        toolbar = QToolBar()
        toolbar.setStyleSheet("""
            QToolBar {
                background-color: #2D2D30;
                border-bottom: 1px solid #3C3C3C;
                spacing: 5px;
                padding: 5px;
            }
            QToolButton {
                background-color: transparent;
                color: white;
                border: none;
                padding: 5px;
            }
            QToolButton:hover {
                background-color: #3E3E42;
            }
        """)
        self.addToolBar(toolbar)
        
        # Add actions to toolbar
        new_action = QAction("📄 New", self)
        new_action.triggered.connect(self.new_file)
        toolbar.addAction(new_action)
        
        open_action = QAction("📁 Open", self)
        open_action.triggered.connect(self.open_file)
        toolbar.addAction(open_action)
        
        save_action = QAction("💾 Save", self)
        save_action.triggered.connect(self.save_file)
        toolbar.addAction(save_action)
        
        toolbar.addSeparator()
        
        run_action = QAction("▶ Run", self)
        run_action.triggered.connect(self.run_compiler)
        toolbar.addAction(run_action)
    
    def set_dark_theme(self):
        """Set dark theme for the application"""
        self.setStyleSheet("""
            QMainWindow {
                background-color: #1E1E1E;
            }
            QMenuBar {
                background-color: #2D2D30;
                color: #D4D4D4;
                border-bottom: 1px solid #3C3C3C;
            }
            QMenuBar::item:selected {
                background-color: #3E3E42;
            }
            QMenu {
                background-color: #2D2D30;
                color: #D4D4D4;
                border: 1px solid #3C3C3C;
            }
            QMenu::item:selected {
                background-color: #0E639C;
            }
            QStatusBar {
                background-color: #007ACC;
                color: white;
            }
        """)
    
    def load_example_code(self):
        """Load example Mini Pascal code"""
        example = """programme exemple;
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
    jusqua y2 <= 0;
    pour i allantde 1 a 10 pas 2 faire
        z3a := z3a mod 3
    fin
fin."""
        self.code_editor.setPlainText(example)
    
    def run_compiler(self):
        """Run the scanner and parser"""
        try:
            # Clear previous outputs
            self.tokens_output.clear()
            self.symbols_output.clear()
            self.parser_output.clear()
            self.console_output.clear()
            
            self.console_output.append("🔄 Starting compilation...\n")
            self.status_bar.showMessage("Compiling...")
            
            # Get code from editor
            code = self.code_editor.toPlainText()
            
            if not code.strip():
                self.console_output.append("❌ Error: No code to compile!")
                self.status_bar.showMessage("Error: No code")
                return
            
            # Save code to temporary file
            temp_file = "temp_code.txt"
            with open(temp_file, 'w', encoding='utf-8') as f:
                f.write(code)
            
            # Reset scanner state
            scanner.tokens = []
            scanner.table_symboles = []
            scanner.position = 0
            scanner.char_courant = ''
            scanner.contenu = ""
            scanner.current_token = ""
            
            # Run scanner
            self.console_output.append("📊 Phase 1: Lexical Analysis (Scanner)...\n")
            scanner.lire_fichier(temp_file)
            scanner.analyser()
            
            # Display tokens
            self.console_output.append(f"✅ Scanner completed: {len(scanner.tokens)} tokens found\n")
            
            tokens_text = "TOKENS:\n" + "="*60 + "\n"
            for token_val, token_type in scanner.tokens:
                tokens_text += f"{token_val:20} : {token_type}\n"
            self.tokens_output.setPlainText(tokens_text)
            
            # Display symbol table
            symbols_text = "SYMBOL TABLE:\n" + "="*60 + "\n"
            for i, symbol in enumerate(scanner.table_symboles, 1):
                symbols_text += f"{i}. {symbol}\n"
            self.symbols_output.setPlainText(symbols_text)
            
            # Run parser
            self.console_output.append("🔍 Phase 2: Syntax Analysis (Parser)...\n")
            
            parser = parser_module.Parser(scanner.tokens)
            success = parser.parse()
            
            # Display parser results
            parser_text = "PARSER RESULTS:\n" + "="*60 + "\n\n"
            
            if success:
                parser_text += "✅ SYNTAX ANALYSIS: SUCCESS\n\n"
                parser_text += "The program is syntactically correct.\n"
                parser_text += "All grammar rules are respected.\n"
                self.console_output.append("✅ Parser completed: No errors found\n")
                self.console_output.append("\n🎉 COMPILATION SUCCESSFUL!")
                self.status_bar.showMessage("Compilation successful!", 3000)
            else:
                parser_text += "❌ SYNTAX ANALYSIS: FAILED\n\n"
                parser_text += f"Number of errors detected: {len(parser.errors)}\n\n"
                
                if parser.errors:
                    parser_text += "ERRORS DETECTED:\n"
                    parser_text += "-"*60 + "\n"
                    for i, error in enumerate(parser.errors, 1):
                        parser_text += f"\n{i}. {error}\n"
                
                self.console_output.append(f"❌ Parser found {len(parser.errors)} error(s)\n")
                self.console_output.append("\n❌ COMPILATION FAILED!")
                self.status_bar.showMessage("Compilation failed!", 3000)
            
            parser_text += "\n" + "="*60 + "\n"
            parser_text += f"Tokens analyzed: {len(parser.tokens)}\n"
            parser_text += f"Final position: {parser.position}\n"
            
            self.parser_output.setPlainText(parser_text)
            
            # Switch to appropriate tab
            if success:
                self.output_tabs.setCurrentIndex(3)  # Console tab
            else:
                self.output_tabs.setCurrentIndex(2)  # Parser results tab
            
            # Clean up
            if os.path.exists(temp_file):
                os.remove(temp_file)
        
        except Exception as e:
            self.console_output.append(f"\n❌ Error: {str(e)}")
            self.status_bar.showMessage(f"Error: {str(e)}", 5000)
            QMessageBox.critical(self, "Error", f"An error occurred:\n{str(e)}")
    
    def new_file(self):
        """Create a new file"""
        reply = QMessageBox.question(
            self, 'New File',
            'Do you want to create a new file? Unsaved changes will be lost.',
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            self.code_editor.clear()
            self.current_file = None
            self.status_bar.showMessage("New file created")
    
    def open_file(self):
        """Open a file"""
        filename, _ = QFileDialog.getOpenFileName(
            self, 'Open File', '',
            'Mini Pascal Files (*.mp *.txt);;All Files (*)'
        )
        
        if filename:
            try:
                with open(filename, 'r', encoding='utf-8') as f:
                    content = f.read()
                    self.code_editor.setPlainText(content)
                    self.current_file = filename
                    self.status_bar.showMessage(f"Opened: {filename}")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Could not open file:\n{str(e)}")
    
    def save_file(self):
        """Save the current file"""
        if self.current_file:
            try:
                with open(self.current_file, 'w', encoding='utf-8') as f:
                    f.write(self.code_editor.toPlainText())
                self.status_bar.showMessage(f"Saved: {self.current_file}")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Could not save file:\n{str(e)}")
        else:
            self.save_file_as()
    
    def save_file_as(self):
        """Save file with a new name"""
        filename, _ = QFileDialog.getSaveFileName(
            self, 'Save File As', '',
            'Mini Pascal Files (*.mp);;Text Files (*.txt);;All Files (*)'
        )
        
        if filename:
            try:
                # Add .mp extension if no extension provided
                if not filename.endswith(('.mp', '.txt')):
                    filename += '.mp'
                
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write(self.code_editor.toPlainText())
                self.current_file = filename
                self.status_bar.showMessage(f"Saved: {filename}")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Could not save file:\n{str(e)}")
    
    def clear_editor(self):
        """Clear the editor"""
        reply = QMessageBox.question(
            self, 'Clear Editor',
            'Are you sure you want to clear the editor?',
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            self.code_editor.clear()
            self.status_bar.showMessage("Editor cleared")
    
    def show_about(self):
        """Show about dialog"""
        about_text = """
        <h2>Mini Pascal Compiler</h2>
        <p><b>Version:</b> 1.0</p>
        <p><b>Language:</b> Mini Pascal</p>
        <br>
        <p>A complete compiler with:</p>
        <ul>
        <li>✅ Lexical Analyzer (Scanner)</li>
        <li>✅ Syntax Analyzer (Parser)</li>
        <li>✅ Syntax Highlighting</li>
        <li>✅ Error Detection</li>
        </ul>
        <br>
        <p><b>File Extension:</b> .mp (Mini Pascal)</p>
        <p><b>Developed with:</b> Python & PyQt5</p>
        """
        QMessageBox.about(self, "About Mini Pascal Compiler", about_text)


def main():
    """Main entry point"""
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    
    # Set application icon (if available)
    # app.setWindowIcon(QIcon('icon.png'))
    
    window = CompilerGUI()
    window.show()
    
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()