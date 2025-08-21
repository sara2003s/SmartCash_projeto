from django.utils import timezone
from financas.models import Transacao, Meta
from django.db.models import Sum
from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User


def login_view(request):
    if request.method == 'POST':
        email = request.POST.get('email')   # pega do formulário
        password = request.POST.get('password')

        user = authenticate(request, username=email, password=password)  # aqui usamos o backend
        if user is not None:
            messages.success(request, "Login realizado com sucesso!")
            login(request, user)
        return redirect('financas:dashboard')
    
    return render(request, 'financas/index.html')

def logout_view(request):
    logout(request)
    return redirect('inicio')  # <-- vai para a home

def register_view(request):
    if request.method == "POST":
        username = request.POST.get("username")
        email = request.POST.get("email")
        password = request.POST.get("password")

        if User.objects.filter(username=username).exists():
            messages.error(request, "Esse usuário já existe.")
            return redirect("register")

        user = User.objects.create_user(username=username, email=email, password=password)
        login(request, user)
        messages.success(request, "Cadastro realizado com sucesso!")
        return redirect("index")

    return render(request, "financas/register.html")

@login_required
def dashboard(request):
    entradas = Transacao.objects.filter(usuario=request.user, tipo='entrada').aggregate(Sum('valor'))['valor__sum'] or 0
    saidas = Transacao.objects.filter(usuario=request.user, tipo='saida').aggregate(Sum('valor'))['valor__sum'] or 0
    saldo = entradas - saidas
   
    try:
        meta = Meta.objects.filter(usuario=request.user).first()
        meta_valor = meta.valor_atingido
        meta_total = meta.valor_total
    except:
        meta_valor = 1000
        meta_total = 2000
        
    try:
        gastos_por_categoria = Transacao.objects.filter(
            usuario=request.user, 
            tipo='saida'
        ).values('categoria__nome', 'categoria__cor').annotate(
            total_gasto=Sum('valor')
        ).order_by('-total_gasto')

        total_gastos = sum(item['total_gasto'] for item in gastos_por_categoria)
        
        gastos_detalhados = []
        for item in gastos_por_categoria:
            porcentagem = (item['total_gasto'] / total_gastos) * 100 if total_gastos > 0 else 0
            gastos_detalhados.append({
                'nome': item['categoria__nome'],
                'cor': item['categoria__cor'], 
                'valor': item['total_gasto'],
                'porcentagem': porcentagem
            })
            
        expenses_labels = [item['categoria__nome'] for item in gastos_por_categoria]
        expenses_data = [item['total_gasto'] for item in gastos_por_categoria]

    except Exception as e:
        print(f"Erro ao buscar dados de gastos: {e}")
        expenses_labels = ['Alimentação', 'Transporte', 'Lazer', 'Saúde', 'Outros']
        expenses_data = [1200.50, 850.00, 650.00, 350.00, 209.00]
        gastos_detalhados = [
            {'nome': 'Alimentação', 'cor': '#F87171', 'valor': 1200.50, 'porcentagem': 37},
            {'nome': 'Transporte', 'cor': '#60A5FA', 'valor': 850.00, 'porcentagem': 26},
            {'nome': 'Lazer', 'cor': '#FBBE24', 'valor': 650.00, 'porcentagem': 20},
            {'nome': 'Saúde', 'cor': '#34D399', 'valor': 350.00, 'porcentagem': 11},
            {'nome': 'Outros', 'cor': '#8B5CF6', 'valor': 209.00, 'porcentagem': 6},
        ]

    try:
        transacoes_recentes = Transacao.objects.filter(usuario=request.user).order_by('-data')[:6]
    except Exception as e:
        print(f"Erro ao buscar transações recentes: {e}")
        transacoes_recentes = [
        ]

    context = {
        'saldo': f"{saldo:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.'), 
        'entradas': f"{entradas:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.'),
        'saidas': f"{saidas:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.'),
        'meta': f"{meta_valor:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.'),
        'meta_total': f"{meta_total:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.'),
        'expenses_labels': expenses_labels,
        'expenses_data': expenses_data,
        'gastos_detalhados': gastos_detalhados, # Use a lista de fallback no caso de erro
        'transacoes_recentes': transacoes_recentes,
    }
    return render(request, "financas/dashboard.html", context)

@login_required
def transacoes(request):
    return render(request, "financas/transacoes.html")

@login_required
def categorias(request):
    return render(request, "financas/categorias.html")

@login_required
def metas(request):
    return render(request, "financas/metas.html")

@login_required
def conexoes_bancarias(request):
    return render(request, "financas/conexoes_bancarias.html")

@login_required
def configuracoes(request):
    return render(request, "financas/configuracoes.html")

