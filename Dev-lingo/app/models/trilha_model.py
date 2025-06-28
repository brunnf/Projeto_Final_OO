import json

class TrilhaModel:
    """
    Esta classe agora gerencia os dados da trilha lendo e escrevendo
    em um arquivo JSON, em vez de guardá-los na memória.
    """
    def __init__(self, db_path='app/dados/trilha.json'): # <-- A MUDANÇA ESTÁ AQUI
        """
        O construtor agora aponta para o novo caminho do arquivo JSON.
        """
        self.db_path = db_path

    # --- Métodos Auxiliares para ler e salvar o JSON ---

    def _ler_dados(self):
        """Lê todo o conteúdo do arquivo JSON e o retorna."""
        try:
            with open(self.db_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            return {"proximo_id_modulo": 1, "proximo_id_aula": 1, "proximo_id_questao": 1, "modulos": []}

    def _salvar_dados(self, dados):
        """Recebe um dicionário de dados e o salva no arquivo JSON."""
        with open(self.db_path, 'w', encoding='utf-8') as f:
            json.dump(dados, f, indent=4, ensure_ascii=False)

    #
    # ... O RESTO DO CÓDIGO DO ARQUIVO CONTINUA EXATAMENTE O MESMO ...
    #
    
    # ======================================================
    # --- MÉTODOS DE MÓDULO (Agora operam no arquivo) ---
    # ======================================================

    def get_all_modulos(self):
        dados = self._ler_dados()
        return dados.get('modulos', [])

    def get_modulo_by_id(self, mod_id):
        dados = self._ler_dados()
        return next((m for m in dados['modulos'] if m['id'] == mod_id), None)

    def create_modulo(self, titulo, descricao):
        dados = self._ler_dados()
        novo_modulo = {
            "id": dados['proximo_id_modulo'], "titulo": titulo, "descricao": descricao,
            "aulas": [], "questoes": []
        }
        dados['modulos'].append(novo_modulo)
        dados['proximo_id_modulo'] += 1
        self._salvar_dados(dados)
        return novo_modulo

    def update_modulo(self, mod_id, titulo, descricao):
        dados = self._ler_dados()
        modulo = next((m for m in dados['modulos'] if m['id'] == mod_id), None)
        if modulo:
            modulo['titulo'] = titulo
            modulo['descricao'] = descricao
            self._salvar_dados(dados)
            return True
        return False

    def delete_modulo(self, mod_id):
        dados = self._ler_dados()
        initial_len = len(dados['modulos'])
        dados['modulos'] = [m for m in dados['modulos'] if m['id'] != mod_id]
        if len(dados['modulos']) < initial_len:
            self._salvar_dados(dados)
            return True
        return False

    # ======================================================
    # --- MÉTODOS DE AULA (Agora operam no arquivo) ---
    # ======================================================

    def get_aula_by_id(self, aula_id):
        dados = self._ler_dados()
        for modulo in dados.get('modulos', []):
            for aula in modulo.get('aulas', []):
                if aula['id'] == aula_id:
                    return aula, modulo
        return None, None

    def create_aula(self, mod_id, titulo, conteudo):
        dados = self._ler_dados()
        modulo = next((m for m in dados['modulos'] if m['id'] == mod_id), None)
        if not modulo: return None
        
        nova_aula = {"id": dados['proximo_id_aula'], "titulo": titulo, "conteudo": conteudo}
        modulo.setdefault('aulas', []).append(nova_aula)
        dados['proximo_id_aula'] += 1
        self._salvar_dados(dados)
        return nova_aula

    def update_aula(self, aula_id, titulo, conteudo):
        dados = self._ler_dados()
        for modulo in dados.get('modulos', []):
            for aula in modulo.get('aulas', []):
                if aula['id'] == aula_id:
                    aula['titulo'] = titulo
                    aula['conteudo'] = conteudo
                    self._salvar_dados(dados)
                    return True
        return False

    def delete_aula(self, mod_id, aula_id):
        dados = self._ler_dados()
        modulo = next((m for m in dados['modulos'] if m['id'] == mod_id), None)
        if modulo:
            initial_len = len(modulo.get('aulas', []))
            modulo['aulas'] = [a for a in modulo.get('aulas', []) if a['id'] != aula_id]
            if len(modulo.get('aulas', [])) < initial_len:
                self._salvar_dados(dados)
                return True
        return False

    # ======================================================
    # --- MÉTODOS DE QUESTÃO (Agora operam no arquivo) ---
    # ======================================================

    def get_questao_by_id(self, questao_id):
        dados = self._ler_dados()
        for modulo in dados.get('modulos', []):
            for questao in modulo.get('questoes', []):
                if questao['id'] == questao_id:
                    return questao, modulo
        return None, None

    def create_questao(self, mod_id, enunciado, opcoes, resposta_correta):
        dados = self._ler_dados()
        modulo = next((m for m in dados['modulos'] if m['id'] == mod_id), None)
        if not modulo: return None
        
        nova_questao = {
            "id": dados['proximo_id_questao'], "enunciado": enunciado,
            "opcoes": opcoes, "resposta_correta": resposta_correta
        }
        modulo.setdefault('questoes', []).append(nova_questao)
        dados['proximo_id_questao'] += 1
        self._salvar_dados(dados)
        return nova_questao

    def update_questao(self, questao_id, enunciado, opcoes, resposta_correta):
        dados = self._ler_dados()
        for modulo in dados.get('modulos', []):
            for questao in modulo.get('questoes', []):
                if questao['id'] == questao_id:
                    questao['enunciado'] = enunciado
                    questao['opcoes'] = opcoes
                    questao['resposta_correta'] = resposta_correta
                    self._salvar_dados(dados)
                    return True
        return False

    def delete_questao(self, mod_id, questao_id):
        dados = self._ler_dados()
        modulo = next((m for m in dados['modulos'] if m['id'] == mod_id), None)
        if modulo:
            initial_len = len(modulo.get('questoes', []))
            modulo['questoes'] = [q for q in modulo.get('questoes', []) if q['id'] != questao_id]
            if len(modulo.get('questoes', [])) < initial_len:
                self._salvar_dados(dados)
                return True
        return False