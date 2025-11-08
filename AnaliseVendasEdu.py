

# ============================================
# Sistema de Análise de Vendas
# ============================================

import os
from collections import defaultdict


vendas = []
contador_id = 1

# ============================================
# FUNÇÕES DE CADASTRO
# ============================================

def registrar_venda(produto, vendedor, quantidade, valor_unitario, data):
    """
    Registra uma nova venda.

    Args:
        produto (str): Nome do produto
        vendedor (str): Nome do vendedor
        quantidade (int): Quantidade vendida
        valor_unitario (float): Valor unitário
        data (str): Data da venda (YYYY-MM-DD)

    Returns:
        dict: Venda registrada ou None se houver erro.
    """
    global contador_id


    if not all([produto, vendedor, data]):
        print("Erro: Todos os campos de texto (produto, vendedor, data) são obrigatórios.")
        return None
    if not isinstance(quantidade, int) or quantidade <= 0:
        print("Erro: Quantidade deve ser um número inteiro positivo.")
        return None
    if not isinstance(valor_unitario, (int, float)) or valor_unitario <= 0:
        print("Erro: Valor unitário deve ser um número positivo.")
        return None
    if len(data) != 10 or data[4] != '-' or data[7] != '-':
        print("Erro: Data deve estar no formato YYYY-MM-DD.")
        return None


    valor_total = quantidade * valor_unitario


    venda = {
        'id': contador_id,
        'produto': produto.strip(),
        'vendedor': vendedor.strip(),
        'quantidade': quantidade,
        'valor_unitario': valor_unitario,
        'valor_total': valor_total,
        'data': data
    }


    vendas.append(venda)
    contador_id += 1

    print(f"Venda ID {venda['id']} registrada com sucesso!")
    return venda

# ============================================
# FUNÇÕES DE CÁLCULOS
# ============================================

def calcular_total_vendas():
    """
    Calcula o total geral de vendas.

    Returns:
        float: Total de todas as vendas
    """
    if not vendas:
        return 0.0

    return sum([v['valor_total'] for v in vendas])

def calcular_vendas_por_vendedor():
    """
    Calcula estatísticas de vendas por vendedor.

    Returns:
        dict: {vendedor: {total_vendas, quantidade_vendas, valor_medio}}
    """

    stats = defaultdict(lambda: {'total_vendas': 0.0, 'quantidade_vendas': 0})

    for venda in vendas:
        vendedor = venda['vendedor']
        stats[vendedor]['total_vendas'] += venda['valor_total']
        stats[vendedor]['quantidade_vendas'] += 1


    for vendedor in stats:
        total = stats[vendedor]['total_vendas']
        qtd = stats[vendedor]['quantidade_vendas']
        stats[vendedor]['valor_medio'] = total / qtd if qtd > 0 else 0.0

    return dict(stats)

def calcular_vendas_por_produto():
    """
    Calcula estatísticas de vendas por produto.

    Returns:
        dict: {produto: {total_vendido, quantidade_vendida, receita}}
    """
    stats = defaultdict(lambda: {'total_vendido': 0.0, 'quantidade_vendida': 0})

    for venda in vendas:
        produto = venda['produto']
        stats[produto]['total_vendido'] += venda['valor_total']
        stats[produto]['quantidade_vendida'] += venda['quantidade']


    for produto in stats:
        stats[produto]['receita'] = stats[produto]['total_vendido']

    return dict(stats)

def calcular_vendas_por_mes():
    """
    Calcula vendas agrupadas por mês.

    Returns:
        dict: {mes (YYYY-MM): total_vendas}
    """
    stats = defaultdict(float)
    for venda in vendas:
        mes = extrair_mes(venda['data'])
        stats[mes] += venda['valor_total']


    return dict(sorted(stats.items()))

# ============================================
# FUNÇÕES DE RANKINGS
# ============================================

def ranking_vendedores(limite=5):
    """
    Gera ranking dos melhores vendedores por valor total.

    Args:
        limite (int): Quantidade de vendedores no ranking

    Returns:
        list: Lista de tuplas (vendedor, total_vendas)
    """
    stats_vendedor = calcular_vendas_por_vendedor()

    stats_lista = stats_vendedor.items()


    ranking = sorted(stats_lista, key=lambda item: item[1]['total_vendas'], reverse=True)


    return [(vendedor, dados['total_vendas']) for vendedor, dados in ranking[:limite]]

