# ============================================
# Sistema de Análise de Vendas
# Refatorado com Classe, Datetime e Type Hints
# ============================================

import os
from collections import defaultdict
from datetime import datetime
from typing import List, Dict, Any, Optional, Tuple, Union

# ============================================
# FUNÇÕES AUXILIARES (Fora da Classe)
# ============================================

def formatar_moeda(valor: float) -> str:
    """
    Formata valor como moeda brasileira.

    Args:
        valor (float): Valor a formatar

    Returns:
        str: Valor formatado (R$ X.XXX,XX)
    """
    try:
        valor_formatado = f"{valor:,.2f}"

        valor_formatado = valor_formatado.replace(",", "v").replace(".", ",").replace("v", ".")
        return f"R$ {valor_formatado}"
    except Exception:
        return "R$ 0,00"

def extrair_mes(data_obj: datetime) -> str:
    """
    Extrai o mês de um objeto datetime.

    Args:
        data_obj (datetime): O objeto de data.

    Returns:
        str: Mês no formato YYYY-MM
    """
    return data_obj.strftime('%Y-%m')

# ============================================
# CLASSE PRINCIPAL DO SISTEMA
# ============================================

class SistemaVendas:
    """
    Encapsula toda a lógica e dados do sistema de vendas.
    """
    
    def __init__(self):
        """
        Inicializa o sistema com listas vazias e contadores.
        """
        self.vendas: List[Dict[str, Any]] = []
        self.contador_id: int = 1

    # ============================================
    # FUNÇÕES DE CADASTRO
    # ============================================

    def registrar_venda(
        self, 
        produto: str, 
        vendedor: str, 
        quantidade: int, 
        valor_unitario: float, 
        data: str
    ) -> Optional[Dict[str, Any]]:
        """
        Registra uma nova venda após validar os dados.

        Args:
            produto (str): Nome do produto
            vendedor (str): Nome do vendedor
            quantidade (int): Quantidade vendida
            valor_unitario (float): Valor unitário
            data (str): Data da venda (YYYY-MM-DD)

        Returns:
            Optional[Dict[str, Any]]: Venda registrada ou None se houver erro.
        """
       
        if not all([produto, vendedor, data]):
            print("Erro: Todos os campos de texto (produto, vendedor, data) são obrigatórios.")
            return None
        if not isinstance(quantidade, int) or quantidade <= 0:
            print("Erro: Quantidade deve ser um número inteiro positivo.")
            return None
        if not isinstance(valor_unitario, (int, float)) or valor_unitario <= 0:
            print("Erro: Valor unitário deve ser um número positivo.")
            return None

    
        try:
            data_obj = datetime.strptime(data, '%Y-%m-%d')
            data_str = data_obj.strftime('%Y-%m-%d')
        except ValueError:
            print("Erro: Data inválida ou fora do formato YYYY-MM-DD.")
            return None

        valor_total = round(quantidade * valor_unitario, 2)

        venda = {
            'id': self.contador_id,
            'produto': produto.strip(),
            'vendedor': vendedor.strip(),
            'quantidade': quantidade,
            'valor_unitario': valor_unitario,
            'valor_total': valor_total,
            'data_str': data_str,
            'data_obj': data_obj  
        }

        self.vendas.append(venda)
        self.contador_id += 1

        print(f"Venda ID {venda['id']} registrada com sucesso!")
        return venda

    # ============================================
    # FUNÇÕES DE CÁLCULOS
    # ============================================

    def calcular_total_vendas(self) -> float:
        """Calcula o total geral de vendas."""
        if not self.vendas:
            return 0.0
        return sum([v['valor_total'] for v in self.vendas])

    def calcular_vendas_por_vendedor(self) -> Dict[str, Dict[str, float]]:
        """Calcula estatísticas de vendas por vendedor."""
        stats = defaultdict(lambda: {'total_vendas': 0.0, 'quantidade_vendas': 0})

        for venda in self.vendas:
            vendedor = venda['vendedor']
            stats[vendedor]['total_vendas'] += venda['valor_total']
            stats[vendedor]['quantidade_vendas'] += 1

   
        for vendedor in stats:
            total = stats[vendedor]['total_vendas']
            qtd = stats[vendedor]['quantidade_vendas']
            stats[vendedor]['valor_medio'] = total / qtd if qtd > 0 else 0.0

        return dict(stats)

    def calcular_vendas_por_produto(self) -> Dict[str, Dict[str, Union[int, float]]]:
        """Calcula estatísticas de vendas por produto."""
        stats = defaultdict(lambda: {'total_vendido': 0.0, 'quantidade_vendida': 0})

        for venda in self.vendas:
            produto = venda['produto']
            stats[produto]['total_vendido'] += venda['valor_total']
            stats[produto]['quantidade_vendida'] += venda['quantidade']

        for produto in stats:
            stats[produto]['receita'] = stats[produto]['total_vendido']

        return dict(stats)

    def calcular_vendas_por_mes(self) -> Dict[str, float]:
        """Calcula vendas agrupadas por mês."""
        stats = defaultdict(float)
        for venda in self.vendas:
            mes = extrair_mes(venda['data_obj'])
            stats[mes] += venda['valor_total']

        return dict(sorted(stats.items()))

    # ============================================
    # FUNÇÕES DE RANKINGS
    # ============================================

    def ranking_vendedores(self, limite: int = 5) -> List[Tuple[str, float]]:
        """Gera ranking dos melhores vendedores por valor total."""
        stats_vendedor = self.calcular_vendas_por_vendedor()
        stats_lista = stats_vendedor.items()
        
        ranking = sorted(stats_lista, key=lambda item: item[1]['total_vendas'], reverse=True)
        
        return [(vendedor, dados['total_vendas']) for vendedor, dados in ranking[:limite]]

    def ranking_produtos(self, limite: int = 5) -> List[Tuple[str, int]]:
        """Gera ranking dos produtos mais vendidos por quantidade."""
        stats_produto = self.calcular_vendas_por_produto()
        stats_lista = stats_produto.items()

        ranking = sorted(stats_lista, key=lambda item: item[1]['quantidade_vendida'], reverse=True)

        return [(produto, int(dados['quantidade_vendida'])) for produto, dados in ranking[:limite]]

    def melhor_mes(self) -> Tuple[Optional[str], float]:
        """Identifica o mês com maior volume de vendas."""
        vendas_mes = self.calcular_vendas_por_mes()
        if not vendas_mes:
            return (None, 0.0)
        
        return max(vendas_mes.items(), key=lambda item: item[1])

    # ============================================
    # FUNÇÕES DE GERAÇÃO DE RELATÓRIOS (DADOS)
    # ============================================

    def gerar_relatorio_geral(self) -> Optional[Dict[str, Any]]:
        """Coleta todas as estatísticas para o relatório."""
        if not self.vendas:
            return None

        relatorio = {
            'total_vendas': self.calcular_total_vendas(),
            'estatisticas_vendedor': self.calcular_vendas_por_vendedor(),
            'estatisticas_produto': self.calcular_vendas_por_produto(),
            'vendas_por_mes': self.calcular_vendas_por_mes(),
            'ranking_vendedores': self.ranking_vendedores(5),
            'ranking_produtos': self.ranking_produtos(5),
            'melhor_mes': self.melhor_mes(),
            'total_transacoes': len(self.vendas)
        }
        return relatorio

    def gerar_relatorio_vendedor(self, nome_vendedor: str) -> Optional[Dict[str, Any]]:
        """Gera relatório específico de um vendedor."""
        

        vendas_do_vendedor = [
            v for v in self.vendas if nome_vendedor.lower() in v['vendedor'].lower()
        ]

        if not vendas_do_vendedor:
            return None

        total_vendas = sum(v['valor_total'] for v in vendas_do_vendedor)
        quantidade_vendas = len(vendas_do_vendedor)
        valor_medio = total_vendas / quantidade_vendas if quantidade_vendas > 0 else 0.0

        produtos_vendidos = defaultdict(int)
        for v in vendas_do_vendedor:
            produtos_vendidos[v['produto']] += v['quantidade']


        nome_oficial = vendas_do_vendedor[0]['vendedor']

        return {
            'nome': nome_oficial,
            'total_vendas': total_vendas,
            'quantidade_transacoes': quantidade_vendas,
            'valor_medio_transacao': valor_medio,
            'produtos_vendidos': dict(produtos_vendidos),
            'lista_vendas': vendas_do_vendedor
        }

    # ============================================
    # FUNÇÕES DE FORMATAÇÃO E EXPORTAÇÃO (SAÍDA)
    # ============================================

    def _formatar_relatorio_texto(self, relatorio: Dict[str, Any]) -> List[str]:
        """
        Função interna para formatar o relatório como texto (para console ou .txt).
        """
        linhas: List[str] = []
        
        linhas.append("=" * 40)
        linhas.append("      RELATÓRIO GERAL DE VENDAS")
        linhas.append("=" * 40)

        linhas.append("\nResumo Geral:")
        linhas.append(f"  - Total Geral de Vendas: {formatar_moeda(relatorio['total_vendas'])}")
        linhas.append(f"  - Total de Transações:   {relatorio['total_transacoes']}")
        mes, valor = relatorio['melhor_mes']
        if mes:
            linhas.append(f"  - Melhor Mês:            {mes} ({formatar_moeda(valor)})")

        linhas.append("\n" + "-" * 40)
        linhas.append("Top 5 Vendedores (por Valor)")
        linhas.append("-" * 40)
        for i, (vendedor, total) in enumerate(relatorio['ranking_vendedores'], 1):
            linhas.append(f"  {i}. {vendedor:<20} - {formatar_moeda(total)}")

        linhas.append("\n" + "-" * 40)
        linhas.append("Top 5 Produtos (por Quantidade)")
        linhas.append("-" * 40)
        for i, (produto, qtd) in enumerate(relatorio['ranking_produtos'], 1):
            linhas.append(f"  {i}. {produto:<20} - {qtd} unidades")

        linhas.append("\n" + "-" * 40)
        linhas.append("Vendas por Mês")
        linhas.append("-" * 40)
        for mes, total in relatorio['vendas_por_mes'].items():
            linhas.append(f"  - {mes}: {formatar_moeda(total)}")

        linhas.append("\n" + "=" * 40)
        
        return linhas

    def _formatar_relatorio_markdown(self, relatorio: Dict[str, Any]) -> List[str]:
        """
        Função interna para formatar o relatório como Markdown.
        """
        linhas: List[str] = []
        
        linhas.append("# Relatório Geral de Vendas\n")
        
        linhas.append("## Resumo Geral\n")
        linhas.append(f"* **Total Geral de Vendas:** {formatar_moeda(relatorio['total_vendas'])}")
        linhas.append(f"* **Total de Transações:** {relatorio['total_transacoes']}")
        mes, valor = relatorio['melhor_mes']
        if mes:
            linhas.append(f"* **Melhor Mês:** {mes} ({formatar_moeda(valor)})\n")
        
        linhas.append("## Top 5 Vendedores (por Valor)\n")
        for i, (vendedor, total) in enumerate(relatorio['ranking_vendedores'], 1):
            linhas.append(f"{i}.  **{vendedor}** - {formatar_moeda(total)}")
        
        linhas.append("\n## Top 5 Produtos (por Quantidade)\n")
        for i, (produto, qtd) in enumerate(relatorio['ranking_produtos'], 1):
            linhas.append(f"{i}.  **{produto}** - {qtd} unidades")
        
        linhas.append("\n## Vendas por Mês\n")
        for mes, total in relatorio['vendas_por_mes'].items():
            linhas.append(f"* **{mes}:** {formatar_moeda(total)}")
            
        return linhas

    def exibir_relatorio_vendas(self) -> None:
        """Exibe relatório geral formatado no console."""
        relatorio = self.gerar_relatorio_geral()
        if not relatorio:
            print("\n*** Nenhuma venda registrada para gerar relatório. ***")
            return
            
        linhas_formatadas = self._formatar_relatorio_texto(relatorio)
        print("\n".join(linhas_formatadas))

    def salvar_relatorio_geral(self, pasta: str = 'relatorios', nome_arquivo: str = 'relatorio_geral.txt') -> None:
        """Salva o relatório geral em um arquivo de texto."""
        relatorio = self.gerar_relatorio_geral()
        if not relatorio:
            print("\n*** Nenhuma venda registrada para salvar relatório. ***")
            return

        if not os.path.exists(pasta):
            os.makedirs(pasta)
        
        filepath = os.path.join(pasta, nome_arquivo)
        
        try:
            linhas_formatadas = self._formatar_relatorio_texto(relatorio)
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write("\n".join(linhas_formatadas))
            print(f"\nRelatório salvo com sucesso em: {os.path.abspath(filepath)}")
        except IOError as e:
            print(f"\nErro ao salvar relatório: {e}")

    def salvar_relatorio_markdown(self, pasta: str = 'relatorios', nome_arquivo: str = 'relatorio_geral.md') -> None:
        """Salva o relatório geral em um arquivo Markdown (.md)."""
        relatorio = self.gerar_relatorio_geral()
        if not relatorio:
            print("\n*** Nenhuma venda registrada para salvar relatório. ***")
            return

        if not os.path.exists(pasta):
            os.makedirs(pasta)
            
        filepath = os.path.join(pasta, nome_arquivo)
        
        try:
            linhas_formatadas = self._formatar_relatorio_markdown(relatorio)
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write("\n".join(linhas_formatadas))
            print(f"\nRelatório Markdown salvo com sucesso em: {os.path.abspath(filepath)}")
        except IOError as e:
            print(f"\nErro ao salvar relatório Markdown: {e}")

    # ============================================
    # DADOS DE EXEMPLO (para facilitar testes)
    # ============================================

    def carregar_dados_exemplo(self) -> None:
        """Carrega um conjunto de vendas para teste."""
        print("Carregando dados de exemplo...")
        self.registrar_venda('Notebook Dell', 'Maria Silva', 2, 3500.00, '2024-01-15')
        self.registrar_venda('Mouse Logitech', 'João Santos', 5, 89.90, '2024-01-16')
        self.registrar_venda('Teclado Mecânico', 'Maria Silva', 3, 250.00, '2024-01-17')
        self.registrar_venda('Monitor LG', 'Carlos Andrade', 2, 1200.00, '2024-01-20')
        self.registrar_venda('Notebook Dell', 'João Santos', 1, 3500.00, '2024-02-05')
        self.registrar_venda('Cadeira Gamer', 'Maria Silva', 1, 1100.00, '2024-02-10')
        self.registrar_venda('Mouse Logitech', 'Ana Pereira', 10, 85.00, '2024-02-12')
        self.registrar_venda('Teclado Mecânico', 'Carlos Andrade', 2, 240.00, '2024-03-01')
        self.registrar_venda('Monitor LG', 'João Santos', 1, 1150.00, '2024-03-05')