def inicio(request):
    planos = [
        {
            "name": "Freemium",
            "price": "Grátis",
            "description": "Para começar a organizar suas finanças",
            "features": [
                "Dashboard básico",
                "Até 3 metas financeiras",
                "Análise básica de gastos",
                "Upload de até 5 extratos por mês",
                "1 usuário (sem compartilhamento)",
                "Upload manual apenas",
                "Suporte por email"
            ],
            "popular": False,
            "cta": "Começar Grátis"
        },
        {
            "name": "Pro",
            "price": "R$ 19,90/mês",
            "description": "Controle completo das suas finanças",
            "features": [
                "Tudo do Freemium",
                "Metas ilimitadas",
                "Análises avançadas e sugestões",
                "Relatórios detalhados",
                "Categorização automática",
                "Alertas personalizados",
                "Exportação PDF/CSV",
                "Integração básica com bancos",
                "Suporte prioritário (email + chat)"
            ],
            "popular": True,
            "cta": "Assinar Pro"
        },
        {
            "name": "Premium",
            "price": "R$ 39,90/mês",
            "description": "Máximo controle + Acesso Familiar",
            "features": [
                "Tudo do Pro",
                "Até 5 usuários (Família Smart)",
                "Planejamento financeiro avançado",
                "Previsões e simulações",
                "Integração completa com bancos",
                "Consultoria financeira mensal",
                "API para integrações",
                "Permissões configuráveis",
                "Suporte telefônico"
            ],
            "popular": False,
            "cta": "Escolher Premium"
        }
    ]

    return render(request, 'financas/index.html', {"plans": planos})

def educacao(request):
    # Simulação de usuário
    user = {
        "username": "Sara",
        "plan": "freemium"  # ou "pro" / "premium"
    }
    
    is_pro = user['plan'] in ['pro', 'premium']

    basic_content = [
        {
            "title": "Como Controlar os Gastos",
            "description": "Aprenda técnicas práticas para não gastar mais do que ganha",
            "content": [
                "🎯 Regra 50-30-20: 50% necessidades, 30% desejos, 20% poupança",
                "📱 Use apps para acompanhar gastos diários",
                "🛒 Faça lista de compras e evite compras por impulso",
                "⏰ Espere 24h antes de compras não essenciais",
                "💳 Prefira débito ao crédito quando possível"
            ],
            "icon": "piggy-bank",
            "color": "blue"
        },
        {
            "title": "Criando uma Reserva de Emergência",
            "description": "Por que e como construir sua segurança financeira",
            "content": [
                "🎯 Meta: 6 meses de gastos essenciais guardados",
                "🏦 Mantenha em conta poupança ou CDB com liquidez",
                "📈 Comece com R$ 50-100 por mês",
                "🚨 Use apenas para emergências reais",
                "⚡ Reponha sempre que usar"
            ],
            "icon": "target",
            "color": "green"
        },
        {
            "title": "Planejamento Financeiro Básico",
            "description": "Primeiros passos para organizar sua vida financeira",
            "content": [
                "📊 Anote todas as receitas e despesas",
                "🎯 Defina metas financeiras claras",
                "📅 Revise seu orçamento mensalmente",
                "💰 Quite dívidas mais caras primeiro",
                "📚 Invista em educação financeira"
            ],
            "icon": "bar-chart",
            "color": "purple"
        },
        {
            "title": "Introdução aos Investimentos",
            "description": "Conceitos básicos para começar a investir",
            "content": [
                "🏦 Comece com Tesouro Direto (renda fixa)",
                "📈 Diversifique seus investimentos",
                "⏰ Invista pensando no longo prazo",
                "📚 Estude antes de investir",
                "💸 Nunca invista dinheiro que você precisa"
            ],
            "icon": "trending-up",
            "color": "orange"
        }
    ]

    pro_content = [
        {
            "title": "Análise Avançada de Mercado",
            "description": "Entenda indicadores econômicos e como afetam seus investimentos",
            "topics": ["Taxa Selic e seus impactos", "Inflação e poder de compra", "Índices de bolsa", "Análise fundamentalista"],
            "icon": "bar-chart"
        },
        {
            "title": "Estratégias de Investimento",
            "description": "Técnicas avançadas para maximizar seus rendimentos",
            "topics": ["Diversificação de carteira", "Rebalanceamento", "Dollar Cost Averaging", "Análise de risco"],
            "icon": "trending-up"
        },
        {
            "title": "Planejamento Tributário",
            "description": "Como otimizar seus impostos legalmente",
            "topics": ["Imposto de Renda em investimentos", "Regime de tributação", "Dedução de IR", "Previdência privada"],
            "icon": "calculator"
        },
        {
            "title": "Consultoria Personalizada",
            "description": "Análises específicas para seu perfil financeiro",
            "topics": ["Relatórios detalhados", "Recomendações personalizadas", "Simulações de cenários", "Acompanhamento mensal"],
            "icon": "file-text"
        }
    ]

    context = {
        "user": user,
        "is_pro": is_pro,
        "basic_content": basic_content,
        "pro_content": pro_content,
    }

    return render(request, "financas/educacao.html", context)