def ranking_produtos(limite=5):
    """
    Gera ranking dos produtos mais vendidos por quantidade.

    Args:
        limite (int): Quantidade de produtos no ranking

    Returns:
        list: Lista de tuplas (produto, quantidade_vendida)
    """
    stats_produto = calcular_vendas_por_produto()
    stats_lista = stats_produto.items()


    ranking = sorted(stats_lista, key=lambda item: item[1]['quantidade_vendida'], reverse=True)


    return [(produto, dados['quantidade_vendida']) for produto, dados in ranking[:limite]]

def melhor_mes():
    """
    Identifica o mês com maior volume de vendas.

    Returns:
        tuple: (mes, total) ou (None, 0.0) se não houver vendas.
    """
    vendas_mes = calcular_vendas_por_mes()
    if not vendas_mes:
        return (None, 0.0)


    return max(vendas_mes.items(), key=lambda item: item[1])

# ============================================
# FUNÇÕES DE RELATÓRIOS
# ============================================

def gerar_relatorio_geral():
    """
    Coleta todas as estatísticas para o relatório.

    Returns:
        dict: Dicionário com todas as informações
    """
    if not vendas:
        return None # Retorna None se não houver vendas

    relatorio = {
        'total_vendas': calcular_total_vendas(),
        'estatisticas_vendedor': calcular_vendas_por_vendedor(),
        'estatisticas_produto': calcular_vendas_por_produto(),
        'vendas_por_mes': calcular_vendas_por_mes(),
        'ranking_vendedores': ranking_vendedores(5),
        'ranking_produtos': ranking_produtos(5),
        'melhor_mes': melhor_mes(),
        'total_transacoes': len(vendas)
    }
    return relatorio

def gerar_relatorio_vendedor(nome_vendedor):
    """
    Gera relatório específico de um vendedor.

    Args:
        nome_vendedor (str): Nome do vendedor

    Returns:
        dict: Estatísticas do vendedor ou None se não encontrado.
    """

    vendas_do_vendedor = [
        v for v in vendas if nome_vendedor.lower() in v['vendedor'].lower()
    ]

    if not vendas_do_vendedor:
        return None

    total_vendas = sum(v['valor_total'] for v in vendas_do_vendedor)
    quantidade_vendas = len(vendas_do_vendedor)
    valor_medio = total_vendas / quantidade_vendas if quantidade_vendas > 0 else 0.0


    produtos_vendidos = defaultdict(int)
    for v in vendas_do_vendedor:
        produtos_vendidos[v['produto']] += v['quantidade']


    nome_oficial = vendas_do_vendedor[0]['vendedor'] if vendas_do_vendedor else nome_vendedor

    return {
        'nome': nome_oficial,
        'total_vendas': total_vendas,
        'quantidade_transacoes': quantidade_vendas,
        'valor_medio_transacao': valor_medio,
        'produtos_vendidos': dict(produtos_vendidos),
        'lista_vendas': vendas_do_vendedor
    }

def exibir_relatorio_vendas():
    """
    Exibe relatório geral formatado no console.
    """
    relatorio = gerar_relatorio_geral()

    if not relatorio:
        print("\n*** Nenhuma venda registrada para gerar relatório. ***")
        return

    print("\n" + "=" * 40)
    print("      RELATÓRIO GERAL DE VENDAS")
    print("=" * 40)

    print(f"\nResumo Geral:")
    print(f"  - Total Geral de Vendas: {formatar_moeda(relatorio['total_vendas'])}")
    print(f"  - Total de Transações:   {relatorio['total_transacoes']}")
    mes, valor = relatorio['melhor_mes']
    if mes:
        print(f"  - Melhor Mês:            {mes} ({formatar_moeda(valor)})")

    print("\n" + "-" * 40)
    print("Top 5 Vendedores (por Valor)")
    print("-" * 40)
    for i, (vendedor, total) in enumerate(relatorio['ranking_vendedores'], 1):
        print(f"  {i}. {vendedor:<20} - {formatar_moeda(total)}")

    print("\n" + "-" * 40)
    print("Top 5 Produtos (por Quantidade)")
    print("-" * 40)
    for i, (produto, qtd) in enumerate(relatorio['ranking_produtos'], 1):
        print(f"  {i}. {produto:<20} - {qtd} unidades")

    print("\n" + "-" * 40)
    print("Vendas por Mês")
    print("-" * 40)
    for mes, total in relatorio['vendas_por_mes'].items():
        print(f"  - {mes}: {formatar_moeda(total)}")

    print("\n" + "=" * 40)