# ============================================
# FUNÇÕES DE MENU (Interface do Usuário)
# ============================================

def menu_registrar_venda(sistema: SistemaVendas) -> None:
    """
    Coleta dados do usuário para registrar uma nova venda.
    """
    print("\n--- Registro de Nova Venda ---")
    try:
        produto = input("Produto: ")
        vendedor = input("Vendedor: ")
        quantidade = int(input("Quantidade: "))
        valor_unitario = float(input("Valor Unitário (ex: 3500.00): "))
        data = input("Data (YYYY-MM-DD): ")


        sistema.registrar_venda(produto, vendedor, quantidade, valor_unitario, data)

    except ValueError:
        print("\nErro: Quantidade e Valor Unitário devem ser números.")
    except Exception as e:
        print(f"\nOcorreu um erro inesperado: {e}")

def menu_relatorio_vendedor(sistema: SistemaVendas) -> None:
    """
    Coleta nome do vendedor e exibe seu relatório.
    """
    print("\n--- Relatório por Vendedor ---")
    nome = input("Digite o nome do vendedor (pode ser parcial): ")
    if not nome:
        print("Nome não pode ser vazio.")
        return
        
    
    relatorio = sistema.gerar_relatorio_vendedor(nome)

    if not relatorio:
        print(f"Nenhuma venda encontrada para o vendedor contendo '{nome}'.")
        return

    print(f"\nRelatório de: {relatorio['nome']}")
    print(f"  - Total Vendido: {formatar_moeda(relatorio['total_vendas'])}")
    print(f"  - Nº de Transações: {relatorio['quantidade_transacoes']}")
    print(f"  - Valor Médio/Transação: {formatar_moeda(relatorio['valor_medio_transacao'])}")
    print("\n  Produtos vendidos (Quantidade):")
    for produto, qtd in relatorio['produtos_vendidos'].items():
        print(f"    - {produto}: {qtd} un.")