def salvar_relatorio_geral():
    """
    Salva o relatório geral em um arquivo de texto.
    """
    relatorio = gerar_relatorio_geral()
    if not relatorio:
        print("\n*** Nenhuma venda registrada para salvar relatório. ***")
        return


    if not os.path.exists('relatorios'):
        os.makedirs('relatorios')

    filepath = 'relatorios/relatorio_geral.txt'

    try:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write("=" * 40 + "\n")
            f.write("      RELATÓRIO GERAL DE VENDAS\n")
            f.write("=" * 40 + "\n")

            f.write(f"\nResumo Geral:\n")
            f.write(f"  - Total Geral de Vendas: {formatar_moeda(relatorio['total_vendas'])}\n")
            f.write(f"  - Total de Transações:   {relatorio['total_transacoes']}\n")
            mes, valor = relatorio['melhor_mes']
            if mes:
                f.write(f"  - Melhor Mês:            {mes} ({formatar_moeda(valor)})\n")

            f.write("\n" + "-" * 40 + "\n")
            f.write("Top 5 Vendedores (por Valor)\n")
            f.write("-" * 40 + "\n")
            for i, (vendedor, total) in enumerate(relatorio['ranking_vendedores'], 1):
                f.write(f"  {i}. {vendedor:<20} - {formatar_moeda(total)}\n")

            f.write("\n" + "-" * 40 + "\n")
            f.write("Top 5 Produtos (por Quantidade)\n")
            f.write("-" * 40 + "\n")
            for i, (produto, qtd) in enumerate(relatorio['ranking_produtos'], 1):
                f.write(f"  {i}. {produto:<20} - {qtd} unidades\n")

            f.write("\n" + "-" * 40 + "\n")
            f.write("Vendas por Mês\n")
            f.write("-" * 40 + "\n")
            for mes, total in relatorio['vendas_por_mes'].items():
                f.write(f"  - {mes}: {formatar_moeda(total)}\n")

            f.write("\n" + "=" * 40 + "\n")
        
        print(f"\nRelatório salvo com sucesso em: {os.path.abspath(filepath)}")
    
    except IOError as e:
        print(f"\nErro ao salvar relatório: {e}")

# ============================================
# NOVA FUNÇÃO - SALVAR EM MARKDOWN
# ============================================

def salvar_relatorio_markdown():
    """
    Salva o relatório geral em um arquivo Markdown (.md).
    """
    relatorio = gerar_relatorio_geral()
    if not relatorio:
        print("\n*** Nenhuma venda registrada para salvar relatório. ***")
        return

 
    if not os.path.exists('relatorios'):
        os.makedirs('relatorios')

    filepath = 'relatorios/relatorio_geral.md'

    try:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write("# Relatório Geral de Vendas\n\n")

            f.write("## Resumo Geral\n\n")
            f.write(f"* **Total Geral de Vendas:** {formatar_moeda(relatorio['total_vendas'])}\n")
            f.write(f"* **Total de Transações:** {relatorio['total_transacoes']}\n")
            mes, valor = relatorio['melhor_mes']
            if mes:
                f.write(f"* **Melhor Mês:** {mes} ({formatar_moeda(valor)})\n\n")

            f.write("## Top 5 Vendedores (por Valor)\n\n")
            for i, (vendedor, total) in enumerate(relatorio['ranking_vendedores'], 1):
                f.write(f"{i}.  **{vendedor}** - {formatar_moeda(total)}\n")

            f.write("\n## Top 5 Produtos (por Quantidade)\n\n")
            for i, (produto, qtd) in enumerate(relatorio['ranking_produtos'], 1):
                f.write(f"{i}.  **{produto}** - {qtd} unidades\n")

            f.write("\n## Vendas por Mês\n\n")
            for mes, total in relatorio['vendas_por_mes'].items():
                f.write(f"* **{mes}:** {formatar_moeda(total)}\n")
        
        print(f"\nRelatório Markdown salvo com sucesso em: {os.path.abspath(filepath)}")
    
    except IOError as e:
        print(f"\nErro ao salvar relatório Markdown: {e}")


# ============================================
# FUNÇÕES AUXILIARES
# ============================================

def formatar_moeda(valor):
    """
    Formata valor como moeda brasileira.

    Args:
        valor (float): Valor a formatar

    Returns:
        str: Valor formatado (R$ X.XXX,XX)
    """

    valor_formatado = f"{valor:,.2f}"
 
    valor_formatado = valor_formatado.replace(",", "v").replace(".", ",").replace("v", ".")
    return f"R$ {valor_formatado}"

def extrair_mes(data):
    """
    Extrai o mês de uma data no formato YYYY-MM-DD.

    Args:
        data (str): Data no formato YYYY-MM-DD

    Returns:
        str: Mês no formato YYYY-MM
    """
   
    if isinstance(data, str) and len(data) >= 7:
        return data[0:7]
    return "Data Inválida"

# ============================================
# DADOS DE EXEMPLO (para facilitar testes)
# ============================================

def carregar_dados_exemplo():
    print("Carregando dados de exemplo...")
    registrar_venda('Notebook Dell', 'Maria Silva', 2, 3500.00, '2024-01-15')
    registrar_venda('Mouse Logitech', 'João Santos', 5, 89.90, '2024-01-16')
    registrar_venda('Teclado Mecânico', 'Maria Silva', 3, 250.00, '2024-01-17')
    registrar_venda('Monitor LG', 'Carlos Andrade', 2, 1200.00, '2024-01-20')
    registrar_venda('Notebook Dell', 'João Santos', 1, 3500.00, '2024-02-05')
    registrar_venda('Cadeira Gamer', 'Maria Silva', 1, 1100.00, '2024-02-10')
    registrar_venda('Mouse Logitech', 'Ana Pereira', 10, 85.00, '2024-02-12')
    registrar_venda('Teclado Mecânico', 'Carlos Andrade', 2, 240.00, '2024-03-01')
    registrar_venda('Monitor LG', 'João Santos', 1, 1150.00, '2024-03-05')
    print(f"{len(vendas)} vendas de exemplo carregadas.\n")

# ============================================
# FUNÇÃO PRINCIPAL
# ============================================

def menu_registrar_venda():
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

        registrar_venda(produto, vendedor, quantidade, valor_unitario, data)

    except ValueError:
        print("\nErro: Quantidade e Valor Unitário devem ser números.")
    except Exception as e:
        print(f"\nOcorreu um erro inesperado: {e}")

def menu_relatorio_vendedor():
    """
    Coleta nome do vendedor e exibe seu relatório.
    """
    print("\n--- Relatório por Vendedor ---")
    nome = input("Digite o nome do vendedor (pode ser parcial): ")
    relatorio = gerar_relatorio_vendedor(nome)

    if not relatorio:
        print(f"Nenhuma venda encontrada para o vendedor contendo '{nome}'.")
        return

    print(f"\nRelatório de: {relatorio['nome']}")
    print(f"  - Total Vendido: {formatar_moeda(relatorio['total_vendas'])}")
    print(f"  - Nº de Transações: {relatorio['quantidade_transacoes']}")
    print(f"  - Valor Médio/Transação: {formatar_moeda(relatorio['valor_medio_transacao'])}")
    print("\n  Produtos vendidos (Quantidade):")
    for produto, qtd in relatorio['produtos_vendidos'].items():
        print(f"    - {produto}: {qtd} un.")

def main():
    """
    Função principal do programa (Menu interativo).
    """
    
    carregar_dados_exemplo()

    while True:
        print("\n" + "=" * 30)
        print("  Sistema de Análise de Vendas")
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
            menu_registrar_venda()
        elif opcao == '2':
            exibir_relatorio_vendas()
        elif opcao == '3':
            menu_relatorio_vendedor()
        elif opcao == '4':
            salvar_relatorio_geral()
        elif opcao == '5': 
            salvar_relatorio_markdown()
        elif opcao == '6': 
            print("Saindo do sistema...")
            break
        else:
            print("Opção inválida. Tente novamente.")

if __name__ == "__main__":
    main()