# ============================================
# FUNÇÃO PRINCIPAL (Execução)
# ============================================

def main() -> None:
    """
    Função principal do programa (Menu interativo).
    """
    
   
    sistema = SistemaVendas()
    
    
    sistema.carregar_dados_exemplo()

    while True:
        print("\n" + "=" * 30)
        print("  Sistema de Análise de Vendas")
        print("=" * 30)
        print("1. Registrar Venda")
        print("2. Exibir Relatório Geral")
        print("3. Exibir Relatório por Vendedor")
        print("4. Salvar Relatório Geral (Arquivo .txt)")
        print("5. Salvar Relatório (Markdown .md)")
        print("6. Sair")
        print("-" * 30)

        opcao = input("Escolha uma opção: ")

        if opcao == '1':
            menu_registrar_venda(sistema) 
        elif opcao == '2':
            sistema.exibir_relatorio_vendas() 
        elif opcao == '3':
            menu_relatorio_vendedor(sistema) 
        elif opcao == '4':
            sistema.salvar_relatorio_geral()
        elif opcao == '5':
            sistema.salvar_relatorio_markdown()
        elif opcao == '6':
            print("Saindo do sistema...")
            break
        else:
            print("Opção inválida. Tente novamente.")

if __name__ == "__main__":
    main()